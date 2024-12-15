import pytest
from httpx import AsyncClient, ASGITransport
from starlette import status

from src.domain.exceptions import UnauthorizedException, SourceUnavailableException, SourceTimeoutException, \
    UnhandledException
from src.main import app

LOGIN_REQUEST_URL = 'http://localhost:8000/api/v1/auth/login'


@pytest.mark.asyncio
async def test_login_success_with_email(override_dependencies):
    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        response = await client.post(
            LOGIN_REQUEST_URL,
            json={"email": "example@gmail.com", "password": "test_password"}
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "success": True,
        "message": "Logged in successfully.",
        "access_token": "TEST_ACCESS_TOKEN",
        "refresh_token": "TEST_REFRESH_TOKEN",
        "token_type": "Bearer",
    }


@pytest.mark.asyncio
async def test_login_success_with_phone(override_dependencies):
    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        response = await client.post(
            LOGIN_REQUEST_URL,
            json={"phone_number": "+1(995)438-24-47", "password": "test_password"}
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "success": True,
        "message": "Logged in successfully.",
        "access_token": "TEST_ACCESS_TOKEN",
        "refresh_token": "TEST_REFRESH_TOKEN",
        "token_type": "Bearer",
    }


@pytest.mark.asyncio
async def test_login_unauthorized_email(override_dependencies, mock_auth_service):
    mock_auth_service.login.side_effect = UnauthorizedException()

    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        response = await client.post(
            LOGIN_REQUEST_URL,
            json={"email": "wrong_email@gmail.com", "password": "wrong_password"}
        )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": UnauthorizedException.get_default_detail()}


@pytest.mark.asyncio
async def test_login_unauthorized_phone(override_dependencies, mock_auth_service):
    mock_auth_service.login.side_effect = UnauthorizedException()

    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        response = await client.post(
            LOGIN_REQUEST_URL,
            json={"phone_number": "+1(995)438-24-47", "password": "wrong_password"}
        )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": UnauthorizedException.get_default_detail()}


@pytest.mark.asyncio
async def test_login_rabbitmq_unavailable(override_dependencies, mock_auth_service):
    mock_auth_service.login.side_effect = SourceUnavailableException()

    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        response = await client.post(
            LOGIN_REQUEST_URL,
            json={"email": "example@gmail.com", "password": "test_password"}
        )

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json() == {"detail": "Currently, login service is not available. Try again later."}


@pytest.mark.asyncio
async def test_login_auth_service_timeout(override_dependencies, mock_auth_service):
    mock_auth_service.login.side_effect = SourceTimeoutException()

    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        response = await client.post(
            LOGIN_REQUEST_URL,
            json={"email": "example@gmail.com", "password": "test_password"}
        )

    assert response.status_code == status.HTTP_504_GATEWAY_TIMEOUT
    assert response.json() == {"detail": "Login service took too long to respond."}


@pytest.mark.asyncio
async def test_login_unhandled_error(override_dependencies, mock_auth_service):
    mock_auth_service.login.side_effect = UnhandledException()

    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        response = await client.post(
            LOGIN_REQUEST_URL,
            json={"email": "example@gmail.com", "password": "test_password"}
        )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"detail": "An unexpected error occurred."}

