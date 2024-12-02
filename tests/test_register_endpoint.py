import pytest
from httpx import AsyncClient, ASGITransport
from starlette import status

from src.domain.exceptions import SourceUnavailableException, SourceTimeoutException, ConflictException, \
    UnhandledException
from src.main import app

REGISTER_REQUEST_URL = 'http://localhost:8000/api/v1/auth/register'


@pytest.mark.asyncio
async def test_register_success(override_dependencies_register, mock_auth_use_case_register):
    expected_response = {
        "success": True,
        "message": "User registered successfully.",
        "user": {
            "id": 1,
            "first_name": "Igor",
            "last_name": "Ruzhilov",
            "middle_name": "Alexandrovich",
            "email": "example@gmail.com",
            "phone_number": "+1(965)344-67-92",
            "role": "css_admin",
        },
    }

    request_data = {
        "first_name": "Igor",
        "last_name": "Ruzhilov",
        "middle_name": "Alexandrovich",
        "email": "example@gmail.com",
        "phone_number": "+1(965)344-67-92",
        "password": "test_pass",
        "role": "css_admin",
    }

    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        response = await client.post(REGISTER_REQUEST_URL, json=request_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == expected_response


@pytest.mark.asyncio
async def test_register_rabbitmq_unavailable(override_dependencies_register, mock_auth_use_case_register):
    mock_auth_use_case_register.register.side_effect = SourceUnavailableException()
    expected_response = {'detail': 'Currently, the registration service is not available. Please try again later.'}

    request_data = {
        "first_name": "Igor",
        "last_name": "Ruzhilov",
        "middle_name": "Alexandrovich",
        "email": "example@gmail.com",
        "phone_number": "+1(965)344-67-92",
        "password": "test_pass",
        "role": "css_admin",
    }

    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        response = await client.post(REGISTER_REQUEST_URL, json=request_data)

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json() == expected_response


@pytest.mark.asyncio
async def test_register_auth_service_timout(override_dependencies_register, mock_auth_use_case_register):
    mock_auth_use_case_register.register.side_effect = SourceTimeoutException()
    expected_response = {'detail': 'The registration service took too long to respond. Please try again later.'}

    request_data = {
        "first_name": "Igor",
        "last_name": "Ruzhilov",
        "middle_name": "Alexandrovich",
        "email": "example@gmail.com",
        "phone_number": "+1(965)344-67-92",
        "password": "test_pass",
        "role": "css_admin",
    }

    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        response = await client.post(REGISTER_REQUEST_URL, json=request_data)

    assert response.status_code == status.HTTP_504_GATEWAY_TIMEOUT
    assert response.json() == expected_response


@pytest.mark.asyncio
async def test_register_email_or_phone_conflict(override_dependencies_register, mock_auth_use_case_register):
    mock_auth_use_case_register.register.side_effect = ConflictException()
    expected_response = {'detail': 'This email or phone number is already taken.'}

    request_data = {
        "first_name": "Igor",
        "last_name": "Ruzhilov",
        "middle_name": "Alexandrovich",
        "email": "example@gmail.com",
        "phone_number": "+1(965)344-67-92",
        "password": "test_pass",
        "role": "css_admin",
    }

    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        response = await client.post(REGISTER_REQUEST_URL, json=request_data)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == expected_response


@pytest.mark.asyncio
async def test_register_unhandled_error(override_dependencies_register, mock_auth_use_case_register):
    mock_auth_use_case_register.register.side_effect = UnhandledException()
    expected_response = {'detail': 'An unexpected error occurred.'}

    request_data = {
        "first_name": "Igor",
        "last_name": "Ruzhilov",
        "middle_name": "Alexandrovich",
        "email": "example@gmail.com",
        "phone_number": "+1(965)344-67-92",
        "password": "test_pass",
        "role": "css_admin",
    }

    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        response = await client.post(REGISTER_REQUEST_URL, json=request_data)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == expected_response
