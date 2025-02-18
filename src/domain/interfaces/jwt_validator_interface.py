from abc import abstractmethod, ABC
from typing import Literal, Optional, List

from src.presentation.schemas import RolesEnum


class IJwtValidator(ABC):
    @abstractmethod
    def validate_token(
            self,
            token: str,
            required_token_type: Literal['access', 'refresh'],
            required_roles: Optional[List[RolesEnum]] = None
            ) -> dict:
        pass
