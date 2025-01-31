from abc import ABC, abstractmethod

from src.domain.schemas import PaymentToken


class IPaymentAdapter(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def rpc_call(self) -> tuple[int, dict] | None:
        pass

    @abstractmethod
    async def get_payment_token(self) -> PaymentToken:
        pass
