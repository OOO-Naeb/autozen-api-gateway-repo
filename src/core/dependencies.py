from typing import Any, AsyncGenerator

from src.application.use_cases.add_bank_account import AddBankAccountUseCase
from src.application.use_cases.add_bank_card import AddBankCardUseCase
from src.application.use_cases.login import LoginUseCase
from src.application.use_cases.p2b_transaction import ProceedP2BTransactionUseCase
from src.application.use_cases.refresh import RefreshUseCase
from src.application.use_cases.register import RegisterUseCase
from src.core.jwt_validator import JWTValidator
from src.core.logger import LoggerService
from src.infrastructure.adapters.http_payment_adapter import PaymentHttpClient
from src.infrastructure.adapters.rabbitmq_auth_adapter import RabbitMQAuthAdapter

logger = LoggerService(__name__, "api_gateway_log.log")
jwt_validator = JWTValidator()
auth_adapter = RabbitMQAuthAdapter(logger=logger)


async def get_add_bank_card_use_case():
    http_client = PaymentHttpClient(logger=logger, base_url="http://localhost:8003/api/v1/payment")
    use_case = AddBankCardUseCase(http_client, jwt_validator)

    yield use_case


async def get_add_bank_account_use_case() -> AsyncGenerator[AddBankAccountUseCase, Any]:
    http_client = PaymentHttpClient(logger=logger, base_url="http://localhost:8003/api/v1/payment")
    use_case = AddBankAccountUseCase(http_client, jwt_validator)

    yield use_case


async def get_proceed_p2b_transaction_use_case() -> AsyncGenerator[ProceedP2BTransactionUseCase, Any]:
    http_client = PaymentHttpClient(logger=logger, base_url="http://localhost:8003/api/v1/payment")
    use_case = ProceedP2BTransactionUseCase(http_client, jwt_validator)

    yield use_case


async def get_login_use_case():
    return LoginUseCase(auth_adapter=auth_adapter)


async def get_refresh_use_case():
    return RefreshUseCase(auth_adapter=auth_adapter)


async def get_register_use_case():
    return RegisterUseCase(auth_adapter=auth_adapter)
