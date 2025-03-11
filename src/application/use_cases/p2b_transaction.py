from src.domain.interfaces.http_payment_adapter_interface import IHttpPaymentAdapter
from src.domain.interfaces.jwt_validator_interface import IJwtValidator
from src.domain.models.payment_requests import P2BTransactionDTO
from src.domain.models.payment_responses import P2BTransactionResponseDTO
from src.presentation.schemas import RolesEnum


class ProceedP2BTransactionUseCase:
    """
    USE CASE: Proceed a p2b (bank card -> bank account) transaction
    via the Payment Service.
    """
    def __init__(
            self,
            http_payment_adapter: IHttpPaymentAdapter,
            jwt_validator: IJwtValidator
    ):
        self._jwt_validator = jwt_validator
        self._http_payment_adapter = http_payment_adapter

    async def execute(self, domain_schema_data: P2BTransactionDTO, access_token: str, payment_token: str) -> P2BTransactionResponseDTO:
        self._jwt_validator.validate_token(
            access_token,
            required_token_type='access',
            required_roles=[RolesEnum.USER]  # 'user'
        )

        return await self._http_payment_adapter.post(
            endpoint='p2b_transfer',
            payload=domain_schema_data.to_dict(),
            response_model=P2BTransactionResponseDTO,
            headers={"X-Payment-Token": payment_token}
        )

