from typing import Annotated

from fastapi import APIRouter, Body, Depends
from starlette.responses import JSONResponse

from src.application.use_cases.add_bank_card import AddBankCardUseCase
from src.core.dependencies import get_add_bank_card_use_case
from src.domain.oauth_schemas import oauth2_token_schema
from src.presentation.schemas import CardInfo

payment_router = APIRouter(
    tags=["Payment"],
    prefix="/api/v1/payment",
)


@payment_router.post('/bank_card')
async def add_bank_card(
        access_token: Annotated[str, Depends(oauth2_token_schema)],
        card_info: Annotated[CardInfo, Body(...)],
        use_case: Annotated[AddBankCardUseCase, Depends(get_add_bank_card_use_case)]
) -> JSONResponse:
    """
    CONTROLLER: Add a payment method to the user's account. Passes the query to the 'AddBankCardUseCase'.

    Args:
        access_token (str): The access token to authenticate the user.
        card_info (CardInfo): The card information to add to the user's account.
        use_case (AddBankCardUseCase): The payment use_case to process the operation.

    Returns:
        JSONResponse: A JSON response containing status code, message and payment token.
    """
    response = await use_case.execute(card_info, str(access_token))

    return JSONResponse(
        status_code=201,
        content={
            'success': True,
            'message': 'Payment method added successfully.',
            'bank_response': {
                **response.to_dict()
            },
        },
    )


# @payment_router.post('/bank_account', response_model=PaymentTokenResponse)
# async def add_bank_account(
#         access_token: Annotated[AccessToken, Depends(oauth2_token_schema)],
#         card_info: Annotated[CardInfo, Body(...)],
#         payment_service: Annotated[PaymentService, Depends(PaymentService)]
# ) -> JSONResponse:
#     """
#     CONTROLLER: Add a payment method to the user's account. Passes the query to the 'PaymentUseCase'.
#
#     Args:
#         access_token (AccessToken): The access token to authenticate the user.
#         card_info (CardInfo): The card information to add to the user's account.
#         payment_service (PaymentService): The payment service to process the payment.
#
#     Returns:
#         JSONResponse: A JSON response containing status code, message and payment token.
#     """
#     response = await payment_service.add_bank_card(access_token, card_info)
#
#     return JSONResponse(
#         status_code=response.status_code,
#         content={
#             'success': True,
#             'message': 'Payment token added successfully.',
#             'payment_token': response.payment_token,
#         },
#     )
