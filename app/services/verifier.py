"""
Payment Verification Service
Verifies payment signatures and parameters
"""

import logging
from typing import Tuple, Optional

from app.models.x402 import (
    X402PaymentPayload,
    X402Accept,
    X402Network,
    X402Scheme
)

logger = logging.getLogger(__name__)


class PaymentVerifier:
    """Service for verifying payment payloads"""

    async def verify_payment(
        self,
        payment_payload: X402PaymentPayload,
        payment_requirements: X402Accept
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Verify a payment payload against requirements

        Args:
            payment_payload: Payment from client
            payment_requirements: Expected payment parameters

        Returns:
            (is_valid, payer_address, error_reason)
        """
        try:
            # Step 1: Verify protocol version
            if payment_payload.x402Version != 1:
                return False, None, "Unsupported x402 version"

            # Step 2: Verify scheme matches
            if payment_payload.scheme != payment_requirements.scheme:
                return False, None, f"Scheme mismatch: expected {payment_requirements.scheme}"

            # Step 3: Verify network matches
            if payment_payload.network != payment_requirements.network:
                return False, None, f"Network mismatch: expected {payment_requirements.network}"

            # Step 4: Network-specific verification
            if payment_payload.network in [X402Network.SOLANA, X402Network.SOLANA_DEVNET]:
                return await self._verify_solana_payment(
                    payment_payload,
                    payment_requirements
                )
            else:
                return False, None, f"Unsupported network: {payment_payload.network}"

        except Exception as e:
            logger.error(f"Payment verification error: {str(e)}")
            return False, None, f"Verification error: {str(e)}"

    async def _verify_solana_payment(
        self,
        payment_payload: X402PaymentPayload,
        payment_requirements: X402Accept
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Verify Solana payment

        Args:
            payment_payload: Payment from client
            payment_requirements: Expected payment parameters

        Returns:
            (is_valid, payer_address, error_reason)
        """
        try:
            # Import here to avoid circular imports
            from app.services.solana import solana_service

            # Verify we have Solana payload
            if not payment_payload.payload or not payment_payload.payload.transaction:
                return False, None, "Missing Solana transaction"

            # Verify transaction structure and signatures
            is_valid, payer, error = await solana_service.verify_transaction(
                payload=payment_payload.payload,
                network=payment_payload.network,
                expected_amount=payment_requirements.maxAmountRequired,
                expected_recipient=payment_requirements.payTo,
                expected_token=payment_requirements.asset
            )

            if not is_valid:
                return False, payer, error or "Invalid Solana transaction"

            # Additional checks
            # 1. Verify amount (would be done in instruction parsing)
            # 2. Verify recipient (would be done in instruction parsing)
            # 3. Verify token mint (would be done in instruction parsing)
            # 4. Verify timing (if needed)

            logger.info(f"Solana payment verified for payer: {payer}")
            return True, payer, None

        except Exception as e:
            logger.error(f"Solana payment verification error: {str(e)}")
            return False, None, f"Solana verification error: {str(e)}"

    def validate_payment_requirements(
        self,
        requirements: X402Accept
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate payment requirements structure

        Args:
            requirements: Payment requirements to validate

        Returns:
            (is_valid, error_reason)
        """
        # Verify scheme
        if requirements.scheme not in [X402Scheme.EXACT]:
            return False, f"Unsupported scheme: {requirements.scheme}"

        # Verify network
        if requirements.network not in [X402Network.SOLANA, X402Network.SOLANA_DEVNET]:
            return False, f"Unsupported network: {requirements.network}"

        # Verify amount
        try:
            amount = int(requirements.maxAmountRequired)
            if amount <= 0:
                return False, "Amount must be positive"
        except ValueError:
            return False, "Invalid amount format"

        # Verify recipient address
        if not requirements.payTo:
            return False, "Missing recipient address"

        # Verify asset
        if not requirements.asset:
            return False, "Missing asset/token address"

        return True, None


# Global instance
payment_verifier = PaymentVerifier()
