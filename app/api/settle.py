"""
Settle Payment API Endpoint - Qwery Facilitator
"""

from fastapi import APIRouter, HTTPException
import logging

from app.services.payment_settler import PaymentSettler
from app.services.wallet import get_facilitator_wallet
from app.models.x402 import SettleRequest, SettleResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize payment settler with facilitator wallet
facilitator_wallet = get_facilitator_wallet()
payment_settler = PaymentSettler(facilitator_wallet)

@router.post("/settle", response_model=SettleResponse)
async def settle_payment(request: SettleRequest):
    """Settle a signed payment transaction on blockchain"""
    try:
        logger.info(f"SETTLEMENT - Qwery Facilitator")
        logger.info(f"Network: {request.network}")
        
        result = await payment_settler.settle(
            signed_transaction=request.signed_transaction,
            network=request.network,
            merchant_address=getattr(request, 'merchant_address', None),
            merchant_amount=getattr(request, 'merchant_amount', None)
        )
        
        return SettleResponse(**result)
        
    except Exception as e:
        logger.error(f"Settlement error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"error": str(e)})
