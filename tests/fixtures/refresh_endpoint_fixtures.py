from src.application.use_cases.auth_use_case import AuthUseCase
from src.domain.schemas import Tokens
from src.main import app
import pytest
from unittest.mock import AsyncMock


@pytest.fixture
def mock_auth_use_case_refresh():
    mock = AsyncMock()
    mock.refresh.return_value = Tokens(
        access_token='NEW_TEST_ACCESS_TOKEN',
        refresh_token="NEW_TEST_REFRESH_TOKEN"
    )
    return mock


@pytest.fixture
def override_dependencies_refresh(mock_auth_use_case_refresh):
    app.dependency_overrides = {AuthUseCase: lambda: mock_auth_use_case_refresh}
    yield
    app.dependency_overrides = {}
