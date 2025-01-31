from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException

from src.domain.oauth_schemas import oauth2_token_schema
from src.domain.schemas import PaymentToken, CardInfo, AccessToken

payment_router = APIRouter(
    tags=["Payment"],
    prefix="/api/v1/payment",
)

@payment_router.post('/add_payment_method', response_model=PaymentToken)
async def add_payment_method(
        access_token: Annotated[AccessToken, Depends(oauth2_token_schema)],
        card_info: Annotated[CardInfo, Body(...)]
) -> PaymentToken | None:
    """
    CONTROLLER: Add a payment method to the user's account. Passes the query to the 'PaymentUseCase'.

    Args:
        card_info (CardInfo): The card information to add to the user's account.
        access_token (AccessToken): The access token to authenticate the user.

    Returns:
        PaymentToken: A payment token needed for payments processing.
    """
    # DEV ONLY -----------------------------------------------------------------------------------------
    try:
        assert access_token
        return PaymentToken(payment_token=f'TEST_PAYMENT_TOKEN_RETURN: {card_info.card_number, card_info.cvv_code}')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # --------------------------------------------------------------------------------------------------
