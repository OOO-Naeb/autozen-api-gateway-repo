from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from src.application.use_cases.auth_use_case import AuthUseCase
from src.main import app


@pytest.fixture
def mock_auth_use_case(monkeypatch):
    mock_auth_use_case = AsyncMock()

    async def mock_auth_use_case_dependency():
        return mock_auth_use_case

    app.dependency_overrides[AuthUseCase] = mock_auth_use_case_dependency

    yield mock_auth_use_case
    app.dependency_overrides = {}


async def login_test_helper(mock_auth_use_case, email, password, side_effect, expected_status_code, expected_response):
    mock_auth_use_case.login.side_effect = side_effect

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://127.0.0.1:8000/api/v1/auth") as client:
        response = await client.post(
            "/login",
            json={"email": email, "password": password}
        )

        assert response.status_code == expected_status_code
        assert response.json() == expected_response