import pytest
from starlette import status

from src.domain.exceptions import UnauthorizedException, SourceUnavailableException, SourceTimeoutException, \
    UnhandledException
from tests.fixtures.login_endpoint_fixtures import TEST_ACCESS_TOKEN, TEST_REFRESH_TOKEN, mock_auth_use_case_for_login
from tests.function_test_helper import function_test_helper

LOGIN_REQUEST_URL = 'http://localhost:8000/api/v1/auth/login'

@pytest.mark.asyncio
async def test_login_success(mock_auth_use_case_for_login):
    expected_response = {
        "success": True,
        "message": "Logged in successfully.",
        "access_token": TEST_ACCESS_TOKEN,
        "refresh_token": TEST_REFRESH_TOKEN,
        "token_type": "Bearer",
    }

    # (Login controller accepts one of two optional arguments: email or phone number)
    # Test in case if email was provided
    await function_test_helper(
        "post",
        LOGIN_REQUEST_URL,
        dependency_to_mock=mock_auth_use_case_for_login,
        dependency_method_name="login",
        request_data={
            'email': 'example@gmail.com',
            'password': 'test_password',
        },
        expected_status_code=status.HTTP_200_OK,
        expected_response=expected_response
    )

    # Test in case if phone number was provided
    await function_test_helper(
        "post",
        LOGIN_REQUEST_URL,
        dependency_to_mock=mock_auth_use_case_for_login,
        dependency_method_name="login",
        request_data={
            'phone_number': '+1(995)438-24-47',
            'password': 'test_password',
        },
        expected_status_code=status.HTTP_200_OK,
        expected_response=expected_response
    )


@pytest.mark.asyncio
async def test_login_unauthorized(mock_auth_use_case_for_login):
    expected_response = {"detail": UnauthorizedException.get_default_detail()}

    # (Login controller accepts one of two optional arguments: email or phone number)
    # Test in case if email was provided
    await function_test_helper(
        "post",
        LOGIN_REQUEST_URL,
        dependency_to_mock=mock_auth_use_case_for_login,
        dependency_method_name="login",
        request_data={
            'email': 'wrong_email@gmail.com',
            'password': 'wrong_password',
        },
        side_effect=UnauthorizedException(),
        expected_status_code=status.HTTP_401_UNAUTHORIZED,
        expected_response=expected_response
    )

    # Test in case if phone number was provided
    await function_test_helper(
        "post",
        LOGIN_REQUEST_URL,
        dependency_to_mock=mock_auth_use_case_for_login,
        dependency_method_name="login",
        request_data={
            'phone_number': '+1(995)438-24-47',
            'password': 'wrong_password',
        },
        expected_status_code=status.HTTP_401_UNAUTHORIZED
    )


@pytest.mark.asyncio
async def test_login_rabbitMQ_unavailable(mock_auth_use_case_for_login):
    expected_response = {"detail": "Currently, login service is not available. Try again later."}

    await function_test_helper(
        "post",
        LOGIN_REQUEST_URL,
        dependency_to_mock=mock_auth_use_case_for_login,
        dependency_method_name="login",
        request_data={
            'email': 'example@gmail.com',
            'password': 'test_password',
        },
        side_effect=SourceUnavailableException(),
        expected_status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        expected_response=expected_response
    )


@pytest.mark.asyncio
async def test_login_auth_service_unavailable(mock_auth_use_case_for_login):
    expected_response = {"detail": "Login service took too long to respond."}

    await function_test_helper(
        "post",
        LOGIN_REQUEST_URL,
        dependency_to_mock=mock_auth_use_case_for_login,
        dependency_method_name="login",
        request_data={
            'email': 'example@gmail.com',
            'password': 'test_password',
        },
        side_effect=SourceTimeoutException(),
        expected_status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        expected_response=expected_response
    )


@pytest.mark.asyncio
async def test_login_unhandled_error(mock_auth_use_case_for_login):
    expected_response = {"detail": "An unexpected error occurred."}

    await function_test_helper(
        "post",
        LOGIN_REQUEST_URL,
        dependency_to_mock=mock_auth_use_case_for_login,
        dependency_method_name="login",
        request_data={
            'email': 'example@gmail.com',
            'password': 'test_password',
        },
        side_effect=UnhandledException() or Exception(),
        expected_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        expected_response=expected_response
    )
