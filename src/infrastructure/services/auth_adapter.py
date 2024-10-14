import httpx
from fastapi import Depends, HTTPException
from jwt import PyJWTError
from pydantic import ValidationError
from starlette import status

from src.core.oauth_schemas import oauth2_refresh_token_scheme
from src.domain.schemas import Tokens, RefreshToken, RegisterRequestForm, LoginRequestForm
from src.core.config import settings


class AuthAdapter:
    @staticmethod
    async def login(data: LoginRequestForm) -> Tokens:
        """
        ADAPTER METHOD: Log in a user with provided credentials. Passes the query to the 'AuthService' microservice.

        Args:
            data (LoginRequestForm): A form data provided for login, containing either email or phone number, and password.

        Returns:
            Tokens: A JSON object containing access, refresh tokens and token type.

        Raises:
            ValueError: If email or phone number, or password is invalid.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{settings.AUTH_SERVICE_URL}/api/v1/auth/login", json=data.model_dump())
                response.raise_for_status()
                response_data = response.json()
                return Tokens(**response_data)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise ValueError("Invalid credentials.")
                raise ValueError(f"Unexpected error during login: {str(e)}")
            except httpx.RequestError:
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Auth service is unavailable.")
            except ValidationError:
                raise ValueError("Invalid response format from AuthService.")
            except Exception as e:
                raise ValueError(f"Unhandled error in AuthAdapter: {str(e)}.")

    @staticmethod
    async def refresh(refresh_token: RefreshToken = Depends(oauth2_refresh_token_scheme)) -> Tokens:
        """
        ADAPTER METHOD: Refresh a user's access and refresh tokens.

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
                response.raise_for_status()
                response_data = response.json()
                return Tokens(**response_data)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise ValueError("Invalid refresh token.")
                raise ValueError(f"Unexpected error during token refresh: {str(e)}")
            except httpx.RequestError:
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Auth service is unavailable.")
            except ValidationError:
                raise ValueError("Invalid response format from AuthService.")
            except Exception as e:
                raise ValueError(f"Unhandled error in AuthAdapter: {str(e)}.")

    @staticmethod
    async def register(data: RegisterRequestForm):
        """
        ADAPTER METHOD: Register a user, create a record in the DB.

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
                response.raise_for_status()

                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    raise ValueError("Invalid data provided.")
                elif e.response.status_code == 409:
                    raise ValueError("User already exists.")
                else:
                    raise ValueError(f"Unexpected error during registration: {e.response.text}")
            except httpx.RequestError:
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                    detail="Auth service is unavailable.")
            except ValidationError:
                raise ValueError("Invalid response format from AuthService.")
            except Exception as e:
                raise ValueError(f"Unhandled error in AuthAdapter: {str(e)}.")
