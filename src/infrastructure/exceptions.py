class RabbitMQError(Exception):
    """Exception for RabbitMQ connection errors."""
    def __init__(self, status_code: int = 503, detail: str = 'RabbitMQ service is unavailable') -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.status_code, self.detail)


class PaymentServiceError(Exception):
    """Exception for Payment Service's responses errors."""
    def __init__(self, detail: str = "An error occurred in the Payment Service.", status_code: int = 500):
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.status_code, self.detail)


class AuthServiceError(Exception):
    """Exception for Auth Service's responses errors."""
    def __init__(self, detail: str = "An error occurred in the Auth Service.", status_code: int = 500):
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.status_code, self.detail)
