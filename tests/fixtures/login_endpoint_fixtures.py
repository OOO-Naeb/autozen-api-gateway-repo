from src.application.services.auth_service import AuthService
from src.domain.schemas import Tokens
from src.main import app

TEST_ACCESS_TOKEN = "test_access_token"
TEST_REFRESH_TOKEN = "test_refresh_token"


import pytest
from unittest.mock import AsyncMock


@pytest.fixture
def mock_auth_use_case():
    mock = AsyncMock()
    mock.login.return_value = Tokens(
        access_token="TEST_ACCESS_TOKEN",
        refresh_token="TEST_REFRESH_TOKEN"
    )
    return mock


@pytest.fixture
def override_dependencies(mock_auth_use_case):
    app.dependency_overrides = {AuthService: lambda: mock_auth_use_case}
    yield
    app.dependency_overrides = {}

