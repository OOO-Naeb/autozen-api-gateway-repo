from abc import abstractmethod, ABC
from typing import Annotated

from fastapi import Depends

from src.core.oauth_schemas import oauth2_token_schema
from src.domain.schemas import LoginRequestForm, RefreshToken, Tokens, RegisterRequestForm


class IAuthAdapter(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def rpc_call(self, routing_key: str, body: dict, timeout: int):
        pass

    @abstractmethod
    async def login(self, data: LoginRequestForm) -> Tokens:
        pass

    @abstractmethod
    async def refresh(self, refresh_token: Annotated[RefreshToken, Depends(oauth2_token_schema)]) -> Tokens:
        pass

    @abstractmethod
    async def register(self, data: RegisterRequestForm):
        pass
