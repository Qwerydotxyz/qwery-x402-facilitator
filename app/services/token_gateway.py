"""
Token Gateway - Accept any token, token-gating, tiered memberships
"""

from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from typing import Dict, List, Optional
import logging

from app.services.token import get_associated_token_address

logger = logging.getLogger(__name__)


class TokenGateway:
    """
    Token Gateway for:
    - Accepting any SPL token as payment
    - Token-gating (hold X tokens = access)
    - Tiered memberships
    - Custom token requirements
    """

    def __init__(self):
        self.tiers = {}  # tier_name -> requirements
        self.accepted_tokens = {}  # token_mint -> token_info

    def add_accepted_token(
        self,
        token_name: str,
        token_mint: str,
        decimals: int,
        min_amount: Optional[int] = None
    ):
        """Register a token as accepted payment"""
        self.accepted_tokens[token_mint] = {
            "name": token_name,
            "mint": token_mint,
            "decimals": decimals,
            "min_amount": min_amount
        }
        logger.info(f"✅ Token registered: {token_name} ({token_mint})")

    def add_membership_tier(
        self,
        tier_name: str,
        required_token: str,
        required_amount: int,
        benefits: List[str]
    ):
        """
        Add a membership tier based on token holdings
        
        Example:
        add_membership_tier(
            tier_name="Gold",
            required_token="USDC_MINT",
            required_amount=1000000000,  # 1000 USDC
            benefits=["Premium API", "Priority support"]
        )
        """
        self.tiers[tier_name] = {
            "token": required_token,
            "amount": required_amount,
            "benefits": benefits
        }
        logger.info(f"✅ Tier registered: {tier_name}")

    async def check_token_gate(
        self,
        client: AsyncClient,
        wallet_address: str,
        required_token_mint: str,
        required_amount: int
    ) -> dict:
        """
        Check if wallet holds required tokens
        
        Returns:
            {
                "has_access": bool,
                "balance": int,
                "required": int,
                "token": str
            }
        """
        
        try:
            wallet_pubkey = Pubkey.from_string(wallet_address)
            token_mint = Pubkey.from_string(required_token_mint)
            
            # Get user's token account
            token_account = get_associated_token_address(wallet_pubkey, token_mint)
            
            # Check balance
            account_info = await client.get_token_account_balance(token_account)
            
            if not account_info.value:
                return {
                    "has_access": False,
                    "balance": 0,
                    "required": required_amount,
                    "token": required_token_mint,
                    "reason": "Token account not found"
                }
            
            balance = int(account_info.value.amount)
            has_access = balance >= required_amount
            
            logger.info(f"Token gate check:")
            logger.info(f"  Wallet: {wallet_address}")
            logger.info(f"  Balance: {balance}")
            logger.info(f"  Required: {required_amount}")
            logger.info(f"  Access: {'✅ GRANTED' if has_access else '❌ DENIED'}")
            
            return {
                "has_access": has_access,
                "balance": balance,
                "required": required_amount,
                "token": required_token_mint
            }
            
        except Exception as e:
            logger.error(f"❌ Token gate check error: {e}")
            return {
                "has_access": False,
                "balance": 0,
                "required": required_amount,
                "token": required_token_mint,
                "reason": str(e)
            }

    async def get_user_tier(
        self,
        client: AsyncClient,
        wallet_address: str
    ) -> dict:
        """
        Check what membership tier user qualifies for
        
        Returns:
            {
                "tier": str,
                "benefits": List[str],
                "qualified_tiers": List[str]
            }
        """
        
        qualified_tiers = []
        
        for tier_name, requirements in self.tiers.items():
            check = await self.check_token_gate(
                client=client,
                wallet_address=wallet_address,
                required_token_mint=requirements["token"],
                required_amount=requirements["amount"]
            )
            
            if check["has_access"]:
                qualified_tiers.append({
                    "name": tier_name,
                    "benefits": requirements["benefits"]
                })
        
        # Return highest tier
        if qualified_tiers:
            highest_tier = qualified_tiers[-1]  # Assume last is highest
            return {
                "tier": highest_tier["name"],
                "benefits": highest_tier["benefits"],
                "qualified_tiers": [t["name"] for t in qualified_tiers]
            }
        else:
            return {
                "tier": "Free",
                "benefits": ["Basic access"],
                "qualified_tiers": []
            }

    def is_token_accepted(self, token_mint: str) -> bool:
        """Check if token is accepted for payment"""
        return token_mint in self.accepted_tokens

    def get_accepted_tokens(self) -> List[dict]:
        """Get list of all accepted tokens"""
        return list(self.accepted_tokens.values())

    def get_tiers(self) -> Dict:
        """Get all membership tiers"""
        return self.tiers


# Global token gateway instance
token_gateway = TokenGateway()

# Register default tokens
token_gateway.add_accepted_token(
    token_name="SOL",
    token_mint="So11111111111111111111111111111111111111112",
    decimals=9
)

token_gateway.add_accepted_token(
    token_name="USDC",
    token_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    decimals=6
)

token_gateway.add_accepted_token(
    token_name="USDT",
    token_mint="Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
    decimals=6
)

# Example tiers (customize as needed)
token_gateway.add_membership_tier(
    tier_name="Bronze",
    required_token="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    required_amount=100_000000,  # 100 USDC
    benefits=["Basic API access", "Standard support"]
)

token_gateway.add_membership_tier(
    tier_name="Silver",
    required_token="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    required_amount=1000_000000,  # 1000 USDC
    benefits=["Enhanced API access", "Priority support", "10% fee discount"]
)

token_gateway.add_membership_tier(
    tier_name="Gold",
    required_token="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    required_amount=10000_000000,  # 10,000 USDC
    benefits=["Unlimited API access", "24/7 support", "25% fee discount", "Custom features"]
)
