import pytest
from httpx import AsyncClient, ASGITransport
from starlette import status

from src.domain.exceptions import UnauthorizedException, SourceUnavailableException, SourceTimeoutException, \
    UnhandledException
from src.main import app

REFRESH_REQUEST_URL = 'http://localhost:8000/api/v1/auth/refresh'


@pytest.mark.asyncio
async def test_refresh_success(override_dependencies_refresh):
    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        response = await client.post(
            REFRESH_REQUEST_URL,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer VALID_REFRESH_TOKEN'
            },
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "success": True,
        'message': 'Tokens have been refreshed successfully.',
        "access_token": "NEW_TEST_ACCESS_TOKEN",
        "refresh_token": "NEW_TEST_REFRESH_TOKEN",
        "token_type": "Bearer"
    }


@pytest.mark.asyncio
async def test_refresh_unauthorized(override_dependencies_refresh, mock_auth_service_refresh):
    mock_auth_service_refresh.refresh.side_effect = UnauthorizedException()

    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        response = await client.post(
            REFRESH_REQUEST_URL,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer VALID_REFRESH_TOKEN'
            },
        )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": UnauthorizedException.get_default_detail()}


@pytest.mark.asyncio
async def test_refresh_service_unavailable(override_dependencies_refresh, mock_auth_service_refresh):
    mock_auth_service_refresh.refresh.side_effect = SourceUnavailableException()

    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        response = await client.post(
            REFRESH_REQUEST_URL,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer VALID_REFRESH_TOKEN'
            },
        )

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json() == {"detail": "Currently, tokens refresh service is not available. Try again later."}


@pytest.mark.asyncio
async def test_refresh_timeout(override_dependencies_refresh, mock_auth_service_refresh):
    mock_auth_service_refresh.refresh.side_effect = SourceTimeoutException()

    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        response = await client.post(
            REFRESH_REQUEST_URL,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer VALID_REFRESH_TOKEN'
            },
        )

    assert response.status_code == status.HTTP_504_GATEWAY_TIMEOUT
    assert response.json() == {"detail": "Token refresh service took too long to respond."}


@pytest.mark.asyncio
async def test_refresh_unhandled_error(override_dependencies_refresh, mock_auth_service_refresh):
    mock_auth_service_refresh.refresh.side_effect = UnhandledException()

    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        response = await client.post(
            REFRESH_REQUEST_URL,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer VALID_REFRESH_TOKEN'
            },
        )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"detail": "An unexpected error occurred."}
