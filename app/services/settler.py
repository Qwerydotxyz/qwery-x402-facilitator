"""
Payment Settler - Qwery Facilitation Mode

Submits fully-signed transactions to blockchain.
Facilitator pays network fees from its wallet.
"""

from solders.transaction import Transaction
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts
import base64
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PaymentSettler:
    """Settles payment transactions on blockchain"""

    def __init__(self, facilitator_keypair: Keypair):
        """
        Initialize payment settler

        Args:
            facilitator_keypair: Facilitator's keypair (pays network fees)
        """
        self.facilitator_keypair = facilitator_keypair
        self.facilitator_pubkey = facilitator_keypair.pubkey()

        # Track fees for monitoring
        self.total_fees_paid = 0
        self.transactions_processed = 0

    async def submit_transaction(
        self,
        client: AsyncClient,
        signed_transaction_b64: str
    ) -> dict:
        """
        Submit fully-signed transaction to blockchain

        CRITICAL: Facilitator PAYS the network fee!

        The transaction is already signed by:
        1. Facilitator (first signature)
        2. User (second signature)

        When we submit it, Solana charges the fee to the first signer,
        which is the facilitator. This implements the x402 facilitation model.

        Args:
            client: Solana RPC client
            signed_transaction_b64: Base64-encoded, fully-signed transaction

        Returns:
            {
                "signature": str,
                "confirmed": bool,
                "network_fee": int,
                "slot": int
            }
        """

        try:
            # Decode transaction
            logger.info("Decoding signed transaction...")
            tx_bytes = base64.b64decode(signed_transaction_b64)
            transaction = Transaction.from_bytes(tx_bytes)

            # Verify transaction has required signatures
            # Should have 2 signatures: facilitator + user
            signature_count = len(transaction.signatures)
            logger.info(f"Transaction has {signature_count} signatures")

            if signature_count < 2:
                raise Exception(
                    f"Transaction missing signatures. "
                    f"Expected 2 (facilitator + user), got {signature_count}"
                )

            logger.info("Submitting transaction to blockchain...")
            logger.info("💰 Facilitator will pay network fee (~5000 lamports)")

            # Send transaction
            # Network fee is charged to the first signer (facilitator)
            opts = TxOpts(
                skip_preflight=False,
                preflight_commitment=Confirmed
            )

            response = await client.send_transaction(
                transaction,
                opts=opts
            )

            signature = response.value
            logger.info(f"Transaction submitted: {signature}")

            # Wait for confirmation
            logger.info("Waiting for confirmation...")
            confirmation = await client.confirm_transaction(
                signature,
                commitment=Confirmed
            )

            confirmed = confirmation.value[0].confirmation_status == "confirmed"
            slot = confirmation.value[0].slot if confirmation.value else 0

            # Estimate network fee
            # Typical Solana transaction fee is ~5000 lamports
            # Could fetch actual fee from transaction details for accuracy
            network_fee = 5000

            if confirmed:
                logger.info(f"✅ Transaction confirmed in slot {slot}")
                logger.info(f"💰 Network fee paid: {network_fee} lamports")
                logger.info(f"🔗 Signature: {signature}")

                # Update fee tracking
                self.total_fees_paid += network_fee
                self.transactions_processed += 1

                avg_fee = self.total_fees_paid / self.transactions_processed
                logger.info(
                    f"📊 Stats: {self.transactions_processed} transactions, "
                    f"{self.total_fees_paid} total fees, "
                    f"{avg_fee:.0f} avg fee"
                )
            else:
                logger.error(f"❌ Transaction failed to confirm: {signature}")

            return {
                "signature": str(signature),
                "confirmed": confirmed,
                "network_fee": network_fee,
                "slot": slot
            }

        except Exception as e:
            logger.error(f"❌ Error submitting transaction: {e}")
            raise Exception(f"Failed to submit transaction: {str(e)}")

    def get_fee_stats(self) -> dict:
        """
        Get fee statistics

        Returns:
            {
                "total_fees_paid": int,
                "transactions_processed": int,
                "average_fee": float
            }
        """
        avg_fee = (
            self.total_fees_paid / self.transactions_processed
            if self.transactions_processed > 0
            else 0
        )

        return {
            "total_fees_paid": self.total_fees_paid,
            "transactions_processed": self.transactions_processed,
            "average_fee": avg_fee
        }

    async def verify_transaction_success(
        self,
        client: AsyncClient,
        signature: str
    ) -> dict:
        """
        Verify a transaction was successful and get details

        Args:
            client: Solana RPC client
            signature: Transaction signature

        Returns:
            {
                "success": bool,
                "slot": int,
                "block_time": int,
                "fee": int
            }
        """

        try:
            # Get transaction details
            tx_response = await client.get_transaction(
                signature,
                commitment=Confirmed
            )

            if not tx_response.value:
                return {
                    "success": False,
                    "error": "Transaction not found"
                }

            tx = tx_response.value

            # Extract details
            success = tx.transaction.meta.err is None
            slot = tx.slot
            block_time = tx.block_time
            fee = tx.transaction.meta.fee

            return {
                "success": success,
                "slot": slot,
                "block_time": block_time,
                "fee": fee
            }

        except Exception as e:
            logger.error(f"Error verifying transaction: {e}")
            return {
                "success": False,
                "error": str(e)
            }
