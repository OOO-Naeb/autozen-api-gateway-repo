from typing import Annotated

from fastapi import APIRouter, Body, Depends, Header

from src.application.use_cases.add_bank_account import AddBankAccountUseCase
from src.application.use_cases.add_bank_card import AddBankCardUseCase
from src.application.use_cases.p2b_transaction import ProceedP2BTransactionUseCase
from src.core.dependencies import get_add_bank_card_use_case, get_add_bank_account_use_case, \
    get_proceed_p2b_transaction_use_case
from src.domain.models.payment_requests import AddBankCardDTO, AddBankAccountDTO, P2BTransactionDTO
from src.domain.oauth_schemas import oauth2_token_schema
from src.presentation.schemas import AddBankCardRequest, AddBankAccountRequest, AddBankCardResponse, \
    AddBankAccountResponse, APIResponse, P2BTransactionRequest, P2BTransactionResponse

payment_router = APIRouter(
    tags=["Payment API"],
    prefix="/api/v1/payment",
)


@payment_router.post('/p2b_transfer', response_model=APIResponse[P2BTransactionResponse], status_code=201)
async def p2b_transfer(
        access_token: Annotated[str, Depends(oauth2_token_schema)],
        payment_token: Annotated[str, Header(convert_underscores=False, title="X-Payment-Token")],
        use_case: Annotated[ProceedP2BTransactionUseCase, Depends(get_proceed_p2b_transaction_use_case)],
        p2b_transaction_data: P2BTransactionRequest
) -> APIResponse[P2BTransactionResponse]:
    """
    CONTROLLER: Make a transfer from a bank card (via previously received payment token) to the
    bank account.

    Args:
        access_token (str): The access token to authorize the user.
        payment_token (str): The payment token to authorize the bank card.
        use_case (P2BTransferUseCase): The use case to make a transfer.
        p2b_transaction_data (P2BTransactionRequest): The Pydantic-schema which contains:
            1. bank_account_number (str): The bank account number to transfer the payment.
            2. amount (Decimal): The amount of money to transfer.
    """
    p2b_transaction_data_dict = p2b_transaction_data.model_dump()

    p2b_transaction_domain_dto = P2BTransactionDTO(
        **p2b_transaction_data_dict
    )
    print("Received a message:", p2b_transaction_domain_dto)  # TODO: For debug only. Remove later.
    response = await use_case.execute(p2b_transaction_domain_dto, access_token, payment_token)

    return APIResponse(
        success=True,
        messsage='Transaction was successful.',
        content={
            **response.to_dict()
        }
    )


@payment_router.post('/bank_card', response_model=APIResponse[AddBankCardResponse], status_code=201)
async def add_bank_card(
        access_token: Annotated[str, Depends(oauth2_token_schema)],
        card_info: Annotated[AddBankCardRequest, Body(...)],
        use_case: Annotated[AddBankCardUseCase, Depends(get_add_bank_card_use_case)]
) -> APIResponse[AddBankCardResponse]:
    """
    CONTROLLER: Add a payment method to the user's account. Passes the query to the 'AddBankCardUseCase'.

    Args:
        access_token (str): The access token to authorize the user.
        card_info (AddBankCardRequest): The card information to add to the user's account.
        use_case (AddBankCardUseCase): The payment use case to process the operation.

    Returns:
        APIResponse: A response schema containing status code, message and bank response.
    """
    bank_card_domain_dto = AddBankCardDTO(**card_info.model_dump())
    print("Received a message: ", bank_card_domain_dto)
    response = await use_case.execute(bank_card_domain_dto, access_token)

    return APIResponse(
        success=True,
        message='Payment method added successfully.',
        content={
            **response.to_dict()
        }
    )


@payment_router.post('/bank_account', response_model=APIResponse[AddBankAccountResponse], status_code=201)
async def add_bank_account(
        access_token: Annotated[str, Depends(oauth2_token_schema)],
        bank_account_info: Annotated[AddBankAccountRequest, Body(...)],
        use_case: Annotated[AddBankAccountUseCase, Depends(get_add_bank_account_use_case)]
) -> APIResponse[AddBankAccountResponse]:
    """
    CONTROLLER: Add a payment method to the company's account. Passes the query to the 'PaymentUseCase'.

    Args:
        access_token (AccessToken): The access token to authorize the user.
        bank_account_info (AddBankCardRequest): The bank account information to add to the company's account.
        use_case (AddBankAccountUseCase): The payment use case to process the operation.

    Returns:
        APIResponse: A response schema containing status code, message and bank response.
    """
    bank_account_domain_dto = AddBankAccountDTO(**bank_account_info.model_dump())
    response = await use_case.execute(bank_account_domain_dto, access_token)

    return APIResponse(
        success=True,
        message='Payment method added successfully.',
        content={
            **response.to_dict()
        }
    )
