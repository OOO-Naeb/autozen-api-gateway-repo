import asyncio
import json
import uuid
from typing import Dict, Any

import aio_pika
from aio_pika import Message, DeliveryMode

from src.core.config import settings
from src.core.exceptions import ApiGatewayError
from src.core.logger import LoggerService
from src.domain.models.payment_methods import CardPaymentMethod
from src.domain.models.payment_token import PaymentTokenResponse
from src.domain.schemas import RabbitMQResponse
from src.infrastructure.exceptions import PaymentServiceError, RabbitMQError
from src.domain.interfaces.payment_adapter_interface import IPaymentAdapter


class RabbitMQPaymentAdapter(IPaymentAdapter):
    def __init__(self, logger: LoggerService):
        self._logger = logger

        self._connection = None
        self._channel = None
        self._exchange = None
        self._exchange_name = 'API-GATEWAY-and-PAYMENT-SERVICE-exchange.direct'
        self._queue_name = 'PAYMENT.all'

    async def connect(self):
        """
        Establishes a connection to the RabbitMQ service and reinstates the channel if it's closed.

        Raises:
            RabbitMQError: When RabbitMQ service is not available.
        """
        if not self._connection or self._connection.is_closed:
            try:
                self._connection = await aio_pika.connect_robust(
                    url=settings.rabbitmq_url,
                    timeout=10,
                    client_properties={'client_name': 'API Gateway Service'}
                )
                self._channel = await self._connection.channel()
                self._exchange = await self._channel.declare_exchange(
                    name=self._exchange_name,
                    type=aio_pika.ExchangeType.DIRECT,
                    durable=True
                )
            except aio_pika.exceptions.AMQPError as e:
                self._logger.error(
                    f"RabbitMQ service is unavailable. Connection error: {e}. From: RabbitMQPaymentAdapter, connect()."
                )
                raise RabbitMQError(detail='RabbitMQ service is not available.')

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
            payload: Dict[str, Any],
            timeout: int = 5
    ) -> RabbitMQResponse | None:
        """
        Sends an RPC call through RabbitMQ to the User Service and waits for the response.

        Args:
            operation_type (str): The operation type to include in the message body.
            payload (Dict[str, Any]): The message payload to send.
            timeout (int): The time to wait for a response before giving up.

        Returns:
            RabbitMQResponse containing the Payment Service response.
        """
        await self.connect()

        message_body = {
            'operation_type': operation_type,
            **payload
        }

        callback_queue = await self._channel.declare_queue(
            name=f'from-PAYMENT-SERVICE-to-API-GATEWAY.response-{uuid.uuid4()}',
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
            payment_service_response = json.loads(message.body.decode())

            response = RabbitMQResponse.success_response(
                status_code=payment_service_response.get('status_code', 200),
                body=payment_service_response.get('body', {})
            )

            return response

        except asyncio.TimeoutError as e:
            self._logger.critical(
                f"Payment Service is not responding. From: RabbitMQPaymentAdapter, _make_rpc_call(): {str(e)}")
            raise PaymentServiceError(
                status_code=504,
                detail='asyncio.TimeoutError: Payment Service is not responding.'
            )
        except aio_pika.exceptions.AMQPException as e:
            error_message = "RabbitMQ communication error."
            self._logger.critical(f"{error_message} From: RabbitMQPaymentAdapter, _make_rpc_call(): {str(e)}")
            raise RabbitMQError(
                status_code=503,
                detail=error_message
            )
        except Exception as e:
            error_message = "Unhandled error occurred while processing a message."
            self._logger.critical(f"{error_message} From: RabbitMQPaymentAdapter, _make_rpc_call(): {str(e)}")
            raise ApiGatewayError(
                status_code=500,
                detail=error_message
            )
        finally:
            await callback_queue.cancel(consumer_tag)

    async def add_bank_card(self, card: CardPaymentMethod) -> PaymentTokenResponse:
        """
        Retrieves a payment token from the bank API Gateway by user's ID from the Payment Service.

        Args:
            card (CardPaymentMethod): The card to add.

        Returns:
            PaymentTokenResponse: The payment token domain model response.
        """
        response = await self._make_rpc_call(
            operation_type='add_bank_card',
            payload=card.to_serializable_dict()  # Converts datetime objects to strings. Otherwise, serialization will fail.
        )

        if not response.success:
            self._handle_error_response(response)

        return PaymentTokenResponse(**response.body)

    def _handle_error_response(self, response: RabbitMQResponse):
        """
        Handles error responses from the Payment Service.

        Args:
            response (RabbitMQResponse): The response to handle.

        Raises:
            PaymentServiceError: When the response status code is 400, 401, or 403.
            PaymentServiceError: When the response status code is 500.
            ApiGatewayError: When the response status code is not handled.
        """
        if response.status_code in (400, 401, 403):
            self._logger.error(
                f"Payment Service error occurred. From: RabbitMQPaymentAdapter, _handle_error_response(): {response.status_code} | {response.error_message}")
            raise PaymentServiceError(
                status_code=response.status_code,
                detail=response.error_message
            )
        elif response.status_code == 500:
            self._logger.critical(
                f"Payment Service error occurred. From: RabbitMQPaymentAdapter, _handle_error_response(): {response.error_message}")
            raise PaymentServiceError(
                status_code=500,
                detail='Unhandled error occurred in the Payment Service while processing the message.'
            )
        else:
            self._logger.critical(
                f"API Gateway error occurred. From: RabbitMQPaymentAdapter, _handle_error_response(): {response.error_message}")
            raise ApiGatewayError(
                status_code=500,
                detail='Unhandled error occurred while processing the response code.'
            )

