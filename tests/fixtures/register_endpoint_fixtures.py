from src.application.services.auth_service import AuthService
from src.domain.schemas import UserFromDB
from src.main import app


import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_auth_use_case_register():
    mock = AsyncMock()
    mock.register.return_value = UserFromDB(
        id=1,
        first_name='Igor',
        last_name='Ruzhilov',
        middle_name='Alexandrovich',
        email='example@gmail.com',
        phone_number='+1(965)344-67-92',
        role='css_admin'
    )
    return mock


@pytest.fixture
def override_dependencies_register(mock_auth_use_case_register):
    app.dependency_overrides = {AuthService: lambda: mock_auth_use_case_register}
    yield
    app.dependency_overrides = {}

