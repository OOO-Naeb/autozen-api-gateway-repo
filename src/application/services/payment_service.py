from typing import Annotated, Any, Coroutine

from fastapi import Depends

from src.core.jwt_validator import JWTValidator
from src.domain.schemas import AccessToken, CardInfo, RolesEnum, PaymentToken
from src.infrastructure.adapters.rabbitmq_payment_adapter import RabbitMQPaymentAdapter
from src.infrastructure.interfaces.payment_adapter_interface import IPaymentAdapter


class PaymentService:
    """
    SERVICE: Payment service class. Contains methods for payments processing, such as add new payment method. It's being used instead of the use cases in order to avoid unnecessary decomposition.
    """
    def __init__(
        self,
        payment_service_adapter: Annotated[IPaymentAdapter, Depends(RabbitMQPaymentAdapter)],
        jwt_validator: JWTValidator = Depends(JWTValidator)
    ) -> None:
        self.payment_service_adapter = payment_service_adapter
        self.jwt_validator = jwt_validator

    async def add_payment_method(
        self,
        access_token: AccessToken,
        card_info: CardInfo
    ) -> tuple[int, PaymentToken] | None:
        """
        SERVICE METHOD: Add a payment method to the user's account. Passes the query to the 'RabbitMQPaymentAdapter'.

        Args:
            access_token (AccessToken): The access token to authenticate the user.
            card_info (CardInfo): The card information to add to the user's account.

        Returns:
            dict: A payment token needed for payments processing.
        """
        await self.jwt_validator.validate_jwt_token(
            str(access_token),
            required_token_type='access',
            required_roles=[RolesEnum.USER]  # 'user'
        )

        return await self.payment_service_adapter.add_payment_method(card_info)
