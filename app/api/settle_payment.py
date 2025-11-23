"""
Settle Payment API Endpoint - Qwery Facilitator
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from solders.pubkey import Pubkey
from typing import Optional
import logging

from app.services.wallet import get_facilitator_wallet
from app.services.payment_settler import PaymentSettler
from app.services.solana import get_solana_client

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Facilitation"])


class SettlePaymentRequest(BaseModel):
    signed_transaction: str = Field(...)
    network: str = Field(default="solana-devnet")
    merchant_address: Optional[str] = Field(
        None,
        description="Optional merchant address to receive 90% of payment"
    )
    merchant_amount: Optional[int] = Field(
        None,
        description="Amount to send to merchant (90% of payment)"
    )


class SettlePaymentResponse(BaseModel):
    signature: str
    confirmed: bool
    network_fee: int
    slot: int
    merchant_signature: Optional[str] = Field(
        None,
        description="Signature of merchant payout (if applicable)"
    )


@router.post("/settle", response_model=SettlePaymentResponse)
async def settle_payment(request: SettlePaymentRequest):
    """Settle a payment transaction on blockchain"""

    try:
        wallet = get_facilitator_wallet()

        if not wallet.is_enabled():
            raise HTTPException(
                status_code=503,
                detail={"error": "Facilitation mode not enabled"}
            )

        client = get_solana_client(request.network)
        balance_status = await wallet.check_balance(client)

        if not balance_status["can_process_payments"]:
            raise HTTPException(
                status_code=503,
                detail={"error": "Insufficient facilitator balance"}
            )

        logger.info("=" * 60)
        logger.info("SETTLEMENT - Qwery Facilitator")
        logger.info("=" * 60)

        # STEP 1: Submit user's payment
        logger.info("📥 Step 1: Submitting user payment to blockchain...")
        payment_settler = PaymentSettler(wallet.keypair)

        result = await payment_settler.submit_transaction(
            client=client,
            signed_transaction_b64=request.signed_transaction
        )

        logger.info(f"Settlement result: {result}")

        # Check if confirmed
        if not result.get("confirmed", False):
            logger.error(f"Transaction not confirmed: {result}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "User payment failed to confirm",
                    "signature": result.get("signature", "unknown")
                }
            )

        logger.info(f"✅ User payment confirmed: {result['signature']}")
        logger.info(f"   Slot: {result.get('slot', 'unknown')}")
        logger.info(f"   Fee: {result.get('network_fee', 0)} lamports")

        # STEP 2: Pay merchant (if provided)
        merchant_signature = None

        if request.merchant_address and request.merchant_amount:
            logger.info("")
            logger.info("💰 Step 2: Paying merchant...")
            logger.info(f"   Merchant: {request.merchant_address}")
            logger.info(f"   Amount: {request.merchant_amount} lamports (90%)")

            try:
                from app.services.payment_creator import PaymentCreator
                creator = PaymentCreator(wallet.keypair)

                merchant_result = await creator.create_merchant_payout(
                    client=client,
                    merchant_pubkey=Pubkey.from_string(request.merchant_address),
                    amount=request.merchant_amount
                )

                if merchant_result.get("confirmed", False):
                    merchant_signature = merchant_result["signature"]
                    logger.info(f"✅ Merchant paid: {merchant_signature}")
                else:
                    logger.error(f"❌ Merchant payout failed")

            except Exception as e:
                logger.error(f"⚠️ Merchant payout error: {e}")
                # Don't fail whole transaction if merchant payout fails
        else:
            logger.info("")
            logger.info("💡 No merchant - funds stay with facilitator")

        logger.info("=" * 60)
        logger.info("✅ SETTLEMENT COMPLETE")
        logger.info(f"   User payment: {result['signature']}")
        if merchant_signature:
            logger.info(f"   Merchant payout: {merchant_signature}")
        logger.info(f"   🌐 Solscan: https://solscan.io/tx/{result['signature']}")
        logger.info("=" * 60)

        return SettlePaymentResponse(
            signature=result["signature"],
            confirmed=True,
            network_fee=result.get("network_fee", 5000),
            slot=result.get("slot", 0),
            merchant_signature=merchant_signature
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Settlement error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)}
        )


@router.get("/fee-stats")
async def get_fee_stats():
    """Get fee statistics"""
    wallet = get_facilitator_wallet()

    if not wallet.is_enabled():
        return {"enabled": False}

    settler = PaymentSettler(wallet.keypair)
    stats = settler.get_fee_stats()

    return {
        "enabled": True,
        "total_fees_paid": stats["total_fees_paid"],
        "transactions_processed": stats["transactions_processed"],
        "average_fee": stats["average_fee"]
    }
