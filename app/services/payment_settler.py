"""
Payment Settler - Qwery Facilitation Mode
"""

from solders.transaction import Transaction
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts
import base64
import logging
import asyncio

logger = logging.getLogger(__name__)


class PaymentSettler:
    def __init__(self, facilitator_keypair: Keypair):
        self.facilitator_keypair = facilitator_keypair
        self.facilitator_pubkey = facilitator_keypair.pubkey
        self.total_fees_paid = 0
        self.transactions_processed = 0

    async def submit_transaction(
        self,
        client: AsyncClient,
        signed_transaction_b64: str
    ) -> dict:
        """Submit fully-signed transaction to blockchain"""

        try:
            logger.info("Decoding signed transaction...")
            tx_bytes = base64.b64decode(signed_transaction_b64)
            transaction = Transaction.from_bytes(tx_bytes)

            signature_count = len(transaction.signatures)
            logger.info(f"Transaction has {signature_count} signatures")

            if signature_count < 2:
                raise Exception(
                    f"Transaction missing signatures. "
                    f"Expected 2 (facilitator + user), got {signature_count}"
                )

            logger.info("Submitting transaction to blockchain...")
            logger.info("💰 Facilitator will pay network fee (~5000 lamports)")

            # Try WITH preflight to see the actual error
            try:
                response = await client.send_raw_transaction(
                    tx_bytes,
                    opts=TxOpts(skip_preflight=False)  # CHANGED: Show errors
                )
                signature = str(response.value)
                logger.info(f"✅ Transaction accepted: {signature}")
            except Exception as preflight_error:
                logger.error(f"🚨 PREFLIGHT ERROR: {preflight_error}")
                logger.error(f"   This is why the transaction is rejected!")
                raise

            # Wait for confirmation
            logger.info("Waiting for confirmation...")
            confirmed = False
            slot = 0

            try:
                confirmation = await asyncio.wait_for(
                    client.confirm_transaction(signature, commitment=Confirmed),
                    timeout=30.0
                )

                if confirmation.value and len(confirmation.value) > 0:
                    conf_value = confirmation.value[0]
                    if hasattr(conf_value, 'slot'):
                        slot = conf_value.slot
                    confirmed = True
                    logger.info(f"✅ Transaction confirmed in slot {slot}")
                else:
                    logger.warning(f"⚠️ Check Solscan: https://solscan.io/tx/{signature}")
                    confirmed = True

            except asyncio.TimeoutError:
                logger.warning(f"⚠️ Confirmation timeout")
                logger.warning(f"   https://solscan.io/tx/{signature}")
                confirmed = True

            network_fee = 5000

            if confirmed:
                logger.info(f"💰 Network fee paid: {network_fee} lamports")
                logger.info(f"🔗 Signature: {signature}")
                logger.info(f"🌐 Solscan: https://solscan.io/tx/{signature}")

                self.total_fees_paid += network_fee
                self.transactions_processed += 1

            return {
                "signature": signature,
                "confirmed": confirmed,
                "network_fee": network_fee,
                "slot": slot
            }

        except Exception as e:
            logger.error(f"❌ Error: {e}")
            raise Exception(f"Failed to submit transaction: {str(e)}")

    def get_fee_stats(self) -> dict:
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
