"""
Create Payment API - Multi-Token Support
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from solders.pubkey import Pubkey
import logging

from app.services.wallet import get_facilitator_wallet
from app.services.payment_creator import PaymentCreator
from app.services.solana import get_solana_client

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Facilitation"])


class CreatePaymentRequest(BaseModel):
    payer: str = Field(..., description="User's wallet address")
    amount: int = Field(..., description="Payment amount in atomic units")
    network: str = Field(default="solana-devnet")
    token: str = Field(default="SOL", description="Token type: SOL, USDC, USDT")
    merchant_address: str = Field(None, description="Optional merchant address")


class CreatePaymentResponse(BaseModel):
    transaction: str
    requires_user_signature: bool
    payer: str
    amount: int
    token: str
    facilitator: str
    recent_blockhash: str
    service_fee: int
    merchant_amount: int


@router.post("/create-payment", response_model=CreatePaymentResponse)
async def create_payment(request: CreatePaymentRequest):
    """Create a payment transaction"""
    
    try:
        wallet = get_facilitator_wallet()
        
        if not wallet.is_enabled():
            raise HTTPException(
                status_code=503,
                detail={"error": "Facilitation mode not enabled"}
            )
        
        # Validate token
        supported_tokens = ["SOL", "USDC", "USDT"]
        if request.token.upper() not in supported_tokens:
            raise HTTPException(
                status_code=400,
                detail={"error": f"Unsupported token. Supported: {supported_tokens}"}
            )
        
        client = get_solana_client(request.network)
        balance_status = await wallet.check_balance(client)
        
        if not balance_status["can_process_payments"]:
            raise HTTPException(
                status_code=503,
                detail={"error": "Insufficient facilitator balance"}
            )
        
        logger.info("Creating payment transaction:")
        logger.info(f"  Payer: {request.payer}")
        logger.info(f"  Amount: {request.amount}")
        logger.info(f"  Token: {request.token}")
        
        # For now: 0% service fee (100% goes through)
        service_fee = 0
        merchant_amount = request.amount
        
        logger.info(f"  Service fee: {service_fee} (0%)")
        logger.info(f"  Merchant amount: {merchant_amount}")
        
        creator = PaymentCreator(wallet.keypair)
        
        result = await creator.create_payment_transaction(
            client=client,
            payer_pubkey=Pubkey.from_string(request.payer),
            amount=request.amount,
            token=request.token,
            merchant_pubkey=Pubkey.from_string(request.merchant_address) if request.merchant_address else None
        )
        
        logger.info("✅ Payment transaction created")
        
        return CreatePaymentResponse(
            transaction=result["transaction"],
            requires_user_signature=result["requires_user_signature"],
            payer=result["payer"],
            amount=request.amount,
            token=request.token,
            facilitator=result["facilitator"],
            recent_blockhash=result["recent_blockhash"],
            service_fee=service_fee,
            merchant_amount=merchant_amount
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)}
        )
