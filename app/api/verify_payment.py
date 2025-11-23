"""
Verify Payment API
Validates payment WITHOUT submitting to blockchain
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from solders.pubkey import Pubkey
import logging

from app.services.wallet import get_facilitator_wallet
from app.services.payment_verifier import PaymentVerifier
from app.services.solana import get_solana_client

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Verification"])


class VerifyPaymentRequest(BaseModel):
    signed_transaction: str = Field(..., description="Base64-encoded signed transaction")
    payer: str = Field(..., description="Expected payer wallet address")
    amount: int = Field(..., description="Expected payment amount in atomic units")
    token: str = Field(default="SOL", description="Expected token: SOL, USDC, USDT")
    network: str = Field(default="solana")
    recipient: str = Field(None, description="Expected recipient (optional)")


class VerifyPaymentResponse(BaseModel):
    valid: bool
    payer: str = None
    amount: int = None
    token: str = None
    recipient: str = None
    reason: str = None


@router.post("/verify", response_model=VerifyPaymentResponse)
async def verify_payment(request: VerifyPaymentRequest):
    """
    Verify a payment transaction WITHOUT submitting to blockchain
    
    Fast pre-check before settlement:
    - Validates transaction structure
    - Checks signatures
    - Verifies balances
    - Does NOT submit to blockchain
    """
    
    try:
        wallet = get_facilitator_wallet()
        
        if not wallet.is_enabled():
            raise HTTPException(
                status_code=503,
                detail={"error": "Facilitation mode not enabled"}
            )
        
        logger.info("============================================================")
        logger.info("VERIFICATION - Fast Pre-Check")
        logger.info("============================================================")
        logger.info(f"📥 Verifying payment:")
        logger.info(f"   Payer: {request.payer}")
        logger.info(f"   Amount: {request.amount}")
        logger.info(f"   Token: {request.token}")
        logger.info(f"   Network: {request.network}")
        
        client = get_solana_client(request.network)
        verifier = PaymentVerifier(wallet.keypair.pubkey())
        
        result = await verifier.verify_transaction(
            client=client,
            signed_transaction_b64=request.signed_transaction,
            expected_payer=request.payer,
            expected_amount=request.amount,
            expected_token=request.token,
            expected_recipient=request.recipient
        )
        
        if result["valid"]:
            logger.info("✅ VERIFICATION PASSED")
            logger.info(f"   Payer: {result['payer']}")
            logger.info(f"   Amount: {result['amount']}")
            logger.info(f"   Token: {result['token']}")
        else:
            logger.warning("❌ VERIFICATION FAILED")
            logger.warning(f"   Reason: {result.get('reason', 'Unknown')}")
        
        logger.info("============================================================")
        
        return VerifyPaymentResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Verification error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)}
        )
