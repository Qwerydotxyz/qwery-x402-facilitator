"""
Token Gateway API
Accept any token, token-gating, tiered memberships
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

from app.services.token_gateway import token_gateway
from app.services.solana import get_solana_client

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Token Gateway"])


class CheckAccessRequest(BaseModel):
    wallet_address: str
    required_token: str
    required_amount: int
    network: str = Field(default="solana")


class CheckAccessResponse(BaseModel):
    has_access: bool
    balance: int
    required: int
    token: str
    reason: str = None


class GetTierRequest(BaseModel):
    wallet_address: str
    network: str = Field(default="solana")


class TierResponse(BaseModel):
    tier: str
    benefits: List[str]
    qualified_tiers: List[str]


class AddTokenRequest(BaseModel):
    token_name: str
    token_mint: str
    decimals: int
    min_amount: Optional[int] = None


class AddTierRequest(BaseModel):
    tier_name: str
    required_token: str
    required_amount: int
    benefits: List[str]


@router.post("/token-gate/check-access", response_model=CheckAccessResponse)
async def check_access(request: CheckAccessRequest):
    """
    Check if wallet has required token holdings for access
    
    Example: Check if user holds 100 USDC
    """
    
    try:
        client = get_solana_client(request.network)
        
        result = await token_gateway.check_token_gate(
            client=client,
            wallet_address=request.wallet_address,
            required_token_mint=request.required_token,
            required_amount=request.required_amount
        )
        
        return CheckAccessResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Token gate check error: {e}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.post("/token-gate/get-tier", response_model=TierResponse)
async def get_tier(request: GetTierRequest):
    """
    Get user's membership tier based on token holdings
    
    Returns highest tier user qualifies for
    """
    
    try:
        client = get_solana_client(request.network)
        
        result = await token_gateway.get_user_tier(
            client=client,
            wallet_address=request.wallet_address
        )
        
        return TierResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Get tier error: {e}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.get("/token-gate/accepted-tokens")
async def get_accepted_tokens():
    """Get list of all accepted tokens"""
    return {
        "tokens": token_gateway.get_accepted_tokens()
    }


@router.get("/token-gate/tiers")
async def get_tiers():
    """Get all membership tiers"""
    return {
        "tiers": token_gateway.get_tiers()
    }


@router.post("/token-gate/add-token")
async def add_token(request: AddTokenRequest):
    """Register a new accepted token (admin only)"""
    
    try:
        token_gateway.add_accepted_token(
            token_name=request.token_name,
            token_mint=request.token_mint,
            decimals=request.decimals,
            min_amount=request.min_amount
        )
        
        return {"status": "success", "token": request.token_name}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.post("/token-gate/add-tier")
async def add_tier(request: AddTierRequest):
    """Add a new membership tier (admin only)"""
    
    try:
        token_gateway.add_membership_tier(
            tier_name=request.tier_name,
            required_token=request.required_token,
            required_amount=request.required_amount,
            benefits=request.benefits
        )
        
        return {"status": "success", "tier": request.tier_name}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
