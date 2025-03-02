import re
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated, Optional, TypeVar, Generic
from uuid import UUID

from pydantic import BaseModel, StringConstraints, field_validator, EmailStr, model_validator, Field, ConfigDict


ApiResponseData = TypeVar("ApiResponseData")


class APIResponse(BaseModel, Generic[ApiResponseData]):
    success: bool
    message: str
    content: ApiResponseData
    model_config = ConfigDict(arbitrary_types_allowed=True)



class AddBankCardRequest(BaseModel):
    """
    Pydantic schema for the card information.
    """
    card_holder_first_name: str
    card_holder_last_name: str
    card_number: Annotated[str, StringConstraints(min_length=11, max_length=16)]  # 11-16 digits only. Validator is below.
    expiration_date: str  # MM/YY only. Validator is below.
    cvv_code: Annotated[str, Field(min_length=3, max_length=3)]  # 3 digits only. Validator is below.
    user_id: Annotated[UUID, Field(description="Unique identifier of the user.")]

    @property
    def expiration_month(self) -> int | None:
        """Returns the expiration month as an integer."""
        match = re.match(r"^(0[1-9]|1[0-2])/\d{2}$", self.expiration_date)
        if match:
            return int(match[1])
        return None

    @property
    def expiration_year(self) -> int | None:
        """Returns the expiration year as a full 4-digit integer (e.g., 2024)."""
        match = re.match(r"^(0[1-9]|1[0-2])/(\d{2})$", self.expiration_date)
        if match:
            year_short = int(match[2])
            return 2000 + year_short
        return None

    @field_validator("expiration_date")
    @classmethod
    def validate_expiration(cls, v):
        match = re.match(r"^(0[1-9]|1[0-2])/(\d{2})$", v)
        if not match:
            raise ValueError("Invalid expiration date format. Use MM/YY instead.")

        month, year = int(match[1]), int(match[2])

        full_year = 2000 + year

        exp_date = date(full_year, month, 1)
        if exp_date < date.today():
            raise ValueError("Expiration date must be in the future.")

        return v

    @field_validator("card_number")
    @classmethod
    def validate_card_number(cls, value: str) -> str:
        if not re.fullmatch(r"\d+", value):
            raise ValueError("Card number must contain only digits.")
        return value

    @field_validator("cvv_code")
    @classmethod
    def validate_cvv(cls, value: str) -> str:
        if not re.fullmatch(r"\d{3}", value):
            raise ValueError("CVV code must contain exactly 3 digits.")
        return value


class AddBankCardResponse(BaseModel):
    """
    Pydantic response schema for the bank card addition.
    """
    id: Annotated[UUID, Field(description="Unique identifier of the payment method.")]
    card_holder_first_name: Annotated[str, Field(description="First name of the card holder.")]
    card_holder_last_name: Annotated[str, Field(description="Last name of the card holder.")]
    card_last_four: Annotated[
        str, Field(min_length=4, max_length=4, description="Last four digits of the card number.")
    ]
    expiration_date: Annotated[str, Field(description="Expiration date of the card in format MM/YY.")]
    payment_token: Annotated[str, Field(description="Payment token for the card.")]
    balance: Annotated[Decimal, Field(description="Current balance of the card.")]
    user_id: Annotated[UUID, Field(description="Unique identifier of the user.")]
    created_at: Annotated[datetime, Field(description="Date of the payment method creation.")]
    updated_at: Annotated[datetime, Field(description="Date of the payment method last update.")]


class AddBankAccountRequest(BaseModel):
    """
    Pydantic schema for the bank account information.
    """
    account_holder_name: Annotated[
        str,
        Field(min_length=1, description="Name of the account holder. Cannot be empty.")
    ]
    account_number: Annotated[
        str,
        Field(min_length=20, max_length=20, description="Account number in IBAN format. Must start with 'KZ' followed by 18 digits.")
    ]
    company_id: Annotated[UUID, Field(description="Unique identifier of the company.")]

    @field_validator("account_holder_name", "account_number")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        """
        Validates that the field is not empty or consists only of spaces.
        """
        if not value.strip():
            raise ValueError("Field cannot be empty or consist only of spaces.")
        return value

    @field_validator("account_number")
    @classmethod
    def validate_account_number_format(cls, value: str) -> str:
        """
        Validates that the account number is in a valid Kazakhstan IBAN format:
        It must start with 'KZ' followed by exactly 18 digits.
        """
        if not re.fullmatch(r"^KZ\d{18}$", value):
            raise ValueError("Account number must be a valid Kazakhstan IBAN (e.g., 'KZ' followed by 18 digits).")
        return value


class AddBankAccountResponse(BaseModel):
    """
    Pydantic response schema for the bank account addition.
    """
    id: Annotated[UUID, Field(description="Unique identifier of the payment method.")]
    account_holder_name: Annotated[str, Field(description="Name of the account holder.")]
    account_number: Annotated[str, Field(description="Account number.")]
    bank_name: Annotated[
        Optional[str], Field(default=None, description="Name of the bank (optional field).")
    ]
    bank_bic: Annotated[
        Optional[str], Field(default=None, description="Bank BIC code (optional field).")
    ]
    is_active: Annotated[bool, Field(description="Is the bank account active?")]
    balance: Annotated[Decimal, Field(description="Current balance of the bank account.")]
    company_id: Annotated[UUID, Field(description="Unique identifier of the company.")]
    created_at: Annotated[datetime, Field(description="Date of the bank account creation.")]
    updated_at: Annotated[datetime, Field(description="Date of the bank account last update.")]



class RolesEnum(str, Enum):
    USER = 'user'
    CSS_EMPLOYEE = 'css_employee'
    CSS_ADMIN = 'css_admin'


class RegisterRequestForm(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    password: str
    roles: list[RolesEnum]


class LoginRequestSchema(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    password: str = ...

    @model_validator(mode='before')
    @classmethod
    def check_is_email_or_phone_number_given(cls, values) -> dict:
        """
        Checks that at least one of the identifiers is provided for authorization: email or phone number BEFORE the serialization.
        This method is a '@model_validator' from Pydantic V2.

        Args:
            values (dict): A dictionary containing the raw data from the query. This field is being automatically filled by Pydantic upon HTTP request.
        Returns:
            values (dict): A dictionary of validated data, ready to be used to create a model object.
        Raises:
            ValueError: If the email and phone number both are not provided.
        """
        email = values.get('email')
        phone_number = values.get('phone_number')

        if not email and not phone_number:
            raise ValueError('Either email or phone number must be provided.')

        return values
