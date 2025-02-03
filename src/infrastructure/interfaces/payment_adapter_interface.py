from abc import ABC, abstractmethod

from src.domain.schemas import PaymentToken, CardInfo


class IPaymentAdapter(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def rpc_call(self, operation_type: str, routing_key: str, body: dict, timeout: int = 5) -> tuple[int, dict] | None:
        pass

    @abstractmethod
    async def add_payment_method(self, card_info: CardInfo) -> tuple[int, PaymentToken] | None:
        pass
