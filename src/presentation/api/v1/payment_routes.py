from typing import Annotated

from fastapi import APIRouter, Body, Depends

from src.application.use_cases.add_bank_account import AddBankAccountUseCase
from src.application.use_cases.add_bank_card import AddBankCardUseCase
from src.core.dependencies import get_add_bank_card_use_case, get_add_bank_account_use_case
from src.domain.models.payment_requests import AddBankCardDTO, AddBankAccountDTO
from src.domain.oauth_schemas import oauth2_token_schema
from src.presentation.schemas import AddBankCardRequest, AddBankAccountRequest, AddBankCardResponse, \
    AddBankAccountResponse, APIResponse

payment_router = APIRouter(
    tags=["Payment"],
    prefix="/api/v1/payment",
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
        access_token (str): The access token to authenticate the user.
        card_info (AddBankCardRequest): The card information to add to the user's account.
        use_case (AddBankCardUseCase): The payment use_case to process the operation.

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
        access_token (AccessToken): The access token to authenticate the user.
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
