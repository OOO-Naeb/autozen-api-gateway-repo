from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Body
from starlette import status
from starlette.responses import JSONResponse

from src.application.use_cases.auth_use_case import AuthUseCase
from src.domain.exceptions import SourceTimeoutException, NotFoundException, \
    UnauthorizedException, SourceUnavailableException, ConflictException, UnhandledException
from src.domain.oauth_schemas import oauth2_token_schema
from src.domain.schemas import Tokens, RefreshToken, LoginRequestForm, RegisterRequestForm, AccessToken

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
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e.detail))
    except SourceUnavailableException:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail='Currently, login service is not available. Try again later.')
    except SourceTimeoutException:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Login service took too long to respond.")
    except UnhandledException or Exception:
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
        tokens = await auth_use_case.refresh(str(refresh_token))
        return tokens
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e.detail))
    except SourceUnavailableException:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail='Currently, tokens refresh service is not available. Try again later.')
    except SourceTimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Token refresh service took too long to respond."
        )
    except UnhandledException or Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")


@auth_router.post('/register')
async def register(data: Annotated[RegisterRequestForm, Body(...)], auth_use_case: Annotated[AuthUseCase, Depends()]) -> JSONResponse:
    """
    CONTROLLER: Register new user with provided data. Passes the query to the 'AuthUseCase'.

    Args:
        data (RegisterRequestForm): The data to register.
        auth_use_case (AuthUseCase): The authentication use-case.

    Returns:
        JSONResponse: A JSON object containing success, error message and status code.

    Raises:
        HTTPException (503): When RabbitMQ service is not available.
        HTTPException (504): When waiting time from the 'AuthService' microservice exceeds the timeout (5s).
        HTTPException (404): If user or source was not found.
        HTTPException (409): When given email or phone number is already in the DB.
        HTTPException (500): If unknown exception occurs.
    """
    try:
        result = await auth_use_case.register(data)
        status_code, user_data = result

        return JSONResponse(
            status_code=int(status_code),
            content={"success": True, "user": user_data.dict(), "message": "User registered successfully"}
        )

    except SourceUnavailableException:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Currently, the registration service is not available. Please try again later.")
    except SourceTimeoutException:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                            detail="The registration service took too long to respond. Please try again later.")
    except NotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Source not found.")
    except ConflictException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="This email or phone number is already taken.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An unexpected error occurred during registration: {str(e)}")


@auth_router.post('/test_token')
async def test_token(access_token: Annotated[AccessToken, Depends(oauth2_token_schema)], auth_use_case: Annotated[AuthUseCase, Depends()]):
    try:
        tokens = await auth_use_case.test_token(str(access_token))
        return tokens
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e.detail))
    except SourceUnavailableException:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail='Currently, tokens refresh service is not available. Try again later.')
    except SourceTimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Token refresh service took too long to respond."
        )
    except UnhandledException or Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")
