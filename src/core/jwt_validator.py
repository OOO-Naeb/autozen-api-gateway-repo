from typing import Literal

import jwt

from src.core.config import settings
from src.domain.exceptions import UnauthorizedException


class JWTValidator:
    def __init__(self):
        self.public_key = settings.JWT_PUBLIC_SECRET_KEY

    async def validate_jwt_token(self, token: str, required_token_type: Literal['access', 'refresh']) -> dict:
        """
        Validates both types of tokens ('access', 'refresh') based on given token type.
        Decodes a token and compares its type inside with given one.

        Args:
            token (str): The token to validate.
            required_token_type (Literal['access', 'refresh']): The token type to compare.

        Returns:
            dict: The decoded token payload.

        Raises:
            UnauthorizedException: If the token type inside doesn't match the given type, if the token is invalid or expired.
        """
        try:
            payload = jwt.decode(token, self.public_key, algorithms=[settings.JWT_ALGORITHM], leeway=10)
            if payload['token_type'] != required_token_type:
                raise UnauthorizedException()

            return payload
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException()
        except jwt.InvalidTokenError:
            raise UnauthorizedException()
