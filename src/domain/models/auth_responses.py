from dataclasses import dataclass
from typing import Optional

from src.domain.interfaces.auth_dto_interfaces import IAuthResponseDTO
from src.presentation.schemas import RolesEnum


@dataclass(frozen=True)
class JwtTokensResponseDTO(IAuthResponseDTO):
    """
    Domain schema for JWT Tokens Response.
    Represents the data returned after successful JWT token generation.
    """
    access_token: str = ""
    refresh_token: str = ""

    def to_dict(self) -> dict:
        """Convert the domain object to a dictionary."""
        base_dict = dict(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
        )

        return base_dict


@dataclass(frozen=True)
class LoginResponseDTO(JwtTokensResponseDTO):
    """
    Domain schema for Login Response.
    Represents the data returned after successful user login.
    """
    def to_dict(self) -> dict:
        """Convert the domain object to a dictionary."""
        base_dict = dict(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
        )

        return base_dict


@dataclass(frozen=True)
class RegisterResponseDTO(IAuthResponseDTO):
    """
    Domain schema for Register Response.
    Represents the data returned after successful user registration.
    """
    first_name: str
    last_name: str

    email: Optional[str] = None
    phone_number: Optional[str] = None
    roles: list[RolesEnum] = None

    def to_dict(self) -> dict:
        """Convert the domain object to a dictionary."""
        base_dict = dict(
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            phone_number=self.phone_number,
            roles=[role.value for role in self.roles],
        )

        return base_dict


@dataclass(frozen=True)
class RefreshTokenResponseDTO(JwtTokensResponseDTO):
    """
    Domain schema for Refresh Token Response.
    Represents the data returned after successful refresh token operation.
    """
    def to_dict(self) -> dict:
        """Convert the domain object to a dictionary."""
        base_dict = dict(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
        )

        return base_dict
