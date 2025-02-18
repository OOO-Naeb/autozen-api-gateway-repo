from src.core.exceptions import ApiGatewayError


class CardValidationError(ApiGatewayError):
    """Exception for Card validation errors."""
    def __init__(self, detail: str = "An error occurred in while validating Card data.", status_code: int = 503):
        super().__init__(detail=detail, status_code=status_code)
