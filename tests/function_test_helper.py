from typing import Literal, Optional, Dict, Any
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport

from src.main import app


async def function_test_helper(
    http_method: Literal["get", "post", "put", "delete", "patch"],
    request_url: str,
    dependency_to_mock: AsyncMock,
    dependency_method_name: str,
    request_data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    side_effect: Optional[Exception] = None,
    expected_status_code: int = 200,
    expected_response: Optional[Any] = None,
):
    if side_effect:
        setattr(dependency_to_mock, dependency_method_name, AsyncMock(side_effect=side_effect))

    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        method = getattr(client, http_method)
        response = await method(request_url, json=request_data, headers=headers)

        assert response.status_code == expected_status_code

        if expected_response is not None:
            response = response.json()
            print("RESPONSE JSON:", response)
            print("EXPECTED RESPONSE:", expected_response)
            assert response == expected_response
