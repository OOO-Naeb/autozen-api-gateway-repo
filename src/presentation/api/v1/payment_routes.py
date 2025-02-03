from http.client import HTTPResponse
from typing import Annotated, Any, Coroutine

from fastapi import APIRouter, Body, Depends, HTTPException
from starlette import status
from starlette.responses import JSONResponse

from src.application.services.payment_service import PaymentService
from src.domain.oauth_schemas import oauth2_token_schema
from src.domain.schemas import PaymentToken, CardInfo, AccessToken

payment_router = APIRouter(
    tags=["Payment"],
    prefix="/api/v1/payment",
)

@payment_router.post('/add_payment_method', response_model=PaymentToken)
async def add_payment_method(
        access_token: Annotated[AccessToken, Depends(oauth2_token_schema)],
        card_info: Annotated[CardInfo, Body(...)],
        payment_service: Annotated[PaymentService, Depends(PaymentService)]
) -> JSONResponse:
    """
    CONTROLLER: Add a payment method to the user's account. Passes the query to the 'PaymentUseCase'.

    Args:
        access_token (AccessToken): The access token to authenticate the user.
        card_info (CardInfo): The card information to add to the user's account.
        payment_service (PaymentService): The payment service to process the payment.

    Returns:
        JSONResponse: A JSON response containing status code, message and payment token.
    """
    status_code, payment_token = await payment_service.add_payment_method(access_token, card_info)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'success': True,
            'message': 'Payment token added successfully.',
            'payment_token': payment_token,
        },
    )
