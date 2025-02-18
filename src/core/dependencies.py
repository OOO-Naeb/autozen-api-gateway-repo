from src.application.use_cases.add_bank_card import AddBankCardUseCase
from src.application.use_cases.login import LoginUseCase
from src.application.use_cases.refresh import RefreshUseCase
from src.application.use_cases.register import RegisterUseCase
from src.core.jwt_validator import JWTValidator
from src.core.logger import LoggerService
from src.infrastructure.adapters.rabbitmq_auth_adapter import RabbitMQAuthAdapter
from src.infrastructure.adapters.rabbitmq_payment_adapter import RabbitMQPaymentAdapter

logger = LoggerService(__name__, "api_gateway_log.log")
jwt_validator = JWTValidator()


def get_add_bank_card_use_case():
    payment_adapter = RabbitMQPaymentAdapter(logger=logger)
    return AddBankCardUseCase(payment_adapter, jwt_validator)


auth_adapter = RabbitMQAuthAdapter(logger=logger)


async def get_login_use_case():
    return LoginUseCase(auth_adapter=auth_adapter)


async def get_refresh_use_case():
    return RefreshUseCase(auth_adapter=auth_adapter)


async def get_register_use_case():
    return RegisterUseCase(auth_adapter=auth_adapter)
