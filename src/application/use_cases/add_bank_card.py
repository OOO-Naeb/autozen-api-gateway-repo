import datetime
import uuid

from src.domain.exceptions import CardValidationError
from src.domain.interfaces.jwt_validator_interface import IJwtValidator
from src.domain.interfaces.payment_adapter_interface import IPaymentAdapter
from src.domain.models.payment_methods import CardPaymentMethod
from src.domain.models.payment_token import PaymentTokenResponse
from src.presentation.schemas import CardInfo, RolesEnum


class AddBankCardUseCase:
    """
    USE CASE: Create a new payment method (bank card) and get a token from the payment gateway (bank API)
    via the Payment Service.
    """

    def __init__(self, payment_adapter: IPaymentAdapter, jwt_validator: IJwtValidator) -> None:
        self._payment_adapter = payment_adapter
        self._jwt_validator = jwt_validator

    async def execute(self, raw_data: CardInfo, access_token: str) -> PaymentTokenResponse:
        self._jwt_validator.validate_token(
            access_token,
            required_token_type='access',
            required_roles=[RolesEnum.USER]  # 'user'
        )

        bank_card = self._to_card_domain(raw_data)  # Convert the card info to the domain model
        self._validate_card(bank_card)  # Validate the bank card

        return await self._payment_adapter.add_bank_card(bank_card)

    @staticmethod
    def _to_card_domain(card_info: CardInfo) -> CardPaymentMethod:
        current_time = datetime.datetime.now(datetime.UTC)

        return CardPaymentMethod(
            id=uuid.uuid4(),
            card_holder_first_name=card_info.card_holder_first_name,
            card_holder_last_name=card_info.card_holder_last_name,
            card_number=card_info.card_number,
            expiration_month=card_info.expiration_month,
            expiration_year=card_info.expiration_year,
            created_at=current_time,
            updated_at=current_time
        )

    @staticmethod
    def _validate_card(card: CardPaymentMethod) -> None:
        """Validate the bank card before creation."""
        if not card.can_be_used_for_payment():
            raise CardValidationError("This bank card cannot be used for payment.")
