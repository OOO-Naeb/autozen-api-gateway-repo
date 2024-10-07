from typing import List

from pydantic import BaseModel

class User(BaseModel):
    first_name: str
    last_name: str
    middle_name: str

class AccessToken(BaseModel):
    access_token: str
    token_type: str = "Bearer"

class RefreshToken(BaseModel):
    refresh_token: str

class Tokens(AccessToken, RefreshToken):
    pass

class TokenData(BaseModel):
    email: str
    roles: List[str] = []

class RegisterRequestForm(BaseModel):
    first_name: str
    last_name: str
    middle_name: str
    phone_number: str
    password: str
    role: str
