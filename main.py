"""
Qwery x402 Facilitator - Main Application
Production-ready payment facilitator for Solana
"""

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import logging

# Import API routes
from app.api import (
    create_payment,
    settle,
    verify,
    wallet_status,
    supported,
    discovery,
    token_gateway
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Qwery x402 Facilitator",
    version="1.2.0",
    description="PayAI-Compatible Payment Facilitator for Solana",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(create_payment.router, tags=["Payments"])
app.include_router(settle.router, tags=["Payments"])
app.include_router(verify.router, tags=["Payments"])
app.include_router(wallet_status.router, tags=["Status"])
app.include_router(supported.router, tags=["Discovery"])
app.include_router(discovery.router, tags=["Discovery"])
app.include_router(token_gateway.router, prefix="/token-gate", tags=["Token Gateway"])

# Root endpoint
@app.get("/")
async def root():
    """Service information and capabilities"""
    facilitator_wallet = os.getenv("FACILITATOR_PRIVATE_KEY")
    is_configured = bool(facilitator_wallet and facilitator_wallet != "your_base58_private_key_here")
    
    return {
        "service": "Qwery x402 Facilitator",
        "version": "1.2.0",
        "tagline": "PayAI-Compatible Payment Facilitator for Solana",
        "features": [
            "Multi-token support (SOL, USDC, USDT)",
            "Zero user fees (facilitator pays)",
            "Token-gated access & membership tiers",
            "Partial transaction signing"
        ],
        "modes": {
            "facilitation": "enabled" if is_configured else "not installed"
        },
        "endpoints": {
            "core": ["/supported", "/discovery", "/health"],
            "facilitation": [
                "/create-payment",
                "/settle", 
                "/verify",
                "/wallet-status"
            ],
            "token_gateway": [
                "/token-gate/check-access",
                "/token-gate/get-tier",
                "/token-gate/accepted-tokens",
                "/token-gate/tiers"
            ]
        },
        "documentation": "/docs"
    }

# Health check
@app.get("/health")
async def health():
    """Health check endpoint"""
    facilitator_wallet = os.getenv("FACILITATOR_PRIVATE_KEY")
    is_configured = bool(facilitator_wallet and facilitator_wallet != "your_base58_private_key_here")
    
    # Get facilitator wallet address if configured
    facilitator_address = None
    if is_configured:
        try:
            from solders.keypair import Keypair
            keypair = Keypair.from_base58_string(facilitator_wallet)
            facilitator_address = str(keypair.pubkey())
        except:
            pass
    
    return {
        "status": "healthy",
        "version": "1.2.0",
        "networks": {
            "solana": "active",
            "solana-devnet": "active" if "active"
        },
        "facilitation": {
            "status": "enabled" if is_configured else "not configured",
            "wallet": facilitator_address
        }
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": {"error": "Internal server error"}}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting Qwery x402 Facilitator v1.2.0")
    facilitator_key = os.getenv("FACILITATOR_PRIVATE_KEY")
    if facilitator_key and facilitator_key != "your_base58_private_key_here":
        logger.info("📡 Solana clients ready")
        logger.info("💰 Facilitation mode: ENABLED")
        try:
            from solders.keypair import Keypair
            keypair = Keypair.from_base58_string(facilitator_key)
            logger.info(f"   Wallet: {str(keypair.pubkey)}")
        except:
            pass
    logger.info("✅ Facilitator ready!")

# Run with: python main.py
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
