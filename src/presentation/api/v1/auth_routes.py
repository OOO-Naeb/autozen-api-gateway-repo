from typing import Annotated

from fastapi import APIRouter, Depends, Body
from starlette import status
from starlette.responses import JSONResponse

from src.application.use_cases.login import LoginUseCase
from src.application.use_cases.refresh import RefreshUseCase
from src.application.use_cases.register import RegisterUseCase
from src.core.dependencies import get_login_use_case, get_refresh_use_case, get_register_use_case
from src.core.jwt_validator import JWTValidator
from src.domain.models.auth_requests import LoginRequestDTO, RefreshTokenRequestDTO, RegisterRequestDTO
from src.domain.models.auth_responses import LoginResponseDTO
from src.domain.oauth_schemas import oauth2_token_schema
from src.presentation.schemas import RegisterRequestForm, LoginRequestSchema, RolesEnum

auth_router = APIRouter(
    tags=["Auth"],
    prefix="/api/v1/auth",
)

@auth_router.post('/login')
async def login(
    form_data: Annotated[LoginRequestSchema, Body(...)],
    login_use_case: Annotated[LoginUseCase, Depends(get_login_use_case)],
) -> JSONResponse:
    """
    CONTROLLER: Log in a user with provided credentials. Passes the query to the 'LoginUseCase'.

    Args:
        form_data (LoginRequestSchema): The login credentials provided by the client.
        login_use_case (LoginUseCase): The login use-case.

    Returns:
        JSONResponse: A JSON object containing access, refresh tokens and token type.
    """
    domain_schema_data = LoginRequestDTO(**form_data.model_dump())
    tokens = await login_use_case.execute(domain_schema_data)

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


@auth_router.post("/refresh")
async def refresh(
        refresh_token: Annotated[str, Depends(oauth2_token_schema)],
        refresh_use_case: Annotated[RefreshUseCase, Depends(get_refresh_use_case)],
        jwt_validator: Annotated[JWTValidator, Depends(JWTValidator)]
) -> JSONResponse:
    """
    CONTROLLER: Return a new pair of access and refresh tokens. Passes the query to the 'RefreshUseCase'.

    Args:
        refresh_token (RefreshToken): The refresh token to get both new access and refresh tokens.
        refresh_use_case (RefreshUseCase): The refresh use-case.
        jwt_validator (JWTValidator): The JWT validator.

    Returns:
        JSONResponse: A JSON object containing access, refresh tokens and token type.
    """
    token_payload = jwt_validator.validate_token(refresh_token, required_token_type='refresh')
    print("Token payload:", token_payload)
    domain_schema_data = RefreshTokenRequestDTO(
        user_id=token_payload.get('sub'),
        roles=token_payload.get('roles')
    )
    tokens = await refresh_use_case.execute(domain_schema_data)

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
async def register(
        data: Annotated[RegisterRequestForm, Body(...)],
        register_use_case: Annotated[RegisterUseCase, Depends(get_register_use_case)]
) -> JSONResponse:
    """
    CONTROLLER: Register new user with provided data. Passes the query to the 'RegisterUseCase'.

    Args:
        data (RegisterRequestForm): The data to register.
        register_use_case (RegisterUseCase): The register use-case.

    Returns:
        JSONResponse: A JSON object containing success, error message and status code.
    """
    print("What we've got:", data.model_dump())
    domain_schema_data = RegisterRequestDTO(**data.model_dump())
    created_user_data = await register_use_case.execute(domain_schema_data)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "success": True,
            "message": "User registered successfully.",
            "user": created_user_data.to_dict(),
        }
    )


@auth_router.post('/test_token')
async def test_token(
        access_token: Annotated[str, Depends(oauth2_token_schema)],
        jwt_validator: Annotated[JWTValidator, Depends(JWTValidator)]
):
    jwt_validator.validate_token(
        access_token,
        required_token_type='access',
        required_roles=[RolesEnum.USER]
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'success': True,
            'message': 'Test token endpoint has been passed successfully.',
        },
    )
