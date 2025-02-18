from src.domain.interfaces.auth_adapter_interface import IAuthAdapter
from src.domain.models.auth_requests import RefreshTokenRequestDTO
from src.domain.models.auth_responses import RefreshTokenResponseDTO


class RefreshUseCase:
    """
    USE CASE: Refresh the access token using the refresh token.
    """
    def __init__(
            self,
            auth_adapter: IAuthAdapter,
    ):
        self._auth_adapter = auth_adapter

    async def execute(self, refresh_token_payload: RefreshTokenRequestDTO) -> RefreshTokenResponseDTO:
        """
        Executes the refresh flow.

        Args:
            refresh_token_payload (RefreshTokenRequestDTO): Refresh token payload.

        Returns:
            RefreshTokenResponseDTO domain schema containing access and refresh tokens.
        """
        return await self._auth_adapter.refresh(refresh_token_payload)
