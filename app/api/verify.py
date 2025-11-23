"""
/verify Endpoint
Verifies payment signature and validity
"""

from fastapi import APIRouter, HTTPException, status
import logging

from app.models.x402 import VerifyRequest, VerifyResponse
from app.services.verifier import payment_verifier

logger = logging.getLogger(__name__)

router = APIRouter(tags=["x402"])


@router.post("/verify", response_model=VerifyResponse)
async def verify_payment(request: VerifyRequest):
    """
    Verify a payment payload

    Validates payment signature and parameters without settling on-chain.
    Use this to check if a payment is valid before calling /settle.

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

    **Response:**
    ```json
    {
      "valid": true,
      "payer": "payer_wallet_address",
      "amount": "50000"
    }
    ```

    **Error Response:**
    ```json
    {
      "valid": false,
      "reason": "Invalid signature"
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
            return VerifyResponse(
                valid=False,
                reason=f"Invalid requirements: {req_error}"
            )

        # Verify payment
        is_valid, payer, error = await payment_verifier.verify_payment(
            payment_payload=request.paymentPayload,
            payment_requirements=request.paymentRequirements
        )

        if is_valid:
            logger.info(f"Payment verified for payer: {payer}")
            return VerifyResponse(
                valid=True,
                payer=payer,
                amount=request.paymentRequirements.maxAmountRequired
            )
        else:
            logger.warning(f"Payment verification failed: {error}")
            return VerifyResponse(
                valid=False,
                reason=error or "Verification failed"
            )

    except Exception as e:
        logger.error(f"Verify endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification error: {str(e)}"
        )
