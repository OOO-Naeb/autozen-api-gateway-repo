import re
from dataclasses import dataclass
from datetime import date
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class AddBankCardDTO:
    """
    Domain DTO schema for adding a bank card to the user's account.
    """
    user_id: UUID
    card_holder_first_name: str
    card_holder_last_name: str
    card_number: str  # 11-16 digits
    expiration_date: str  # MM/YY
    cvv_code: str  # 3 digit

    def __post_init__(self) -> None:
        match = re.match(r"^(0[1-9]|1[0-2])/(\d{2})$", self.expiration_date)
        if not match:
            raise ValueError("Invalid expiration date format. Use MM/YY instead.")
        month, year = int(match.group(1)), int(match.group(2))
        full_year = 2000 + year
        exp_date = date(full_year, month, 1)
        if exp_date < date.today():
            raise ValueError("Expiration date must be in the future.")

    @property
    def expiration_month(self) -> Optional[int]:
        """
        Returns the expiration month as an integer.
        """
        match = re.match(r"^(0[1-9]|1[0-2])/\d{2}$", self.expiration_date)
        if match:
            return int(match.group(1))
        return None

    @property
    def expiration_year(self) -> Optional[int]:
        """
        Returns the expiration year as a full 4-digit integer (e.g., 2024).
        """
        match = re.match(r"^(0[1-9]|1[0-2])/(\d{2})$", self.expiration_date)
        if match:
            year_short = int(match.group(2))
            return 2000 + year_short
        return None

    def to_dict(self) -> dict:
        """
        Convert the domain DTO object to a dictionary.
        """
        return dict(
            user_id=str(self.user_id),
            card_holder_first_name=self.card_holder_first_name,
            card_holder_last_name=self.card_holder_last_name,
            card_number=self.card_number,
            expiration_date=self.expiration_date,
            cvv_code=self.cvv_code
        )


@dataclass
class AddBankAccountDTO:
    """
    Domain DTO schema for adding a bank account to the company's account.
    """
    account_holder_name: str
    account_number: str
    company_id: UUID

    def __post_init__(self) -> None:
        if not self.account_holder_name.strip():
            raise ValueError("account_holder_name cannot be empty or consist only of spaces.")
        if not self.account_number.strip():
            raise ValueError("account_number cannot be empty or consist only of spaces.")

    def to_dict(self) -> dict:
        """
        Convert the domain DTO object to a dictionary.
        """
        return dict(
            account_holder_name=self.account_holder_name,
            account_number=self.account_number,
            company_id= str(self.company_id)
        )

