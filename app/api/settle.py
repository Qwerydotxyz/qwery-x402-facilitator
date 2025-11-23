"""
/settle Endpoint
Settles payment on blockchain
"""

from fastapi import APIRouter, HTTPException, status
import logging

from app.models.x402 import SettleRequest, SettleResponse
from app.services.verifier import payment_verifier
from app.services.settler import payment_settler

logger = logging.getLogger(__name__)

router = APIRouter(tags=["x402"])


@router.post("/settle", response_model=SettleResponse)
async def settle_payment(request: SettleRequest):
    """
    Settle a payment on blockchain

    Submits the transaction to the blockchain and returns the transaction hash.
    Should be called after /verify confirms the payment is valid.

    **Request Body:**
    ```json
    {
      "paymentPayload": {
        "x402Version": 1,
        "scheme": "exact",
        "network": "solana",
        "payload": {
          "transaction": "base64_encoded_transaction"
        }
      },
      "paymentRequirements": {
        "scheme": "exact",
        "network": "solana",
        "maxAmountRequired": "50000",
        "asset": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "payTo": "merchant_wallet_address",
        "resource": "https://example.com/premium",
        "maxTimeoutSeconds": 60
      }
    }
    ```

    **Success Response:**
    ```json
    {
      "success": true,
      "transaction": "5PtrKmcw6XHGAzMnoGkwgzgHxxGYtx9...",
      "network": "solana",
      "payer": "payer_wallet_address"
    }
    ```

    **Error Response:**
    ```json
    {
      "success": false,
      "errorReason": "Transaction settlement failed"
    }
    ```
    """
    try:
        # Validate payment requirements structure
        is_valid_req, req_error = payment_verifier.validate_payment_requirements(
            request.paymentRequirements
        )

        if not is_valid_req:
            logger.warning(f"Invalid payment requirements: {req_error}")
            return SettleResponse(
                success=False,
                errorReason=f"Invalid requirements: {req_error}"
            )

        # Verify payment first (double-check before settling)
        is_valid, payer, verify_error = await payment_verifier.verify_payment(
            payment_payload=request.paymentPayload,
            payment_requirements=request.paymentRequirements
        )

        if not is_valid:
            logger.warning(f"Payment verification failed before settlement: {verify_error}")
            return SettleResponse(
                success=False,
                payer=payer,
                errorReason=verify_error or "Payment verification failed"
            )

        # Settle payment on blockchain
        success, tx_hash, payer, settle_error = await payment_settler.settle_payment(
            payment_payload=request.paymentPayload,
            payment_requirements=request.paymentRequirements
        )

        if success:
            logger.info(f"Payment settled: {tx_hash} from {payer}")
            return SettleResponse(
                success=True,
                transaction=tx_hash,
                network=request.paymentPayload.network,
                payer=payer
            )
        else:
            logger.error(f"Payment settlement failed: {settle_error}")
            return SettleResponse(
                success=False,
                payer=payer,
                errorReason=settle_error or "Settlement failed"
            )

    except Exception as e:
        logger.error(f"Settle endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Settlement error: {str(e)}"
        )
