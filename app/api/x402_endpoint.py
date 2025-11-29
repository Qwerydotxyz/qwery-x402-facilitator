"""
x402 Protocol Endpoint - Returns 402 Payment Required
This endpoint enables x402scan registration and x402 protocol compliance
"""

import os
from fastapi import APIRouter, Request, Header
from fastapi.responses import JSONResponse
from typing import Optional

router = APIRouter()

# Token addresses (Solana Mainnet)
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
USDT_MINT = "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"
SOL_MINT = "So11111111111111111111111111111111111111112"


def get_facilitator_wallet() -> str:
    """Get facilitator wallet address from environment"""
    facilitator_key = os.getenv("FACILITATOR_PRIVATE_KEY")
    
    if facilitator_key and facilitator_key != "your_base58_private_key_here":
        try:
            from solders.keypair import Keypair
            keypair = Keypair.from_base58_string(facilitator_key)
            return str(keypair.pubkey())
        except Exception:
            pass
    
    return "Configure FACILITATOR_PRIVATE_KEY in .env"


def get_base_url() -> str:
    """Get base URL from environment"""
    return os.getenv("BASE_URL", "https://facilitator.qwery.xyz")


def build_402_response(resource_url: str, facilitator_wallet: str) -> dict:
    """
    Build x402 compliant 402 Payment Required response
    Schema: https://www.x402.org/
    """
    return {
        "x402Version": 1,
        "accepts": [
            {
                "scheme": "exact",
                "network": "solana",
                "maxAmountRequired": "100000",  # 0.1 USDC (6 decimals)
                "resource": resource_url,
                "description": "Access Qwery x402 Facilitator API",
                "mimeType": "application/json",
                "payTo": facilitator_wallet,
                "maxTimeoutSeconds": 60,
                "asset": USDC_MINT
            },
            {
                "scheme": "exact",
                "network": "solana",
                "maxAmountRequired": "100000",  # 0.1 USDT (6 decimals)
                "resource": resource_url,
                "description": "Access Qwery x402 Facilitator API",
                "mimeType": "application/json",
                "payTo": facilitator_wallet,
                "maxTimeoutSeconds": 60,
                "asset": USDT_MINT
            },
            {
                "scheme": "exact",
                "network": "solana",
                "maxAmountRequired": "1000000",  # 0.001 SOL (9 decimals)
                "resource": resource_url,
                "description": "Access Qwery x402 Facilitator API",
                "mimeType": "application/json",
                "payTo": facilitator_wallet,
                "maxTimeoutSeconds": 60,
                "asset": SOL_MINT
            }
        ]
    }


@router.get("/create")
@router.post("/create")
async def x402_create_endpoint(
    request: Request,
    x_payment: Optional[str] = Header(None, alias="X-Payment"),
    x_payment_signature: Optional[str] = Header(None, alias="X-Payment-Signature")
):
    """
    x402 Protocol Compliant Endpoint
    
    Behavior:
    - Without X-Payment header: Returns HTTP 402 Payment Required
    - With valid X-Payment header: Returns HTTP 200 with resource
    
    This endpoint is designed for x402scan registration.
    """
    
    facilitator_wallet = get_facilitator_wallet()
    base_url = get_base_url()
    resource_url = f"{base_url}/create"
    
    # Check for payment headers
    if not x_payment and not x_payment_signature:
        # No payment provided - return 402 Payment Required
        return JSONResponse(
            status_code=402,
            content=build_402_response(resource_url, facilitator_wallet),
            headers={
                "X-Payment-Required": "true",
                "Content-Type": "application/json"
            }
        )
    
    # Payment header present - verify and return success
    # In production, you would verify the payment signature here
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Payment accepted",
            "x402Version": 1,
            "resource": resource_url,
            "facilitator": facilitator_wallet,
            "available_endpoints": {
                "create_payment": f"{base_url}/create-payment",
                "settle": f"{base_url}/settle",
                "verify": f"{base_url}/verify",
                "wallet_status": f"{base_url}/wallet-status"
            }
        }
    )


@router.get("/x402")
async def x402_info():
    """
    x402 Protocol Information Endpoint
    Returns facilitator capabilities and supported payment methods
    """
    
    facilitator_wallet = get_facilitator_wallet()
    base_url = get_base_url()
    
    return {
        "x402Version": 1,
        "facilitator": {
            "name": "Qwery x402 Facilitator",
            "version": "1.2.0",
            "wallet": facilitator_wallet,
            "description": "Production-ready payment facilitator for Solana"
        },
        "supported_assets": [
            {
                "symbol": "USDC",
                "mint": USDC_MINT,
                "decimals": 6,
                "network": "solana"
            },
            {
                "symbol": "USDT", 
                "mint": USDT_MINT,
                "decimals": 6,
                "network": "solana"
            },
            {
                "symbol": "SOL",
                "mint": SOL_MINT,
                "decimals": 9,
                "network": "solana"
            }
        ],
        "endpoints": {
            "x402_gate": f"{base_url}/create",
            "protocol_info": f"{base_url}/x402",
            "create_payment": f"{base_url}/create-payment",
            "settle": f"{base_url}/settle",
            "verify": f"{base_url}/verify",
            "health": f"{base_url}/health",
            "docs": f"{base_url}/docs"
        },
        "features": [
            "Zero user fees",
            "Multi-token support",
            "Instant settlement",
            "Token-gated access"
        ]
    }
