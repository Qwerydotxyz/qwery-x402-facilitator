"""
Wallet Status API Endpoint

Endpoint for monitoring facilitator wallet status.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Monitoring"])


class WalletStatusResponse(BaseModel):
    """Facilitator wallet status"""

    enabled: bool = Field(..., description="Whether facilitation mode is enabled")
    public_key: str = Field(None, description="Facilitator's public key")
    balance: int = Field(None, description="Current balance in lamports")
    balance_sol: float = Field(None, description="Current balance in SOL")
    min_balance: int = Field(None, description="Minimum balance threshold")
    is_low: bool = Field(None, description="Whether balance is below minimum")
    can_process_payments: bool = Field(None, description="Whether wallet can process payments")
    service_fee_percent: int = Field(None, description="Service fee percentage")


@router.get(
    "/wallet-status",
    response_model=WalletStatusResponse,
    summary="Get Wallet Status",
    description="""
    Get facilitator wallet status and balance.

    **Returns:**
    - Wallet balance in lamports and SOL
    - Whether balance is sufficient
    - Service fee percentage
    - Alerts if balance is low

    **Use this endpoint to:**
    - Monitor facilitator balance
    - Check if facilitation mode is enabled
    - Get alerts when wallet needs funding
    """
)
async def get_wallet_status(network: str = "solana-devnet"):
    """Get facilitator wallet status"""

    from app.services.wallet import get_facilitator_wallet
    from app.services.solana import get_solana_client

    wallet = get_facilitator_wallet()

    if not wallet.is_enabled():
        return WalletStatusResponse(
            enabled=False,
            public_key=None,
            balance=None,
            balance_sol=None,
            min_balance=None,
            is_low=None,
            can_process_payments=False,
            service_fee_percent=None
        )

    try:
        # Get Solana client
        client = get_solana_client(network)

        # Check balance
        status_result = await wallet.check_balance(client)

        return WalletStatusResponse(
            enabled=True,
            public_key=wallet.get_public_key_string(),
            balance=status_result["balance"],
            balance_sol=status_result["balance_sol"],
            min_balance=status_result["min_balance"],
            is_low=status_result["is_low"],
            can_process_payments=status_result["can_process_payments"],
            service_fee_percent=wallet.service_fee_percent
        )

    except Exception as e:
        logger.error(f"Error getting wallet status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to get wallet status",
                "reason": str(e)
            }
        )


class FundingInfo(BaseModel):
    """Funding information"""

    public_key: str
    devnet_faucet: str = "https://faucet.solana.com"
    recommended_amount_sol: float = 0.1
    recommended_amount_lamports: int = 100_000_000
    estimated_transactions: int


@router.get(
    "/funding-info",
    response_model=FundingInfo,
    summary="Get Funding Information",
    description="Get information about how to fund the facilitator wallet"
)
async def get_funding_info():
    """Get funding information"""

    from app.services.wallet import get_facilitator_wallet

    wallet = get_facilitator_wallet()

    if not wallet.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Facilitation mode not enabled"
        )

    # Estimate transactions
    # Assuming ~5000 lamports per transaction fee
    recommended_lamports = 100_000_000
    fee_per_tx = 5000
    estimated_tx = recommended_lamports // fee_per_tx

    return FundingInfo(
        public_key=wallet.get_public_key_string(),
        devnet_faucet="https://faucet.solana.com",
        recommended_amount_sol=0.1,
        recommended_amount_lamports=recommended_lamports,
        estimated_transactions=estimated_tx
    )
