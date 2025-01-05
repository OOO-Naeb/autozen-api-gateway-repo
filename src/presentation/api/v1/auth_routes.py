from typing import Annotated

from fastapi import APIRouter, Depends, Body
from starlette import status
from starlette.responses import JSONResponse

from src.application.services.auth_service import AuthService
from src.domain.oauth_schemas import oauth2_token_schema
from src.domain.schemas import Tokens, RefreshToken, LoginRequestForm, RegisterRequestForm, AccessToken

auth_router = APIRouter(
    tags=["Auth"],
    prefix="/api/v1/auth",
)

@auth_router.post('/login', response_model=Tokens)
async def login(
    form_data: Annotated[LoginRequestForm, Body(...)],
    auth_service: Annotated[AuthService, Depends()],
) -> JSONResponse:
    """
    CONTROLLER: Log in a user with provided credentials. Passes the query to the 'AuthUseCase'.

    Args:
        form_data (LoginRequestForm): The login credentials provided by the client.
        auth_service (AuthService): The authentication use-case.

    Returns:
        JSONResponse: A JSON object containing access, refresh tokens and token type.
    """
    tokens = await auth_service.login(form_data)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'success': True,
            'message': 'Logged in successfully.',
            'access_token': tokens.access_token,
            'refresh_token': tokens.refresh_token,
            'token_type': 'Bearer',
        },
    )


@auth_router.post("/refresh", response_model=Tokens)
async def refresh(refresh_token: Annotated[RefreshToken, Depends(oauth2_token_schema)], auth_service: Annotated[AuthService, Depends()]) -> JSONResponse:
    """
    CONTROLLER: Return a new pair of access and refresh tokens. Passes the query to the 'AuthUseCase'.

    Args:
        refresh_token (RefreshToken): The refresh token to get both new access and refresh tokens.
        auth_service (AuthService): The authentication use-case.

    Returns:
        JSONResponse: A JSON object containing access, refresh tokens and token type.
    """
    tokens = await auth_service.refresh(str(refresh_token))

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'success': True,
            'message': 'Tokens have been refreshed successfully.',
            'access_token': tokens.access_token,
            'refresh_token': tokens.refresh_token,
            'token_type': 'Bearer',
        },
    )


@auth_router.post('/register')
async def register(data: Annotated[RegisterRequestForm, Body(...)], auth_service: Annotated[AuthService, Depends()]) -> JSONResponse:
    """
    CONTROLLER: Register new user with provided data. Passes the query to the 'AuthUseCase'.

    Args:
        data (RegisterRequestForm): The data to register.
        auth_service (AuthService): The authentication use-case.

    Returns:
        JSONResponse: A JSON object containing success, error message and status code.
    """
    user_data = await auth_service.register(data)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "success": True,
            "message": "User registered successfully.",
            "user": user_data.model_dump(),
        }
    )


@auth_router.post('/test_token')
async def test_token(access_token: Annotated[AccessToken, Depends(oauth2_token_schema)], auth_service: Annotated[AuthService, Depends()]):
    tokens = await auth_service.test_token(str(access_token))

    return tokens
