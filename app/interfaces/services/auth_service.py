from typing import List, Annotated

import httpx
from fastapi import Depends, HTTPException, Security
from fastapi.security import SecurityScopes, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import ValidationError
from starlette import status

from app.interfaces.http.schemas.schemas import TokenData, Tokens, RefreshToken, RegisterRequestForm, AccessToken
from app.core.config import settings

from jwt.exceptions import PyJWTError
import jwt

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/login",
    scopes=settings.get_parsed_scopes
)


class AuthService:
    @staticmethod
    async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Tokens:
        """
        SERVICE: Authenticate a user and return access and refresh tokens.

        Args:
            form_data (LoginRequestForm): The user's login credentials.

        Returns:
            Tokens: A JSON object containing access and refresh tokens.

        Raises:
            HTTPException: If there is an error while trying to validate credentials.
        """

        # 'username' field can be used for either email or phone_number provided. It needs to be checked before
        # sending to a different microservice.
        credentials = {
            'username': form_data.username,
            'password': form_data.password,
            'scopes': form_data.scopes,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{settings.AUTH_SERVICE_URL}/api/v1/auth/login", json=credentials)
                return response.json()
            except HTTPException:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

    @staticmethod
    async def refresh(refresh_token: RefreshToken = Depends(oauth2_scheme)) -> Tokens:
        """
        SERVICE: Refresh a user's access and refresh tokens.

        Args:
            refresh_token (RefreshToken): The user's current refresh token.

        Returns:
            Tokens: A JSON object containing access and refresh tokens.

        Raises:
            HTTPException: If there is an error while trying to validate the refresh token.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{settings.AUTH_SERVICE_URL}/api/v1/auth/refresh",
                                             json=refresh_token.model_dump_json())
                return response.json()
            except HTTPException:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

    @staticmethod
    async def register(data: RegisterRequestForm):
        """
        SERVICE: Register a user, create a record in the DB.

        Args:
            data (RegisterRequestForm): The user's data to register.

        Returns:
            HTTPResponse: A JSON object containing success, error message and status code.

        Raises:
            HTTPException: If there is an error while trying to validate the data or register/create a new record in the DB.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{settings.AUTH_SERVICE_URL}/api/v1/auth/register",
                                             json=data.model_dump_json())
                return response.json()
            except HTTPException as exception:
                raise HTTPException(status_code=exception.status_code, detail=exception.detail)

    @staticmethod
    async def get_current_user(security_scopes: SecurityScopes,
                               access_token: AccessToken = Depends(oauth2_scheme)) -> TokenData:
        """
        SERVICE: Receive a user's data from the provided access token. It decodes a JWT access token and analyzing security scopes with scopes in the token.

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
