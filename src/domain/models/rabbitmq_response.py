from dataclasses import dataclass
from typing import Union, Optional


@dataclass
class RabbitMQResponse:
    """Value object for RabbitMQ response with error handling."""
    status_code: int
    body: Union[str, dict]
    success: bool = True
    error_message: Optional[str] = None
    error_origin: Optional[str] = None

    @classmethod
    def success_response(cls, status_code: int, body: Union[str, dict]) -> "RabbitMQResponse":
        return cls(
            status_code=status_code,
            body=body,
            success=True
        )

    @classmethod
    def error_response(cls, status_code: int, error_origin: str, message: str = '') -> "RabbitMQResponse":
        return cls(
            status_code=status_code,
            body={},
            success=False,
            error_message=message,
            error_origin=error_origin
        )
