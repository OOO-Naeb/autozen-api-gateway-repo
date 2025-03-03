from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional, TypeVar, Union
from uuid import UUID, uuid4


@dataclass
class AddBankCardResponseDTO:
    """
    Domain model for the response from the Payment Service when adding a bank card.
    """
    user_id: UUID
    is_active: bool
    card_holder_first_name: str
    card_holder_last_name: str
    card_last_four: str # Exactly 4 digits
    expiration_date: str  # Format: MM/YY
    payment_token: str
    balance: Decimal = Decimal("0.00")
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    id: UUID = field(default_factory=uuid4)

    def to_dict(self) -> dict:
        """
        Convert the domain DTO object to a dictionary.
        """
        return dict(
            id=self.id,
            card_holder_first_name=self.card_holder_first_name,
            card_holder_last_name=self.card_holder_last_name,
            card_last_four=self.card_last_four,
            expiration_date=self.expiration_date,
            payment_token=self.payment_token,
            balance=self.balance,
            user_id=str(self.user_id),
            created_at=self.created_at,
            updated_at=self.updated_at
        )


@dataclass
class AddBankAccountResponseDTO:
    """
    Domain DTO for the response from the Payment Service when adding a bank account.
    """
    company_id: UUID
    id: UUID = field(default_factory=uuid4)
    account_holder_name: str = ""
    account_number: str = ""
    bank_name: Optional[str] = None
    bank_bic: Optional[str] = None
    is_active: bool = True
    balance: Decimal = Decimal("0.00")
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """
        Convert the domain DTO object to a dictionary.
        """
        return dict(
            id=self.id,
            account_holder_name=self.account_holder_name,
            account_number=self.account_number,
            bank_name=self.bank_name,
            bank_bic=self.bank_bic,
            is_active=self.is_active,
            balance=self.balance,
            company_id=str(self.company_id),
            created_at=self.created_at,
            updated_at=self.updated_at
        )


PaymentServiceResponseDTO = TypeVar("PaymentServiceResponseDTO", bound=Union[AddBankAccountResponseDTO, AddBankCardResponseDTO])  # TODO: Add more response DTOs in the future
