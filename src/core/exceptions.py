class ApiGatewayError(Exception):
    """Base infrastructure exception for API Gateway errors."""
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.detail)

