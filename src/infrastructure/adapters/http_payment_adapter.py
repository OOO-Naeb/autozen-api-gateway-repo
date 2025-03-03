import httpx
from typing import Any, Dict, Optional, Type

from src.core.exceptions import ApiGatewayError
from src.core.logger import LoggerService
from src.domain.interfaces.http_payment_adapter_interface import IHttpPaymentAdapter
from src.domain.models.payment_responses import PaymentServiceResponseDTO
from src.infrastructure.exceptions import PaymentServiceError


class PaymentHttpClient(IHttpPaymentAdapter):
    """
    HTTP-client for communication with Payment Service.
    """
    def __init__(self, logger: LoggerService, base_url: str, timeout: int = 5) -> None:
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._logger = logger

    async def _request(
        self,
        method: str,
        endpoint: str,
        response_model: Type[PaymentServiceResponseDTO],
        payload: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> PaymentServiceResponseDTO:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {"Content-Type": "application/json"}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(method, url, json=payload, params=params, headers=headers)
                self._logger.debug(f"Response status: {response.status_code}")
                self._logger.debug(f"Response data: {response.text}")

                response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_payment_service_error(e)
        except httpx.RequestError as e:
            if "Connection refused" in str(e):
                self._logger.critical(f"Payment Service is not available: {e}.")
                raise PaymentServiceError(status_code=504, detail="Payment Service is not available.")
            self._logger.critical(f"Request error occurred. Probably, the Payment Service is not responding: {e}.")
            raise ApiGatewayError(status_code=500, detail=str(e))
        except httpx.TimeoutException as e:
            self._logger.critical(f"Request timeout occurred: {e}")
            raise PaymentServiceError(status_code=504, detail=str(e))

        try:
            data = response.json()
        except Exception as e:
            self._logger.error(f"Error parsing JSON response: {e}")
            raise ApiGatewayError(status_code=500, detail="Invalid JSON response.")

        content = data.get('content') if isinstance(data, dict) and 'content' in data else data

        if not isinstance(content, dict):
            self._logger.error(f"Invalid response format: {content}")
            raise ApiGatewayError(status_code=500, detail="Invalid response format.")
        try:
            return response_model(**content)
        except Exception as e:
            self._logger.error(f"Error constructing response model: {e}.")
            raise ApiGatewayError(status_code=500, detail="Error processing response data.")

    async def post(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        response_model: Type[PaymentServiceResponseDTO]
    ) -> PaymentServiceResponseDTO:
        return await self._request("POST", endpoint, response_model, payload=payload)

    async def get(
        self,
        response_model: Type[PaymentServiceResponseDTO],
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> PaymentServiceResponseDTO:
        return await self._request("GET", endpoint, response_model, params=params)

    async def put(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        response_model: Type[PaymentServiceResponseDTO]
    ) -> PaymentServiceResponseDTO:
        return await self._request("PUT", endpoint, response_model, payload=payload)

    async def delete(
        self,
        response_model: Type[PaymentServiceResponseDTO],
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> PaymentServiceResponseDTO:
        return await self._request("DELETE", endpoint, response_model, params=params)

    def _handle_payment_service_error(self, e: httpx.HTTPStatusError) -> None:
        status_code = e.response.status_code
        error_details = dict(e.response.json()).get("detail")

        if status_code == 400:
            self._logger.error(f"Payment Service Error (400): {error_details}")
            raise PaymentServiceError(status_code=status_code, detail=f"Bad request. From Payment Service: {error_details}")
        elif status_code == 403:
            self._logger.warning(f"Payment Service Error (403): {error_details}")
            raise PaymentServiceError(status_code=status_code, detail=f"Forbidden. From Payment Service: {error_details}")
        elif status_code == 404:
            self._logger.warning(f"Payment Service Error (404): {error_details}")
            raise PaymentServiceError(status_code=status_code, detail=f"User or company with provided ID does not exist.")
        elif status_code == 409:
            self._logger.warning(f"Payment Service Error (409): {error_details}")
            raise PaymentServiceError(status_code=status_code, detail=f"Conflict. {error_details}")
        elif status_code == 422:
            self._logger.error(f"Payment Service Error (422): {error_details}")
            raise PaymentServiceError(status_code=status_code, detail=f"Unprocessable Entity. From Payment Service: {error_details}")
        elif status_code == 500:
            self._logger.critical(f"Payment Service Error (500): {error_details}")
            raise PaymentServiceError(status_code=status_code, detail=f"Internal Server Error. From Payment Service: {error_details}")
        else:
            self._logger.critical(f"Unhandled Payment Service Error ({status_code}): {error_details}.")
            raise PaymentServiceError(status_code=status_code, detail=f"Unexpected error from Payment Service: {error_details}.")
