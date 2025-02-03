import asyncio
import json
import logging
import os
import uuid

import aio_pika

from src.core.config import settings
from src.domain.exceptions import SourceUnavailableException, SourceTimeoutException
from src.domain.schemas import CardInfo, PaymentTokenResponse
from src.infrastructure.interfaces.payment_adapter_interface import IPaymentAdapter


class RabbitMQPaymentAdapter(IPaymentAdapter):
    def __init__(self):
        # Logging setup --------------------------------------------------------------------------------------------- #
        self.logger = logging.getLogger(__name__)

        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_format = '%(levelname)s:    %(asctime)s - %(name)s: %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

        file_handler = logging.FileHandler(os.path.join(log_dir, 'payment_log.log'))
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        # ----------------------------------------------------------------------------------------------------------- #

        self.connection = None
        self.channel = None
        self.exchange = None
        self.exchange_name = 'GATEWAY-PAYMENT-EXCHANGE.direct'

    async def connect(self):
        """
        ADAPTER METHOD: Establish a connection to the RabbitMQ service.

        Raises:
            SourceUnavailableException: When RabbitMQ service is not available.
        """
        if not self.connection or self.connection.is_closed:
            try:
                self.connection = await aio_pika.connect_robust(
                    url=settings.rabbitmq_url,
                    timeout=10,
                    client_properties={'client_name': 'API Gateway Service'}
                )
                self.channel = await self.connection.channel()
                self.exchange = await self.channel.declare_exchange(
                    name=self.exchange_name,
                    type=aio_pika.ExchangeType.DIRECT,
                    durable=True
                )
            except aio_pika.exceptions.AMQPError as e:
                self.logger.error(
                    f"RabbitMQ service is unavailable. Connection error: {e}. From: RabbitMQPaymentAdapter, connect()."
                )
                raise SourceUnavailableException('RabbitMQ service is not available.')

    async def rpc_call(self, operation_type: str, routing_key: str, body: dict, timeout: int = 5) -> tuple[int, dict] | None:
        """
        ADAPTER METHOD: Send an RPC call through RabbitMQ and wait for the response.

        Args:
            operation_type (str): The operation type to include in the message body
            routing_key (str): The routing key to use when sending the message.
            body (dict): The message body to send.
            timeout (int): The time to wait for a response before giving up.

        Returns:
            tuple[int, dict] | None: The status code and response body, or None if no response was received.
        """
        await self.connect()

        callback_queue = await self.channel.declare_queue(name=f'FROM-PAYMENT-TO-GATEWAY-RESPONSE-QUEUE-{uuid.uuid4()}',
                                                          exclusive=True, auto_delete=True)
        correlation_id = str(uuid.uuid4())
        body['operation_type'] = operation_type  # Add metadata to the body -> which method in the Payment Service is supposed to be called.

        # Dev logs
        print("Generated correlation ID from sender ->", correlation_id)

        rabbitmq_response_future = asyncio.get_event_loop().create_future()

        async def on_response(response_message: aio_pika.IncomingMessage):
            if response_message.correlation_id == correlation_id:
                rabbitmq_response_future.set_result(response_message)
                await response_message.ack()

        consumer_tag = await callback_queue.consume(on_response)

        await self.exchange.publish(
            aio_pika.Message(
                body=json.dumps(body).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                correlation_id=correlation_id,
                reply_to=callback_queue.name
            ),
            routing_key=routing_key
        )

        try:
            message = await asyncio.wait_for(rabbitmq_response_future, timeout)

            response = json.loads(message.body.decode())
            status_code = response.get("status_code")
            response_body = response.get("body")

            return status_code, response_body

        except asyncio.TimeoutError:
            self.logger.error(
                "Payment Service is unavailable. No response. From: RabbitMQPaymentAdapter, rpc_call()."
            )

            raise SourceTimeoutException()

        finally:
            await callback_queue.cancel(consumer_tag)
            if not self.channel.is_closed:
                await self.channel.close()

    async def add_payment_method(self, card_info: CardInfo) -> PaymentTokenResponse | None:
        """
        ADAPTER METHOD: Get a payment token from the Payment Service.

        Args:
            card_info (CardInfo): The card information to use.

        Returns:
            PaymentTokenResponse | None: An object containing status code and payment token, or None if no response was received.
        """
        card_info = card_info.__dict__
        status_code, payment_token = await self.rpc_call('add_new_payment_method', 'PAYMENT.all', card_info)

        return PaymentTokenResponse(status_code=status_code, payment_token=payment_token)
