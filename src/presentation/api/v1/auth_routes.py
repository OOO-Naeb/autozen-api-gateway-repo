from http.client import HTTPResponse
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from jwt import PyJWTError
from starlette import status

from src.application.use_cases.auth_use_case import AuthUseCase
from src.core.oauth_schemas import oauth2_refresh_token_scheme
from src.domain.schemas import Tokens, RefreshToken, LoginRequestForm, RegisterRequestForm

auth_router = APIRouter(
    tags=["Auth"],
    prefix="/api/v1/auth",
)

@auth_router.post('/login', response_model=Tokens)
async def login(form_data: Annotated[LoginRequestForm, Depends()], auth_use_case: Annotated[AuthUseCase, Depends()]) -> Tokens:
    """
    CONTROLLER: Log in a user with provided credentials. Passes the query to the 'AuthUseCase'.

    Args:
        form_data (LoginRequestForm): The login credentials provided by the client.
        auth_use_case (AuthUseCase): The authentication use-case.

    Returns:
        Tokens: A JSON object containing access, refresh tokens and token type.

    Raises:
        HTTPException: If email or phone number, or password is invalid.
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
async def refresh(refresh_token: Annotated[RefreshToken, Depends(oauth2_refresh_token_scheme)], auth_use_case: Annotated[AuthUseCase, Depends()]) -> Tokens:
    """
    CONTROLLER: Return a new pair of access and refresh tokens. Passes the query to the 'AuthUseCase'.

    Args:
        refresh_token (RefreshToken): The refresh token to get both new access and refresh tokens.
        auth_use_case (AuthUseCase): The authentication use-case.

    Returns:
        Tokens: A JSON object containing access, refresh tokens and token type.

    Raises:
        HTTPException: If provided refresh token is invalid or damaged.
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
async def register(data: RegisterRequestForm, auth_use_case: Annotated[AuthUseCase, Depends()]):
    """
    CONTROLLER: Register new user with provided data. Passes the query to the 'AuthUseCase'.


    Args:
        data (RegisterRequestForm): The data to register.
        auth_use_case (AuthUseCase): The authentication use-case.

    Returns:
        HTTPResponse: A JSON object containing success, error message and status code.

    Raises:
        HTTPException: If provided data doesn't match the requirements (RegisterRequestForm) or in case of server error.
    """
    try:
        result = await auth_use_case.register(data)
        return result
    except ValueError as e:
        if "User already exists" in str(e):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Currently, register service is not available. Try again later.')
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

