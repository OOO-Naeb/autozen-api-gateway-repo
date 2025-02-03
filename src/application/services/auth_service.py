from http import HTTPStatus
from http.client import HTTPResponse
from typing import Annotated

from fastapi import Depends

from src.core.jwt_validator import JWTValidator
from src.domain.schemas import Tokens, RefreshToken, LoginRequestForm, RegisterRequestForm, UserFromDB
from src.infrastructure.adapters.rabbitmq_auth_adapter import RabbitMQAuthAdapter
from src.infrastructure.interfaces.auth_adapter_interface import IAuthAdapter


class AuthService:
    """
    SERVICE: Authentication service class. Contains methods for user login, registration and token refresh. It's being used instead of the use cases in order to avoid unnecessary decomposition.
    """
    def __init__(self, auth_adapter: Annotated[IAuthAdapter, Depends(RabbitMQAuthAdapter)], jwt_validator: Annotated[JWTValidator, Depends()]) -> None:
        self.auth_adapter = auth_adapter
        self.jwt_validator = jwt_validator

    async def login(self, data: LoginRequestForm) -> Tokens:
        """
        SERVICE METHOD: Log in a user with provided credentials. Passes the query to the 'AuthAdapter'.

        Args:
            data (LoginRequestForm): A form data provided for login, containing either email or phone number, and password.

        Returns:
            Tokens: A JSON object containing access, refresh tokens and token type.
        """
        return await self.auth_adapter.login(data)

    async def refresh(self, refresh_token: str) -> Tokens:
        """
        SERVICE METHOD: Return a new pair of access and refresh tokens. Passes the query through to the 'AuthAdapter'.

        Args:
            refresh_token (RefreshToken): A JSON object containing refresh token in the 'Authorization' header.

        Returns:
            Tokens: A JSON object containing access, refresh tokens and token type.
        """
        refresh_token_payload = await self.jwt_validator.validate_jwt_token(refresh_token, required_token_type='refresh')
        print("Token was validated in AuthService.")

        return await self.auth_adapter.refresh(refresh_token_payload)

    async def register(self, data: RegisterRequestForm) -> UserFromDB:
        """
        SERVICE METHOD: Register new user with provided data. Passes the query through to the 'AuthAdapter'.

        Args:
            data (RegisterRequestForm): The data to register.

        Returns:
            HTTPResponse: A JSON object containing success, error message and status code.
        """
        return await self.auth_adapter.register(data)

    async def test_token(self, access_token: str):
        access_token_payload = await self.jwt_validator.validate_jwt_token(access_token, required_token_type='access')
        print("Token was validated in AuthUseCase.")

        return HTTPStatus.OK, access_token_payload