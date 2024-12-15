from src.application.services.auth_service import AuthService
from src.domain.schemas import Tokens
from src.main import app
import pytest
from unittest.mock import AsyncMock


@pytest.fixture
def mock_auth_service_refresh():
    mock = AsyncMock()
    mock.refresh.return_value = Tokens(
        access_token='NEW_TEST_ACCESS_TOKEN',
        refresh_token="NEW_TEST_REFRESH_TOKEN"
    )
    return mock


@pytest.fixture
def override_dependencies_refresh(mock_auth_service_refresh):
    app.dependency_overrides = {AuthService: lambda: mock_auth_service_refresh}
    yield
    app.dependency_overrides = {}
