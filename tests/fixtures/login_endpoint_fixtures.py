from unittest.mock import AsyncMock

import pytest

from src.application.use_cases.auth_use_case import AuthUseCase
from src.domain.schemas import Tokens
from src.main import app

TEST_ACCESS_TOKEN = "test_access_token"
TEST_REFRESH_TOKEN = "test_refresh_token"


@pytest.fixture
def mock_auth_use_case_for_login(monkeypatch):
    mock_auth_use_case = AsyncMock()

    mock_auth_use_case.login.return_value = Tokens(
        access_token=TEST_ACCESS_TOKEN,
        refresh_token=TEST_REFRESH_TOKEN
    )

    async def mock_auth_use_case_dependency():
        return mock_auth_use_case

    app.dependency_overrides[AuthUseCase] = mock_auth_use_case_dependency

    yield mock_auth_use_case

    app.dependency_overrides = {}
