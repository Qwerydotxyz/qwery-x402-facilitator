"""
Payment Transaction Creator - Multi-Token Support

Supports:
- SOL (native)
- USDC (SPL token)
- USDT (SPL token)
"""

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.system_program import TransferParams, transfer
from solders.message import Message
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
import base64
import logging
from typing import Optional
from app.services.token import (
    get_associated_token_address,
    create_transfer_checked_instruction,
    create_associated_token_account_instruction,
    get_token_mint,
    TOKEN_DECIMALS
)

logger = logging.getLogger(__name__)


class PaymentCreator:
    """Creates and partially signs payment transactions"""

    def __init__(self, facilitator_keypair: Keypair):
        self.facilitator_keypair = facilitator_keypair
        self.facilitator_pubkey = facilitator_keypair.pubkey()

    async def create_payment_transaction(
        self,
        client: AsyncClient,
        payer_pubkey: Pubkey,
        amount: int,
        token: str = "SOL",
        merchant_pubkey: Optional[Pubkey] = None
    ) -> dict:
        """
        Create a payment transaction
        
        Supports SOL, USDC, USDT
        """

        try:
            logger.info(f"Creating {token} payment transaction...")
            logger.info(f"  Amount: {amount}")
            logger.info(f"  From: {payer_pubkey}")
            logger.info(f"  To: {self.facilitator_pubkey}")

            # Get recent blockhash
            blockhash_resp = await client.get_latest_blockhash(commitment=Confirmed)
            recent_blockhash = blockhash_resp.value.blockhash

            instructions = []

            if token.upper() == "SOL":
                # SOL transfer (existing logic)
                transfer_ix = transfer(
                    TransferParams(
                        from_pubkey=payer_pubkey,
                        to_pubkey=self.facilitator_pubkey,
                        lamports=amount
                    )
                )
                instructions.append(transfer_ix)
                
            else:
                # SPL Token transfer (USDC/USDT)
                token_mint = get_token_mint(token)
                decimals = TOKEN_DECIMALS.get(token.upper(), 6)
                
                # Get token accounts
                user_token_account = get_associated_token_address(payer_pubkey, token_mint)
                facilitator_token_account = get_associated_token_address(
                    self.facilitator_pubkey, 
                    token_mint
                )
                
                logger.info(f"  User token account: {user_token_account}")
                logger.info(f"  Facilitator token account: {facilitator_token_account}")
                
                # Check if facilitator token account exists
                try:
                    account_info = await client.get_account_info(facilitator_token_account)
                    if not account_info.value:
                        logger.info("  Creating facilitator token account...")
                        create_ix = create_associated_token_account_instruction(
                            payer=self.facilitator_pubkey,
                            owner=self.facilitator_pubkey,
                            mint=token_mint
                        )
                        instructions.append(create_ix)
                except:
                    logger.info("  Creating facilitator token account...")
                    create_ix = create_associated_token_account_instruction(
                        payer=self.facilitator_pubkey,
                        owner=self.facilitator_pubkey,
                        mint=token_mint
                    )
                    instructions.append(create_ix)
                
                # Create token transfer instruction
                transfer_ix = create_transfer_checked_instruction(
                    source=user_token_account,
                    mint=token_mint,
                    destination=facilitator_token_account,
                    owner=payer_pubkey,
                    amount=amount,
                    decimals=decimals
                )
                instructions.append(transfer_ix)

            # Create message with facilitator as fee payer
            message = Message.new_with_blockhash(
                instructions=instructions,
                payer=self.facilitator_pubkey,
                blockhash=recent_blockhash
            )

            # Create unsigned transaction
            transaction = Transaction.new_unsigned(message)

            # Facilitator partially signs
            logger.info("✍️  Facilitator signing transaction (partial)...")
            transaction.partial_sign([self.facilitator_keypair], recent_blockhash)

            # Serialize
            serialized = base64.b64encode(bytes(transaction)).decode('utf-8')

            logger.info(f"✅ {token} payment transaction created and partially signed")
            logger.info(f"   Transaction size: {len(serialized)} bytes")

            return {
                "transaction": serialized,
                "requires_user_signature": True,
                "payer": str(payer_pubkey),
                "amount": amount,
                "token": token,
                "facilitator": str(self.facilitator_pubkey),
                "recent_blockhash": str(recent_blockhash)
            }

        except Exception as e:
            logger.error(f"❌ Error creating payment transaction: {e}")
            raise Exception(f"Failed to create payment: {str(e)}")

    async def create_merchant_payout(
        self,
        client: AsyncClient,
        merchant_pubkey: Pubkey,
        amount: int,
        token: str = "SOL"
    ) -> dict:
        """Create transaction to pay merchant"""

        try:
            blockhash_resp = await client.get_latest_blockhash(commitment=Confirmed)
            recent_blockhash = blockhash_resp.value.blockhash

            if token.upper() == "SOL":
                # SOL transfer
                transfer_ix = transfer(
                    TransferParams(
                        from_pubkey=self.facilitator_pubkey,
                        to_pubkey=merchant_pubkey,
                        lamports=amount
                    )
                )
            else:
                # SPL token transfer
                token_mint = get_token_mint(token)
                decimals = TOKEN_DECIMALS.get(token.upper(), 6)
                
                facilitator_token_account = get_associated_token_address(
                    self.facilitator_pubkey, 
                    token_mint
                )
                merchant_token_account = get_associated_token_address(
                    merchant_pubkey, 
                    token_mint
                )
                
                transfer_ix = create_transfer_checked_instruction(
                    source=facilitator_token_account,
                    mint=token_mint,
                    destination=merchant_token_account,
                    owner=self.facilitator_pubkey,
                    amount=amount,
                    decimals=decimals
                )

            message = Message.new_with_blockhash(
                instructions=[transfer_ix],
                payer=self.facilitator_pubkey,
                blockhash=recent_blockhash
            )

            transaction = Transaction.new_unsigned(message)
            transaction.sign([self.facilitator_keypair], recent_blockhash)

            logger.info(f"Paying merchant: {amount} {token} to {merchant_pubkey}")
            signature = await client.send_transaction(transaction)

            confirmation = await client.confirm_transaction(
                signature.value,
                commitment=Confirmed
            )

            confirmed = bool(confirmation.value)
            
            if confirmed:
                logger.info(f"✅ Merchant payout confirmed: {signature.value}")

            return {
                "signature": str(signature.value),
                "confirmed": confirmed
            }

        except Exception as e:
            logger.error(f"❌ Error paying merchant: {e}")
            raise Exception(f"Failed to pay merchant: {str(e)}")
