from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type

import httpx

from src.domain.models.payment_responses import PaymentServiceResponseDTO


class IHttpPaymentAdapter(ABC):
    @abstractmethod
    async def post(
            self,
            endpoint: str,
            payload: Dict[str, Any],
            response_model: Type[PaymentServiceResponseDTO],
            headers: Optional[Dict[str, str]] = None
    ) -> PaymentServiceResponseDTO | None:
        """
        Asynchronously sends a POST request.
        """
        pass

    @abstractmethod
    async def get(
            self,
            response_model: Type[PaymentServiceResponseDTO],
            endpoint: str,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None
    ) -> PaymentServiceResponseDTO | None:
        """
        Asynchronously sends a GET request.
        """
        pass

    @abstractmethod
    async def put(
            self,
            endpoint: str,
            payload: Dict[str, Any],
            response_model: Type[PaymentServiceResponseDTO],
            headers: Optional[Dict[str, str]] = None
    ) -> PaymentServiceResponseDTO | None:
        """
        Asynchronously sends a PUT request.
        """
        pass

    @abstractmethod
    async def delete(
            self,
            response_model: Type[PaymentServiceResponseDTO],
            endpoint: str,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None
    ) -> PaymentServiceResponseDTO | None:
        """
        Asynchronously sends a DELETE request.
        """
        pass

    @abstractmethod
    def _handle_payment_service_error(self, e: httpx.HTTPStatusError) -> None:
        """
        Handle error status codes from the Payment Service.
        """
        pass