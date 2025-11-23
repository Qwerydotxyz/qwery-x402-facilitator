"""
Settle Payment API Endpoint - Qwery Facilitator
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from app.services.payment_settler import PaymentSettler
from app.models.x402 import SettlePaymentRequest, SettlePaymentResponse

router = APIRouter()
logger = logging.getLogger(__name__)
payment_settler = PaymentSettler()

@router.post("/settle", response_model=SettlePaymentResponse)
async def settle_payment(request: SettlePaymentRequest):
    """
    Settle a signed payment transaction on blockchain
    """
    try:
        logger.info(f"SETTLEMENT - Qwery Facilitator")
        logger.info(f"Network: {request.network}")
        
        result = await payment_settler.settle(
            signed_transaction=request.signed_transaction,
            network=request.network,
            merchant_address=request.merchant_address,
            merchant_amount=request.merchant_amount
        )
        
        return SettlePaymentResponse(**result)
        
    except Exception as e:
        logger.error(f"Settlement error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)}
        )
