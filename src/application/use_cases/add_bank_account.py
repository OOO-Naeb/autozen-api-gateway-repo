from src.domain.interfaces.http_payment_adapter_interface import IHttpPaymentAdapter
from src.domain.interfaces.jwt_validator_interface import IJwtValidator
from src.domain.models.payment_requests import AddBankAccountDTO
from src.domain.models.payment_responses import AddBankAccountResponseDTO
from src.presentation.schemas import RolesEnum


class AddBankAccountUseCase:
    """
    USE CASE: Create a new payment method (bank account).
    via the Payment Service.
    """

    def __init__(self, http_payment_adapter: IHttpPaymentAdapter, jwt_validator: IJwtValidator) -> None:
        self._jwt_validator = jwt_validator
        self._http_payment_adapter = http_payment_adapter

    async def execute(self, domain_schema_data: AddBankAccountDTO, access_token: str) -> AddBankAccountResponseDTO:
        self._jwt_validator.validate_token(
            access_token,
            required_token_type='access',
            required_roles=[RolesEnum.CSS_ADMIN]  # 'css_admin'
        )

        return await self._http_payment_adapter.post(
            endpoint="bank_account",
            payload=domain_schema_data.to_dict(),
            response_model=AddBankAccountResponseDTO
        )
