import json
import logging
import uuid
import time

import pika
from pika import exceptions
from starlette.responses import JSONResponse

from src.domain.exceptions import SourceTimeoutException, SourceUnavailableException, NotFoundException, \
    ConflictException, UnauthorizedException, UnhandledException
from src.domain.schemas import Tokens, RefreshToken, RegisterRequestForm, LoginRequestForm
from src.infrastructure.interfaces.adapter_interface import IAuthAdapter


class RabbitMQAuthAdapter(IAuthAdapter):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.connection = None
        self.channel = None
        self.exchange_name = 'AUTH.direct'

    async def connect(self):
        """
        Establishes a connection to the RabbitMQ service.

        Raises:
            SourceUnavailableException: When RabbitMQ service is not available.
        """
        if self.connection is None or self.channel is None:
            try:
                self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
                self.channel = self.connection.channel()
                self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='direct', durable=True)
            except pika.exceptions.AMQPConnectionError:
                self.logger.error(f"RabbitMQ service is unavailable. Connection error. From: RabbitMQAuthAdapter, connect().")
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

        queue_for_responses = self.channel.queue_declare(queue='', exclusive=True)
        callback_queue = queue_for_responses.method.queue

        corr_id = str(uuid.uuid4())

        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=routing_key,
            body=json.dumps(body),
            properties=pika.BasicProperties(
                reply_to=callback_queue,
                correlation_id=corr_id,
                delivery_mode=2,
            )
        )

        response = None
        status_code = None
        response_body = None
        response_start_time = time.time()

        def on_response(ch, method, props, body):
            nonlocal response, status_code, response_body
            if props.correlation_id == corr_id:
                response = json.loads(body.decode('utf-8'))
                status_code = response.get("status_code", 500)
                response_body = response.get("body", {})

        self.channel.basic_consume(
            queue=callback_queue,
            on_message_callback=on_response,
            auto_ack=True
        )

        while response is None:
            self.connection.process_data_events()
            if time.time() > response_start_time + timeout:
                self.logger.error(f"Timeout while waiting for response from 'AuthService' microservice. From: RabbitMQAuthAdapter, rpc_call().")
                raise SourceTimeoutException(detail="Timeout waiting for response from 'AuthService' microservice.")

        return status_code, response_body

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

    async def register(self, data: RegisterRequestForm) -> JSONResponse:
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

        return JSONResponse(status_code=status_code, content=response_body)

