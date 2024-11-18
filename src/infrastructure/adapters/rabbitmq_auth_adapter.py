import asyncio
import json
import logging
import uuid

import aio_pika
from starlette.responses import JSONResponse

from src.core.config import settings
from src.domain.exceptions import SourceTimeoutException, SourceUnavailableException, NotFoundException, \
    ConflictException, UnauthorizedException, UnhandledException
from src.domain.schemas import Tokens, RegisterRequestForm, LoginRequestForm, UserFromDB
from src.infrastructure.interfaces.adapter_interface import IAuthAdapter


class RabbitMQAuthAdapter(IAuthAdapter):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.connection = None
        self.channel = None
        self.exchange = None
        self.exchange_name = 'GATEWAY-AUTH-EXCHANGE.direct'

    async def connect(self):
        """
        Establishes a connection to the RabbitMQ service.

        Raises:
            SourceUnavailableException: When RabbitMQ service is not available.
        """
        if not self.connection or self.connection.is_closed:
            try:
                self.connection = await aio_pika.connect_robust(
                    settings.rabbitmq_url,
                    timeout=10,
                    client_properties={'client_name': 'API Gateway Service'}
                )
                self.channel = await self.connection.channel()
                self.exchange = await self.channel.declare_exchange(
                    self.exchange_name, aio_pika.ExchangeType.DIRECT, durable=True
                )
            except aio_pika.exceptions.AMQPConnectionError:
                self.logger.error(
                    f"RabbitMQ service is unavailable. Connection error. From: RabbitMQAuthAdapter, connect()."
                )
                raise SourceUnavailableException(detail="RabbitMQ service is unavailable.")

    async def rpc_call(self, routing_key: str, body: dict, timeout: int = 5) -> tuple:
        """
        Sends an RPC call through RabbitMQ and waits for the response.

        Args:
            routing_key (str): The routing key for the RabbitMQ queue.
            body (dict): The request body to send.
            timeout (int): Timeout for waiting for the response.

        Returns:
            tuple: status_code (int), response_body (dict)

        Raises:
            SourceTimeoutException: If the response takes too long.
        """
        await self.connect()

        callback_queue = await self.channel.declare_queue(name=f'FOR-GATEWAY-RESPONSE-QUEUE-{uuid.uuid4()}', exclusive=True)
        correlation_id = str(uuid.uuid4())

        # Dev logs
        print("Correlation ID from sender ->", correlation_id)

        rabbitmq_response_future = asyncio.get_event_loop().create_future()

        async def on_response(response_message: aio_pika.IncomingMessage):
            if response_message.correlation_id == correlation_id:
                rabbitmq_response_future.set_result(response_message)

        await callback_queue.consume(on_response)

        await self.exchange.publish(
            aio_pika.Message(
                body=json.dumps(body).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                correlation_id=correlation_id,
                reply_to=callback_queue.name,
            ),
            routing_key=routing_key,
        )

        try:
            message = await asyncio.wait_for(rabbitmq_response_future, timeout)

            response = json.loads(message.body.decode())
            status_code = response.get("status_code", 500)
            response_body = response.get("body", {})

            return status_code, response_body

        except asyncio.TimeoutError:
            self.logger.error(
                f"Timeout while waiting for response from 'AuthService' microservice. From: RabbitMQAuthAdapter, rpc_call()."
            )

            raise SourceTimeoutException(detail="Timeout waiting for response from 'AuthService' microservice.")

    async def login(self, data: LoginRequestForm) -> Tokens:
        """
        ADAPTER METHOD: Log in a user by sending the request to 'AuthService' through RabbitMQ with RPC.

        Args:
            data (LoginRequestForm): A form data provided for login, containing either email or phone number,
            and password.

        Returns:
            Tokens: A JSON object containing access, refresh tokens and token type.

        Raises:
            UnauthorizedException (401): If credentials are invalid.
            NotFoundException (404): If the source was not found.
            SourceTimeoutException (504): When waiting time from 'AuthService' exceeds the timeout.
            UnhandledException (500): If unknown exception occurs.
        """
        status_code, response_body = await self.rpc_call(routing_key='AUTH.login', body=data.model_dump())

        if status_code == 401:
            raise UnauthorizedException(detail="Invalid credentials provided.")
        elif status_code == 404:
            raise NotFoundException(detail="Source was not found.")
        elif status_code >= 400:
            self.logger.error(f"Unknown error in RabbitMQAuthAdapter during LOGIN: {status_code} | {response_body}")
            raise UnhandledException()

        return Tokens(**response_body)

    async def refresh(self, refresh_token_payload: dict) -> Tokens:
        """
        ADAPTER METHOD: Refresh a user's tokens by sending the request to 'AuthService' through RabbitMQ with RPC.

        Args:
            refresh_token_payload (dict): The user's refresh token payload.

        Returns:
            Tokens: A JSON object containing access and refresh tokens.

        Raises:
            UnauthorizedException (401): If the refresh token is invalid.
            NotFoundException (404): If the source was not found.
            SourceTimeoutException (504): When waiting time from 'AuthService' exceeds the timeout.
            UnhandledException (500): If unknown exception occurs.
        """
        print("PAYLOAD TO SEND:", refresh_token_payload)
        status_code, response_body = await self.rpc_call(routing_key='AUTH.refresh', body=refresh_token_payload)

        if status_code == 401:
            raise UnauthorizedException(detail="Invalid refresh token.")
        elif status_code == 404:
            raise NotFoundException(detail="Source was not found.")
        elif status_code >= 400:
            self.logger.error(f"Unknown error in RabbitMQAuthAdapter during REFRESHING TOKEN: {status_code} | {response_body}")
            raise UnhandledException()

        return Tokens(**response_body)

    async def register(self, data: RegisterRequestForm) -> tuple[int, UserFromDB]:
        """
        ADAPTER METHOD: Register a user by sending the request to 'AuthService' through RabbitMQ with RPC.

        Args:
            data (RegisterRequestForm): The user's data to register.

        Returns:
            JSONResponse: Response from AuthService with status code and detail message.

        Raises:
            NotFoundException (404): If user or source was not found.
            ConflictException (409): When given email or phone number is already in the DB.
            SourceTimeoutException (504): When waiting time from the 'AuthService' microservice exceeds the timeout (5s).
            UnhandledException (500): If unknown exception occurs.
        """
        status_code, response_body = await self.rpc_call(routing_key='AUTH.register', body=data.model_dump())

        if status_code == 404:
            raise NotFoundException(detail="User or source not found in AuthService.")
        elif status_code == 409:
            raise ConflictException(detail="User's email is already registered in the DB.")
        elif status_code >= 400:
            self.logger.error(f"Unknown error in RabbitMQAuthAdapter during REGISTERING: {status_code} | {response_body}")
            raise UnhandledException()

        return status_code, UserFromDB(**response_body)

