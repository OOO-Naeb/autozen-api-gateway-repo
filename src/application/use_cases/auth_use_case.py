from http.client import HTTPResponse
from typing import Annotated

from fastapi import Depends

from src.core.oauth_schemas import oauth2_token_schema
from src.domain.schemas import Tokens, RefreshToken, LoginRequestForm, RegisterRequestForm
from src.infrastructure.adapters.rabbitmq_auth_adapter import RabbitMQAuthAdapter
from src.infrastructure.interfaces.adapter_interface import IAuthAdapter


class AuthUseCase:
    def __init__(self, auth_adapter: Annotated[IAuthAdapter, Depends(RabbitMQAuthAdapter)]) -> None:
        self.auth_adapter = auth_adapter

    async def login(self, data: LoginRequestForm) -> Tokens:
        """
        USE CASE METHOD: Log in a user with provided credentials. Passes the query to the 'AuthAdapter'.

        Args:
            data (LoginRequestForm): A form data provided for login, containing either email or phone number, and password.

        Returns:
            Tokens: A JSON object containing access, refresh tokens and token type.
        """
        return await self.auth_adapter.login(data)

    async def refresh(self, refresh_token: Annotated[RefreshToken, Depends(oauth2_token_schema)]) -> Tokens:
        """
        USE CASE METHOD: Return a new pair of access and refresh tokens. Passes the query through to the 'AuthAdapter'.

        Args:
            refresh_token (RefreshToken): A JSON object containing refresh token in the 'Authorization' header.

        Returns:
            Tokens: A JSON object containing access, refresh tokens and token type.
        """
        return await self.auth_adapter.refresh(refresh_token)

    async def register(self, data: RegisterRequestForm):
        """
        USE CASE METHOD: Register new user with provided data. Passes the query through to the 'AuthAdapter'.

        Args:
            data (RegisterRequestForm): The data to register.

        Returns:
            HTTPResponse: A JSON object containing success, error message and status code.
        """
        return await self.auth_adapter.register(data)
