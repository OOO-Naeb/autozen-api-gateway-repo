from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from src.application.use_cases.auth_use_case import AuthUseCase
from src.main import app

TEST_ACCESS_TOKEN = "test_access_token"
TEST_REFRESH_TOKEN_RECEIVED = "test_refresh_token_received"
TEST_REFRESH_TOKEN_TO_SEND = "test_refresh_token_sent"

@pytest.fixture()
def mock_auth_use_case(monkeypatch):
    mock_auth_use_case = AsyncMock()

    async def mock_auth_use_case_dependency():
        return mock_auth_use_case

    app.dependency_overrides[AuthUseCase] = mock_auth_use_case_dependency

    yield mock_auth_use_case
    app.dependency_overrides = {}


async def refresh_test_helper(mock_auth_use_case, refresh_token, side_effect, expected_status_code, expected_response):
    mock_auth_use_case.refresh.side_effect = side_effect

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://127.0.0.1:8000/api/v1/auth") as client:
        response = await client.post(
             "/refresh",
                headers={"Authorization": f"Bearer {refresh_token}"}
        )

        assert response.status_code == expected_status_code
        assert response.json() == expected_response
