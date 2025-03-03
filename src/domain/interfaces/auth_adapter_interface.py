from abc import abstractmethod, ABC

from src.domain.models.auth_requests import LoginRequestDTO, RegisterRequestDTO, RefreshTokenRequestDTO
from src.domain.models.auth_responses import LoginResponseDTO, RegisterResponseDTO, RefreshTokenResponseDTO
from src.domain.models.rabbitmq_response import RabbitMQResponse


class IAuthAdapter(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def _make_rpc_call(self, routing_key: str, body: dict, timeout: int) -> RabbitMQResponse | None:
        pass

    @abstractmethod
    async def login(self, data: LoginRequestDTO) -> LoginResponseDTO:
        pass

    @abstractmethod
    async def refresh(self, refresh_token_payload: RefreshTokenRequestDTO) -> RefreshTokenResponseDTO:
        pass

    @abstractmethod
    async def register(self, data: RegisterRequestDTO) -> RegisterResponseDTO:
        pass
