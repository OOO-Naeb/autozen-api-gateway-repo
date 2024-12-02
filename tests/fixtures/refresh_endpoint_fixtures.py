from unittest.mock import AsyncMock

import pytest

from src.application.use_cases.auth_use_case import AuthUseCase
from src.domain.schemas import Tokens
from src.main import app

TEST_ACCESS_TOKEN = "test_access_token"
TEST_REFRESH_TOKEN_RECEIVED = "test_refresh_token_received"
TEST_REFRESH_TOKEN_TO_SEND = "test_refresh_token_sent"

@pytest.fixture
def mock_auth_use_case_for_refresh(monkeypatch):
    mock_auth_use_case = AsyncMock()

    mock_auth_use_case.refresh.return_value = Tokens(
        access_token=TEST_ACCESS_TOKEN,
        refresh_token=TEST_REFRESH_TOKEN_RECEIVED
    )

    async def mock_auth_use_case_dependency():
        return mock_auth_use_case

    app.dependency_overrides[AuthUseCase] = mock_auth_use_case_dependency

    yield mock_auth_use_case

    app.dependency_overrides = {}
