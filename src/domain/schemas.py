import re
from datetime import date
from enum import Enum
from typing import Optional, Annotated

from pydantic import BaseModel, EmailStr, model_validator, constr, field_validator, StringConstraints


class User(BaseModel):
    first_name: str
    last_name: str
    middle_name: str
    password: str


class RoleEnum(str, Enum):
    CSS_EMPLOYEE = 'css_employee'
    CSS_ADMIN = 'css_admin'
    USER = 'user'


class UserFromDB(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: str
    email: EmailStr
    phone_number: str
    role: RoleEnum


class UserToDB(BaseModel):
    first_name: str
    last_name: str
    middle_name: str
    email: EmailStr
    phone_number: str
    password: str
    role: RoleEnum

class AccessToken(BaseModel):
    access_token: str


class RefreshToken(BaseModel):
    refresh_token: str


class Tokens(AccessToken, RefreshToken):
    pass


class PaymentToken(BaseModel):
    payment_token: str


class CardInfo(BaseModel):
    card_holder_first_name: str
    card_holder_last_name: str
    card_number: Annotated[str, StringConstraints(min_length=11, max_length=11)]
    expiration_date: Annotated[str, StringConstraints(pattern=r"^(0[1-9]|1[0-2])\/\d{2}$")]
    cvv_code: Annotated[str, StringConstraints(min_length=3, max_length=3)]

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
            raise ValueError("Expiration date must be in the future")

        return v


class RegisterRequestForm(BaseModel):
    first_name: str
    last_name: str
    middle_name: str
    email: EmailStr
    phone_number: str
    password: str
    role: RoleEnum


class LoginRequestForm(BaseModel):
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
