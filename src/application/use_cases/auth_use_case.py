import re
from http.client import HTTPResponse
from re import Match
from typing import List, Annotated

import jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import SecurityScopes
from jwt import PyJWTError
from pydantic import ValidationError
from starlette import status

from src.core.config import settings
from src.core.oauth_schemas import oauth2_access_token_scheme, oauth2_refresh_token_scheme
from src.infrastructure.services.auth_adapter import AuthAdapter
from src.domain.schemas import Tokens, TokenData, AccessToken, RefreshToken, LoginRequestForm, RegisterRequestForm


class AuthUseCase:
    def __init__(self, auth_adapter: Annotated[AuthAdapter, Depends()]) -> None:
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

    async def refresh(self, refresh_token: Annotated[RefreshToken, Depends(oauth2_refresh_token_scheme)]) -> Tokens:
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

    @staticmethod
    async def get_current_user(security_scopes: SecurityScopes,
                               access_token: AccessToken = Depends(oauth2_access_token_scheme)) -> TokenData:
        """
        Receive a user's data from the provided access token. It decodes a JWT access token and analyzing security scopes with scopes in the token.

        Args:
            security_scopes (SecurityScopes): The security scopes that the user tries to get access to.
            access_token (AccessToken): Provided access token to validate.

        Returns:
            TokenData: A JSON object containing email, list of roles (List[str]).
        """
        try:
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            roles: List[str] = payload.get("roles", [])

            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            token_data = TokenData(email=email, roles=roles)
        except (PyJWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        for scope in security_scopes.scopes:
            if scope not in token_data.roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not allowed",
                )

        return token_data

    @staticmethod
    async def get_current_active_user(current_user: TokenData = Security(get_current_user, scopes=[])):
        return current_user
