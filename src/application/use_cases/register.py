from src.core.logger import LoggerService
from src.domain.interfaces.auth_adapter_interface import IAuthAdapter
from src.domain.models.auth_requests import RegisterRequestDTO
from src.domain.models.auth_responses import RegisterResponseDTO


class RegisterUseCase:
    """
    USE CASE: Register a user and return their data.
    """

    def __init__(
            self,
            auth_adapter: IAuthAdapter,
    ):
        self._auth_adapter = auth_adapter

    async def execute(self, user_data: RegisterRequestDTO) -> RegisterResponseDTO:
        """
        Executes the register flow.

        Args:
            user_data (RegisterRequestDTO): User's data to register.

        Returns:
            RegisterResponseDTO: created user's data.
        """
        return await self._auth_adapter.register(user_data)
