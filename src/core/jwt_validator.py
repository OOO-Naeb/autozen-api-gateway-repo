from typing import Literal, Optional, List

import jwt

from src.core.config import settings
from src.core.exceptions import ApiGatewayError
from src.domain.interfaces.jwt_validator_interface import IJwtValidator
from src.presentation.schemas import RolesEnum


class JWTValidator(IJwtValidator):
    def __init__(self):
        self.public_key = settings.JWT_PUBLIC_SECRET_KEY

    def validate_token(
            self,
            token: str,
            required_token_type: Literal['access', 'refresh'],
            required_roles: Optional[List[RolesEnum]] = None
    ) -> dict:
        """
        Validates both types of tokens ('access', 'refresh') based on given token type.
        Decodes a token and compares its type, roles (Optional. Only if roles are given.) inside with given one.

        Args:
            token (str): The token to validate.
            required_token_type (Literal['access', 'refresh']): The token type to compare.
            required_roles (Optional[List['user', 'css_employee', 'css_admin']]): The required roles to compare. Parameter is optional. If nothing is given, it will be ignored.

        Returns:
            dict: The decoded token payload.

        Raises:
            UnauthorizedException: If the token type inside doesn't match the given type, if the token is invalid or expired.
        """
        try:
            payload = jwt.decode(token, self.public_key, algorithms=[settings.JWT_ALGORITHM], leeway=10)
            if payload['token_type'] != required_token_type:
                raise ApiGatewayError(
                    status_code=401,
                    detail="Invalid token."
                )

            if required_roles:
                for role in required_roles:
                    if role.value not in payload['roles']:
                        raise ApiGatewayError(
                            status_code=403,
                            detail="You don't have permission to access this resource."
                        )

            return payload

        except jwt.InvalidSignatureError:
            raise ApiGatewayError(
                status_code=401,
                detail="Invalid token signature."
            )
        except jwt.ExpiredSignatureError:
            raise ApiGatewayError(
                status_code=401,
                detail="Expired token signature."
            )
        except jwt.InvalidTokenError:
            raise ApiGatewayError(
                status_code=401,
                detail="Invalid token."
            )
