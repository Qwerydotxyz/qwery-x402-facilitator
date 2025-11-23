"""
Facilitator Wallet Management

Manages the facilitator's hot wallet for x402 payment facilitation.
"""

import os
import base58
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class FacilitatorWallet:
    """Manages facilitator's hot wallet"""

    def __init__(self):
        """Initialize wallet from environment variables"""

        # Load configuration
        private_key_b58 = os.getenv("FACILITATOR_PRIVATE_KEY")
        if not private_key_b58:
            logger.warning("⚠️  FACILITATOR_PRIVATE_KEY not set - facilitation mode disabled")
            self.enabled = False
            self.keypair = None
            self.pubkey = None
            return

        try:
            # Decode private key
            private_key_bytes = base58.b58decode(private_key_b58)
            self.keypair = Keypair.from_bytes(private_key_bytes)
            self.pubkey = self.keypair.pubkey()
            self.enabled = True

            # Load settings
            self.min_balance = int(os.getenv("FACILITATOR_MIN_BALANCE", "100000"))
            self.service_fee_percent = int(os.getenv("FACILITATOR_SERVICE_FEE_PERCENT", "10"))

            logger.info(f"✅ Facilitator wallet initialized: {self.pubkey}")
            logger.info(f"📊 Service fee: {self.service_fee_percent}%")
            logger.info(f"⚠️  Min balance alert: {self.min_balance} lamports")

        except Exception as e:
            logger.error(f"❌ Failed to initialize facilitator wallet: {e}")
            self.enabled = False
            self.keypair = None
            self.pubkey = None

    def is_enabled(self) -> bool:
        """Check if facilitation mode is enabled"""
        return self.enabled

    async def get_balance(self, client: AsyncClient) -> int:
        """Get current wallet balance in lamports"""
        if not self.enabled:
            return 0

        try:
            response = await client.get_balance(self.pubkey)
            return response.value
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return 0

    async def check_balance(self, client: AsyncClient) -> dict:
        """
        Check if balance is sufficient for processing payments

        Returns:
            {
                "balance": int,
                "balance_sol": float,
                "min_balance": int,
                "is_low": bool,
                "can_process_payments": bool
            }
        """
        balance = await self.get_balance(client)

        is_low = balance < self.min_balance
        can_process = balance > 10000  # Need at least 10k for one transaction fee

        if is_low:
            logger.warning(
                f"⚠️  Low balance: {balance} lamports "
                f"(min: {self.min_balance} lamports)"
            )

        if not can_process:
            logger.error(
                f"❌ Insufficient balance: {balance} lamports "
                f"(need at least 10000 lamports)"
            )

        return {
            "balance": balance,
            "balance_sol": balance / 1_000_000_000,  # Convert to SOL
            "min_balance": self.min_balance,
            "is_low": is_low,
            "can_process_payments": can_process
        }

    def calculate_amounts(self, payment_amount: int) -> dict:
        """
        Calculate service fee and merchant payout

        Args:
            payment_amount: Total payment amount in lamports

        Returns:
            {
                "total": int,              # Total payment
                "service_fee": int,        # Facilitator's fee
                "merchant_amount": int,    # Amount to merchant
                "fee_percent": int         # Service fee percentage
            }
        """
        service_fee = int(payment_amount * self.service_fee_percent / 100)
        merchant_amount = payment_amount - service_fee

        return {
            "total": payment_amount,
            "service_fee": service_fee,
            "merchant_amount": merchant_amount,
            "fee_percent": self.service_fee_percent
        }

    def get_public_key_string(self) -> Optional[str]:
        """Get public key as string"""
        return str(self.pubkey) if self.enabled else None


# Singleton instance
_facilitator_wallet: Optional[FacilitatorWallet] = None


def get_facilitator_wallet() -> FacilitatorWallet:
    """Get or create facilitator wallet singleton"""
    global _facilitator_wallet
    if _facilitator_wallet is None:
        _facilitator_wallet = FacilitatorWallet()
    return _facilitator_wallet
