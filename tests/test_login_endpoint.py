import pytest
from starlette import status

from src.domain.exceptions import UnauthorizedException, SourceUnavailableException, SourceTimeoutException, \
    UnhandledException
from src.domain.schemas import Tokens
from tests.fixtures.login_endpoint_fixtures import login_test_helper

TEST_ACCESS_TOKEN = "test_access_token"
TEST_REFRESH_TOKEN = "test_refresh_token"


@pytest.mark.asyncio
async def test_login_success(mock_auth_use_case):
    mock_auth_use_case.login.return_value = Tokens(access_token=TEST_ACCESS_TOKEN, refresh_token=TEST_REFRESH_TOKEN)
    expected_response = {
        "success": True,
        "message": "Logged in successfully.",
        "access_token": TEST_ACCESS_TOKEN,
        "refresh_token": TEST_REFRESH_TOKEN,
        "token_type": "Bearer",
    }

    await login_test_helper(mock_auth_use_case, "test.root@example.com", "test_password", None, status.HTTP_200_OK, expected_response)


@pytest.mark.asyncio
async def test_login_unauthorized(mock_auth_use_case):
    expected_response = {"detail": "Invalid credentials"}

    await login_test_helper(mock_auth_use_case, "wrong@example.com", "wrong_password", UnauthorizedException("Invalid credentials"), status.HTTP_401_UNAUTHORIZED, expected_response)


@pytest.mark.asyncio
async def test_login_rabbitMQ_unavailable(mock_auth_use_case):
    expected_response = {"detail": "Currently, login service is not available. Try again later."}
    await login_test_helper(mock_auth_use_case, "test.root@example.com", "test_password", SourceUnavailableException(), status.HTTP_503_SERVICE_UNAVAILABLE, expected_response)


@pytest.mark.asyncio
async def test_login_auth_service_unavailable(mock_auth_use_case):
    expected_response = {"detail": "Login service took too long to respond."}

    await login_test_helper(mock_auth_use_case, "test.root@example.com", "test_password", SourceTimeoutException(), status.HTTP_504_GATEWAY_TIMEOUT, expected_response)


@pytest.mark.asyncio
async def test_login_unhandled_error(mock_auth_use_case):
    expected_response = {"detail": "An unexpected error occurred."}

    await login_test_helper(mock_auth_use_case, "test.root@example.com", "test_password", UnhandledException(), status.HTTP_500_INTERNAL_SERVER_ERROR, expected_response)
