import pytest
from starlette import status

from src.domain.exceptions import UnauthorizedException, SourceUnavailableException, SourceTimeoutException, \
    UnhandledException
from src.domain.schemas import Tokens
from tests.fixtures.refresh_endpoint_fixtures import mock_auth_use_case, TEST_ACCESS_TOKEN, TEST_REFRESH_TOKEN_TO_SEND, \
    TEST_REFRESH_TOKEN_RECEIVED, refresh_test_helper


@pytest.mark.asyncio
async def test_refresh_success(mock_auth_use_case):
    mock_auth_use_case.refresh.return_value = Tokens(access_token=TEST_ACCESS_TOKEN, refresh_token=TEST_REFRESH_TOKEN_RECEIVED)
    expected_response = {
        "success": True,
        "message": "Tokens have been refreshed successfully.",
        "access_token": TEST_ACCESS_TOKEN,
        "refresh_token": TEST_REFRESH_TOKEN_RECEIVED,
        "token_type": "Bearer",
    }

    await refresh_test_helper(
        mock_auth_use_case,
        TEST_REFRESH_TOKEN_TO_SEND,
        None,
        status.HTTP_200_OK,
        expected_response
    )


@pytest.mark.asyncio
async def test_refresh_unauthorized(mock_auth_use_case):
    expected_response = {"detail": "Unauthorized. Token has expired or invalid. Access Denied."}

    await refresh_test_helper(
        mock_auth_use_case,
        "wrong_token",
        UnauthorizedException(),
        status.HTTP_401_UNAUTHORIZED,
        expected_response
    )


@pytest.mark.asyncio
async def test_refresh_rabbitMQ_unavailable(mock_auth_use_case):
    expected_response = {"detail": "Currently, tokens refresh service is not available. Try again later."}
    await refresh_test_helper(mock_auth_use_case, TEST_REFRESH_TOKEN_TO_SEND, SourceUnavailableException(), status.HTTP_503_SERVICE_UNAVAILABLE, expected_response)


@pytest.mark.asyncio
async def test_login_auth_service_unavailable(mock_auth_use_case):
    expected_response = {"detail": "Token refresh service took too long to respond."}

    await refresh_test_helper(mock_auth_use_case, TEST_REFRESH_TOKEN_TO_SEND, SourceTimeoutException(), status.HTTP_504_GATEWAY_TIMEOUT, expected_response)


@pytest.mark.asyncio
async def test_refresh_unhandled_error(mock_auth_use_case):
    expected_response = {"detail": "An unexpected error occurred."}

    await refresh_test_helper(mock_auth_use_case, TEST_REFRESH_TOKEN_TO_SEND, UnhandledException(), status.HTTP_500_INTERNAL_SERVER_ERROR, expected_response)





