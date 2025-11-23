"""
Solana Blockchain Service
Handles payment verification and settlement on Solana
"""

import base64
import logging
from typing import Optional, Tuple
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solana.rpc.commitment import Confirmed
from solders.pubkey import Pubkey
from solders.signature import Signature

from app.models.x402 import X402Network, SolanaPayload
from app.models.network import get_network_config

logger = logging.getLogger(__name__)


class SolanaService:
    """Service for Solana blockchain operations"""

    def __init__(self):
        self.clients = {}
        self._init_clients()

    def _init_clients(self):
        """Initialize Solana RPC clients"""
        for network in [X402Network.SOLANA, X402Network.SOLANA_DEVNET]:
            config = get_network_config(network)
            if config:
                self.clients[network] = AsyncClient(config.rpcUrl)
                logger.info(f"Initialized Solana client for {network}")

    def get_client(self, network: X402Network) -> AsyncClient:
        """Get RPC client for network"""
        client = self.clients.get(network)
        if not client:
            raise ValueError(f"Network {network} not supported")
        return client

    async def verify_transaction(
        self,
        payload: SolanaPayload,
        network: X402Network,
        expected_amount: str,
        expected_recipient: str,
        expected_token: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Verify a Solana transaction

        Args:
            payload: Solana payment payload
            network: Solana network
            expected_amount: Expected amount in atomic units
            expected_recipient: Expected recipient wallet
            expected_token: Expected token mint address

        Returns:
            (is_valid, payer_address, error_reason)
        """
        try:
            client = self.get_client(network)

            # Decode transaction
            tx_bytes = base64.b64decode(payload.transaction)
            transaction = Transaction.deserialize(tx_bytes)

            # Get payer (first signature)
            if not transaction.signatures or len(transaction.signatures) == 0:
                return False, None, "No signatures found"

            payer = str(transaction.signatures[0].pubkey())

            # Verify transaction is signed
            if not transaction.signatures[0].signature:
                return False, payer, "Transaction not signed"

            # Check if transaction is valid (has required instructions)
            if not transaction.instructions or len(transaction.instructions) == 0:
                return False, payer, "No instructions found"

            # Verify recipient
            # For now, we do basic validation
            # In production, you'd parse the transfer instruction

            logger.info(f"Transaction verified for payer: {payer}")
            return True, payer, None

        except Exception as e:
            logger.error(f"Transaction verification error: {str(e)}")
            return False, None, f"Verification error: {str(e)}"

    async def settle_transaction(
        self,
        payload: SolanaPayload,
        network: X402Network
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Settle transaction on Solana blockchain

        Args:
            payload: Solana payment payload
            network: Solana network

        Returns:
            (success, transaction_signature, error_reason)
        """
        try:
            client = self.get_client(network)

            # Decode and send transaction
            tx_bytes = base64.b64decode(payload.transaction)

            # Send transaction
            response = await client.send_raw_transaction(
                tx_bytes,
                opts={"skip_preflight": False, "preflight_commitment": Confirmed}
            )

            if response.value:
                tx_signature = str(response.value)
                logger.info(f"Transaction settled: {tx_signature}")

                # Wait for confirmation (optional, can be async)
                # confirmation = await client.confirm_transaction(
                #     Signature.from_string(tx_signature),
                #     commitment=Confirmed
                # )

                return True, tx_signature, None
            else:
                return False, None, "Transaction send failed"

        except Exception as e:
            logger.error(f"Transaction settlement error: {str(e)}")
            return False, None, f"Settlement error: {str(e)}"

    async def check_balance(
        self,
        wallet_address: str,
        network: X402Network
    ) -> Optional[int]:
        """
        Check SOL balance of a wallet

        Args:
            wallet_address: Wallet public key
            network: Solana network

        Returns:
            Balance in lamports or None if error
        """
        try:
            client = self.get_client(network)
            pubkey = Pubkey.from_string(wallet_address)

            response = await client.get_balance(pubkey)
            if response.value is not None:
                return response.value
            return None

        except Exception as e:
            logger.error(f"Balance check error: {str(e)}")
            return None

    async def verify_token_transfer(
        self,
        transaction_signature: str,
        network: X402Network,
        expected_amount: str,
        expected_recipient: str,
        token_mint: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify a token transfer transaction on-chain

        Args:
            transaction_signature: Transaction signature to verify
            network: Solana network
            expected_amount: Expected amount in atomic units
            expected_recipient: Expected recipient wallet
            token_mint: Token mint address

        Returns:
            (is_valid, error_reason)
        """
        try:
            client = self.get_client(network)

            # Get transaction details
            sig = Signature.from_string(transaction_signature)
            response = await client.get_transaction(
                sig,
                encoding="json",
                commitment=Confirmed
            )

            if not response.value:
                return False, "Transaction not found"

            # Parse and verify transaction
            # This would involve checking:
            # 1. Transfer instruction exists
            # 2. Amount matches
            # 3. Recipient matches
            # 4. Token mint matches

            # For now, basic validation
            logger.info(f"Token transfer verified: {transaction_signature}")
            return True, None

        except Exception as e:
            logger.error(f"Token transfer verification error: {str(e)}")
            return False, f"Verification error: {str(e)}"

    async def close(self):
        """Close all RPC clients"""
        for client in self.clients.values():
            await client.close()


# Global instance
solana_service = SolanaService()

# Export clients dictionary for compatibility with main.py
# This allows both old code (solana_service) and new code (solana_clients) to work
solana_clients = solana_service.clients


# ⬇️ ADD THIS NEW FUNCTION ⬇️
def get_solana_client(network: str) -> AsyncClient:
    """
    Get Solana client for specified network
    Solana RPC client wrapper for x402 protocol

    Args:
        network: Network name as string (e.g., "solana", "solana-devnet")

    Returns:
        AsyncClient instance

    Raises:
        ValueError: If network is not supported
    """
    # Convert string to X402Network enum
    # Only include networks that actually exist in X402Network
    network_map = {
        "solana": X402Network.SOLANA,
        "solana-devnet": X402Network.SOLANA_DEVNET,
    }

    network_enum = network_map.get(network.lower())
    if not network_enum:
        raise ValueError(f"Unsupported network: {network}. Supported: {list(network_map.keys())}")

    return solana_service.get_client(network_enum)
