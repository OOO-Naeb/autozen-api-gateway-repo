from dataclasses import dataclass
from datetime import datetime, date
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from uuid import UUID


class PaymentMethod(ABC):
    id: Optional[UUID] = None
    is_active: bool = True

    created_at: datetime = None
    updated_at: datetime = None

    @abstractmethod
    def can_be_used_for_payment(self) -> bool:
        """Check if the payment method can be used for payment."""
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """Convert the domain object to a dictionary."""
        pass

    def convert_datetime_fields_to_str(self, data: Any) -> Any:
        """
        Convert datetime/date fields to strings in the given data.
        """
        if isinstance(data, (datetime, date)):
            return data.isoformat()
        elif isinstance(data, dict):
            return {key: self.convert_datetime_fields_to_str(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.convert_datetime_fields_to_str(item) for item in data]
        else:
            return data

    def to_serializable_dict(self) -> Dict[str, Any]:
        """
        Convert the domain object to a dictionary with datetime/date fields converted to strings.
        """
        raw_dict = self.to_dict()

        return self.convert_datetime_fields_to_str(raw_dict)


@dataclass
class CardPaymentMethod(PaymentMethod):
    card_holder_first_name: str = ""
    card_holder_last_name: str = ""
    card_number: str = ""
    expiration_month: int = 0
    expiration_year: int = 0
    payment_token: str = ""

    id: Optional[UUID] = None

    @property
    def card_holder_full_name(self) -> str:
        return f"{self.card_holder_first_name} {self.card_holder_last_name}"

    def is_expired(self) -> bool:
        today = date.today()
        exp_date = date(self.expiration_year, self.expiration_month, 1)
        return exp_date < today

    def can_be_used_for_payment(self) -> bool:
        return not self.is_expired()

    def to_dict(self) -> dict:
        """Convert the domain object to a dictionary."""
        return dict(
            card_holder_first_name=self.card_holder_first_name,
            card_holder_last_name=self.card_holder_last_name,
            card_number=self.card_number,
            expiration_month=self.expiration_month,
            expiration_year=self.expiration_year,
            payment_token=self.payment_token,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at
        )


@dataclass
class BankAccountPaymentMethod(PaymentMethod):
    account_holder_name: str = ""
    account_number: str = ""
    bank_name: str = ""
    bank_bic: str = ""

    def can_be_used_for_payment(self) -> bool:
        # Credentials validation logic goes here
        return self.is_active

    def to_dict(self) -> dict:
        return dict(
            account_holder_name=self.account_holder_name,
            account_number=self.account_number,
            bank_name=self.bank_name,
            bank_bic=self.bank_bic,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
