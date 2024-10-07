from http.client import HTTPResponse
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.interfaces.http.schemas.schemas import Tokens, RefreshToken, RegisterRequestForm
from app.interfaces.services.auth_service import AuthService

auth_router = APIRouter(
    tags=["Auth"],
    prefix="/api/v1/auth",
)

@auth_router.post('/login', response_model=Tokens)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Tokens:
    """
    ENDPOINT: Log in a user with provided credentials.

    Args:
        form_data (LoginRequestForm): The login credentials provided by the client.

    Returns:
        Tokens: A JSON object containing access, refresh tokens and token type.

    Raises:
        HTTPException: If the credentials are invalid or not found.
    """
    tokens = await AuthService.login(form_data)
    if not tokens:
        raise HTTPException(status_code=401, detail='Invalid credentials')

    return tokens

@auth_router.post("/refresh", response_model=Tokens)
async def refresh(refresh_token: RefreshToken) -> Tokens:
    """
    ENDPOINT: Return a new pair of access and refresh tokens.

    Args:
        refresh_token (RefreshToken): The refresh token to get both new access and refresh tokens.

    Returns:
        Tokens: A JSON object containing access, refresh tokens and token type.

    Raises:
        HTTPException: If provided refresh token is invalid or damaged.
    """
    new_tokens = await AuthService.refresh(refresh_token)
    if not new_tokens:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    return new_tokens

@auth_router.post('/register')
async def register(data: RegisterRequestForm):
    """
    ENDPOINT: Register new user with provided data.


    Args:
        data (RegisterRequestForm): The data to register.

    Returns:
        HTTPResponse: A JSON object containing success, error message and status code.

    Raises:
        HTTPException: If provided data doesn't match the requirements (RegisterRequestForm) or in case of server error.
    """
    response = await AuthService.register(data)
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()
