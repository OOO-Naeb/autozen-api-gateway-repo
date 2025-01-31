from abc import abstractmethod, ABC

from src.domain.schemas import LoginRequestForm, Tokens, RegisterRequestForm


class IAuthAdapter(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def rpc_call(self, routing_key: str, body: dict, timeout: int) -> tuple[int, dict] | None:
        pass

    @abstractmethod
    async def login(self, data: LoginRequestForm) -> Tokens:
        pass

    @abstractmethod
    async def refresh(self, refresh_token_payload: dict) -> Tokens:
        pass

    @abstractmethod
    async def register(self, data: RegisterRequestForm):
        pass
