from datetime import datetime, date
from dataclasses import dataclass
from typing import Optional, Any, Dict
from uuid import UUID


@dataclass
class PaymentTokenResponse:
    """
    Domain model for payment token response. Payment token is being returned
    by the payment gateway (in the Payment Service) after a successful payment method registration.
    """
    payment_token: str
    card_type: str
    expiration_month: int
    expiration_year: int

    created_at: datetime = None
    updated_at: datetime = None

    id: Optional[UUID] = None

    def to_dict(self) -> dict:
        """ Convert the domain object to a dictionary. """
        return {
            "id": self.id,
            "payment_token": self.payment_token,
            "card_type": self.card_type,
            "expiration_month": self.expiration_month,
            "expiration_year": self.expiration_year,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def convert_datetime_fields_to_str(self, data: Any) -> Any:
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
