from abc import ABC, abstractmethod
from typing import Dict, Any

from src.domain.models.payment_methods import CardPaymentMethod
from src.domain.models.payment_token import PaymentTokenResponse


class IPaymentAdapter(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def _make_rpc_call(self, operation_type: str, payload: Dict[str, Any], timeout: int = 5) -> tuple[int, dict] | None:
        pass

    @abstractmethod
    async def add_bank_card(self, card: CardPaymentMethod) -> PaymentTokenResponse | None:
        pass

    # @abstractmethod
    # async def add_bank_account(self, bank_account_info: BankAccountInfo) -> tuple[int, dict] | None:
    #     pass
