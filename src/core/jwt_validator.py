from typing import Literal, Optional, List

import jwt

from src.core.config import settings
from src.domain.exceptions import UnauthorizedException, AccessDeniedException
from src.domain.schemas import RolesEnum


class JWTValidator:
    def __init__(self):
        self.public_key = settings.JWT_PUBLIC_SECRET_KEY

    async def validate_jwt_token(
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
                raise UnauthorizedException()

            if required_roles:
                for role in required_roles:
                    if role.value not in payload['roles']:
                        raise AccessDeniedException()

            return payload

        except jwt.InvalidSignatureError:
            raise UnauthorizedException()
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException()
        except jwt.InvalidTokenError as e:
            raise e
