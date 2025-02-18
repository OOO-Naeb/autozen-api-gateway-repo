from src.core.logger import LoggerService
from src.domain.interfaces.auth_adapter_interface import IAuthAdapter
from src.domain.models.auth_requests import LoginRequestDTO
from src.domain.models.auth_responses import LoginResponseDTO


class LoginUseCase:
    """
    USE CASE: Log in a user.
    """

    def __init__(
            self,
            auth_adapter: IAuthAdapter,
    ):
        self._auth_adapter = auth_adapter

    async def execute(self, credentials: LoginRequestDTO) -> LoginResponseDTO:
        """
        Executes the login flow.

        Args:
            credentials: User credentials containing email/phone and hashed_password

        Returns:
            LoginResponseDTO containing access and refresh tokens
        """
        return await self._auth_adapter.login(credentials)
