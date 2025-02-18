import asyncio
import json
import uuid

import aio_pika
from aio_pika import DeliveryMode, Message

from src.core.config import settings
from src.core.exceptions import ApiGatewayError
from src.core.logger import LoggerService
from src.domain.models.auth_requests import LoginRequestDTO, RegisterRequestDTO, RefreshTokenRequestDTO
from src.domain.models.auth_responses import LoginResponseDTO, RefreshTokenResponseDTO, RegisterResponseDTO
from src.domain.schemas import RabbitMQResponse
from src.domain.interfaces.auth_adapter_interface import IAuthAdapter
from src.infrastructure.exceptions import RabbitMQError, AuthServiceError


class RabbitMQAuthAdapter(IAuthAdapter):
    def __init__(
            self,
            logger: LoggerService
    ):
        self._logger = logger

        self._connection = None
        self._channel = None
        self._exchange = None
        self._exchange_name = 'API-GATEWAY-to-AUTH-SERVICE-exchange.direct'
        self._queue_name = 'AUTH.all'

    async def connect(self):
        """
        Establishes a connection to the RabbitMQ service.

        Raises:
            RabbitMQError: When RabbitMQ service is not available.
        """
        if not self._connection or self._connection.is_closed:
            try:
                self._connection = await aio_pika.connect_robust(
                    url=settings.rabbitmq_url,
                    timeout=10,
                    client_properties={'client_name': 'API Gateway'}
                )
                self._channel = await self._connection.channel()
                self._exchange = await self._channel.declare_exchange(
                    name=self._exchange_name,
                    type=aio_pika.ExchangeType.DIRECT,
                    durable=True
                )
            except aio_pika.exceptions.AMQPConnectionError as e:
                self._logger.critical(f"RabbitMQ service is unavailable. Connection error: {e}. From: RabbitMQAuthAdapter, connect().")
                raise RabbitMQError(detail="RabbitMQ service is unavailable.")

        if not self._channel or self._channel.is_closed:
            self._channel = await self._connection.channel()
            self._exchange = await self._channel.declare_exchange(
                self._exchange_name,
                aio_pika.ExchangeType.DIRECT,
                durable=True
            )

    async def _make_rpc_call(
            self,
            operation_type: str,
            payload: dict,
            timeout: int = 5
    ) -> RabbitMQResponse | None:
        """
        Sends an RPC call through RabbitMQ to the User Service and waits for the response.

        Args:
            operation_type (str): The operation type to include in the message body.
            payload (Dict[str, Any]): The message payload to send.
            timeout (int): The time to wait for a response before giving up.

        Returns:
            RabbitMQResponse containing the Auth Service response.
        """
        await self.connect()

        message_body = {
            'operation_type': operation_type,
            **payload
        }

        callback_queue = await self._channel.declare_queue(
            name=f'from-AUTH-SERVICE-to-API-GATEWAY.response-{uuid.uuid4()}',
            exclusive=True,
            auto_delete=True
        )

        future = asyncio.get_event_loop().create_future()
        correlation_id = str(uuid.uuid4())

        async def on_response(received_message: aio_pika.IncomingMessage):
            if received_message.correlation_id == correlation_id:
                future.set_result(received_message)
                await received_message.ack()

        consumer_tag = await callback_queue.consume(on_response)

        try:
            # Send message
            await self._exchange.publish(
                Message(
                    body=json.dumps(message_body).encode(),
                    delivery_mode=DeliveryMode.PERSISTENT,
                    correlation_id=correlation_id,
                    reply_to=callback_queue.name,
                ),
                routing_key=self._queue_name
            )

            # Wait for response
            message = await asyncio.wait_for(future, timeout)
            auth_service_response = json.loads(message.body.decode())
            print("Auth Service Response:", auth_service_response)

            return RabbitMQResponse(
                status_code=auth_service_response.get('status_code'),
                body=auth_service_response.get('body'),
                success=auth_service_response.get('success'),
                error_message=auth_service_response.get('error_message'),
                error_origin=auth_service_response.get('error_origin')
            )

        except asyncio.TimeoutError as e:
            self._logger.critical(
                f"Auth Service is not responding. From: RabbitMQAuthAdapter, _make_rpc_call(): {str(e)}")
            raise AuthServiceError(
                status_code=504,
                detail='asyncio.TimeoutError: Auth Service is not responding.'
            )
        except aio_pika.exceptions.AMQPException as e:
            error_message = "RabbitMQ communication error."
            self._logger.critical(f"{error_message} From: RabbitMQAuthAdapter, _make_rpc_call(): {str(e)}")
            raise RabbitMQError(
                status_code=503,
                detail=error_message
            )
        except Exception as e:
            error_message = "Unhandled error occurred while processing a message."
            self._logger.critical(f"{error_message} From: RabbitMQAuthAdapter, _make_rpc_call(): {str(e)}")
            raise ApiGatewayError(
                status_code=500,
                detail=error_message
            )
        finally:
            await callback_queue.cancel(consumer_tag)

    async def login(self, login_data: LoginRequestDTO) -> LoginResponseDTO:
        """
        ADAPTER METHOD: Log in a user by sending the request to Auth Service through RabbitMQ with RPC.

        Args:
            login_data (LoginRequestDTO): A login domain schema, containing either email or phone number,
            and password.

        Returns:
            LoginResponseDTO: Auth Service's response domain schema, containing both access
            and refresh tokens.
        """
        response = await self._make_rpc_call(
            operation_type='login',
            payload=login_data.to_dict()
        )

        if not response.success:
            self._handle_error_response(response)

        access_token = response.body.get('access_token')
        refresh_token = response.body.get('refresh_token')

        return LoginResponseDTO(access_token=access_token, refresh_token=refresh_token)

    async def refresh(self, refresh_token_payload: RefreshTokenRequestDTO) -> RefreshTokenResponseDTO:
        """
        ADAPTER METHOD: Refresh a user's tokens by sending the request to Auth Service through RabbitMQ with RPC.

        Args:
            refresh_token_payload (RefreshTokenRequestDTO): The user's refresh token payload based on domain schema.

        Returns:
            RefreshTokenResponseDTO: A domain schema containing access and refresh tokens.
        """
        response = await self._make_rpc_call(
            operation_type='refresh',
            payload=refresh_token_payload.to_dict()
        )

        if not response.success:
            self._handle_error_response(response)

        return RefreshTokenResponseDTO(**response.body)

    async def register(self, data: RegisterRequestDTO) -> RegisterResponseDTO:
        """
        ADAPTER METHOD: Register a user by sending the request to Auth Service through RabbitMQ with RPC.

        Args:
            data (RegisterRequestDTO): The user's data to register based on domain schema.

        Returns:
            RegisterResponseDTO: A domain schema containing created user's data.
        """
        response = await self._make_rpc_call(
            operation_type='register',
            payload=data.to_dict()
        )

        if not response.success:
            self._handle_error_response(response)

        print("Response:", response)

        return RegisterResponseDTO(**response.body)

    def _handle_error_response(self, response: RabbitMQResponse):
        """
        Handles error responses from the Payment Service.

        Args:
            response (RabbitMQResponse): The response to handle.

        Raises:
            AuthServiceError: When the response status code is 400, 401, 403, 404 or 500.
            ApiGatewayError: When the response status code is not handled.
        """
        if response.status_code in (400, 401, 403, 404):
            self._logger.error(
                f"Auth Service error occurred. From: RabbitMQAuthAdapter, _handle_error_response(): {response.status_code} | {response.error_message}")
            raise AuthServiceError(
                status_code=response.status_code,
                detail=response.error_message
            )
        elif response.status_code == 500:
            self._logger.critical(
                f"Auth Service error occurred. From: RabbitMQAuthAdapter, _handle_error_response(): {response.error_message}")
            raise AuthServiceError(
                status_code=response.status_code,
                detail='Unhandled error occurred in the Auth Service while processing the message.'
            )
        else:
            self._logger.critical(
                f"API Gateway error occurred. From: RabbitMQAuthAdapter, _handle_error_response(): {response.error_message}")
            raise ApiGatewayError(
                status_code=500,
                detail='Unhandled error occurred while processing the response code.'
            )

