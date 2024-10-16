from http.client import HTTPResponse
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Body
from starlette import status

from src.application.use_cases.auth_use_case import AuthUseCase
from src.core.oauth_schemas import oauth2_token_schema
from src.domain.schemas import Tokens, RefreshToken, LoginRequestForm, RegisterRequestForm

auth_router = APIRouter(
    tags=["Auth"],
    prefix="/api/v1/auth",
)

@auth_router.post('/login', response_model=Tokens)
async def login(form_data: Annotated[LoginRequestForm, Body(...)], auth_use_case: Annotated[AuthUseCase, Depends()]) -> Tokens:
    """
    CONTROLLER: Log in a user with provided credentials. Passes the query to the 'AuthUseCase'.

    Args:
        form_data (LoginRequestForm): The login credentials provided by the client.
        auth_use_case (AuthUseCase): The authentication use-case.

    Returns:
        Tokens: A JSON object containing access, refresh tokens and token type.

    Raises:
        HTTPException: If provided email or phone number, or password is invalid (status code 401).
        HTTPException: If the login service is unavailable (status code 503).
        HTTPException: If an unexpected error occurs on the server (status code 500).
    """
    try:
        tokens = await auth_use_case.login(form_data)
        return tokens
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Currently, login service is not available. Try again later.')
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")


@auth_router.post("/refresh", response_model=Tokens)
async def refresh(refresh_token: Annotated[RefreshToken, Depends(oauth2_token_schema)], auth_use_case: Annotated[AuthUseCase, Depends()]) -> Tokens:
    """
    CONTROLLER: Return a new pair of access and refresh tokens. Passes the query to the 'AuthUseCase'.

    Args:
        refresh_token (RefreshToken): The refresh token to get both new access and refresh tokens.
        auth_use_case (AuthUseCase): The authentication use-case.

    Returns:
        Tokens: A JSON object containing access, refresh tokens and token type.

    Raises:
        HTTPException: If provided refresh token is invalid (status code 401).
        HTTPException: If the refresh service is unavailable (status code 503).
        HTTPException: If an unexpected error occurs on the server (status code 500).
    """
    try:
        tokens = await auth_use_case.refresh(refresh_token)
        return tokens
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail='Currently, tokens refresh service is not available. Try again later.')
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred during token refresh.")

@auth_router.post('/register')
async def register(data: Annotated[RegisterRequestForm, Body(...)], auth_use_case: Annotated[AuthUseCase, Depends()]):
    """
    CONTROLLER: Register new user with provided data. Passes the query to the 'AuthUseCase'.


    Args:
        data (RegisterRequestForm): The data to register.
        auth_use_case (AuthUseCase): The authentication use-case.

    Returns:
        HTTPResponse: A JSON object containing success, error message and status code.

    Raises:
        HTTPException: If there's a record in DB with the same data (status code 409).
        HTTPException: If provided data doesn't match the requirements (status code 400).
        HTTPException: If the register service is unavailable (status code 503).
        HTTPException: If an unexpected error occurs on the server (status code 500).
    """
    try:
        result = await auth_use_case.register(data)
        return result
    except ValueError as e:
        if "User already exists" in str(e):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Duplicate record. This email or phone number is already taken.')
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Currently, register service is not available. Try again later.')
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

