import pytest
from starlette import status

from src.domain.exceptions import UnauthorizedException, SourceUnavailableException, SourceTimeoutException, \
    UnhandledException
from tests.fixtures.refresh_endpoint_fixtures import mock_auth_use_case_for_refresh, TEST_ACCESS_TOKEN, TEST_REFRESH_TOKEN_TO_SEND, \
    TEST_REFRESH_TOKEN_RECEIVED
from tests.function_test_helper import function_test_helper

REFRESH_REQUEST_URL = 'http://localhost:8000/api/v1/auth/refresh'

@pytest.mark.asyncio
async def test_refresh_success(mock_auth_use_case_for_refresh):
    expected_response = {
        "success": True,
        "message": "Tokens have been refreshed successfully.",
        "access_token": TEST_ACCESS_TOKEN,
        "refresh_token": TEST_REFRESH_TOKEN_RECEIVED,
        "token_type": "Bearer",
    }

    await function_test_helper(
        'post',
        REFRESH_REQUEST_URL,
        dependency_to_mock=mock_auth_use_case_for_refresh,
        dependency_method_name='refresh',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {TEST_REFRESH_TOKEN_TO_SEND}',
        },
        expected_status_code=status.HTTP_200_OK,
        expected_response=expected_response
    )


@pytest.mark.asyncio
async def test_refresh_unauthorized(mock_auth_use_case_for_refresh):
    expected_response = {"detail": UnauthorizedException.get_default_detail()}

    await function_test_helper(
        'post',
        REFRESH_REQUEST_URL,
        dependency_to_mock=mock_auth_use_case_for_refresh,
        dependency_method_name='refresh',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {TEST_REFRESH_TOKEN_TO_SEND}',
        },
        side_effect=UnauthorizedException(),
        expected_status_code=status.HTTP_401_UNAUTHORIZED,
        expected_response=expected_response
    )


@pytest.mark.asyncio
async def test_refresh_rabbitMQ_unavailable(mock_auth_use_case_for_refresh):
    expected_response = {"detail": "Currently, tokens refresh service is not available. Try again later."}

    await function_test_helper(
        'post',
        REFRESH_REQUEST_URL,
        dependency_to_mock=mock_auth_use_case_for_refresh,
        dependency_method_name='refresh',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {TEST_REFRESH_TOKEN_TO_SEND}',
        },
        side_effect=SourceUnavailableException(),
        expected_status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        expected_response=expected_response
    )


@pytest.mark.asyncio
async def test_refresh_auth_service_unavailable(mock_auth_use_case_for_refresh):
    expected_response = {"detail": "Token refresh service took too long to respond."}

    await function_test_helper(
        'post',
        REFRESH_REQUEST_URL,
        dependency_to_mock=mock_auth_use_case_for_refresh,
        dependency_method_name='refresh',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {TEST_REFRESH_TOKEN_TO_SEND}',
        },
        side_effect=SourceTimeoutException(),
        expected_status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        expected_response=expected_response
    )


@pytest.mark.asyncio
async def test_refresh_unhandled_error(mock_auth_use_case_for_refresh):
    expected_response = {"detail": "An unexpected error occurred."}

    await function_test_helper(
        'post',
        REFRESH_REQUEST_URL,
        dependency_to_mock=mock_auth_use_case_for_refresh,
        dependency_method_name='refresh',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {TEST_REFRESH_TOKEN_TO_SEND}',
        },
        side_effect=UnhandledException(),
        expected_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        expected_response=expected_response
    )
