"""
x402 Protocol Models - Qwery Implementation
Standard x402 protocol specification
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class X402Scheme(str, Enum):
    """Payment schemes supported by x402 protocol"""
    EXACT = "exact"  # EIP-3009 Transfer with Authorization


class X402Network(str, Enum):
    """Supported blockchain networks"""
    SOLANA = "solana"
    SOLANA_DEVNET = "solana-devnet"


class X402Accept(BaseModel):
    """
    Payment requirement specification
    Sent in 402 response to client
    """
    scheme: X402Scheme = Field(..., description="Payment scheme (exact)")
    network: X402Network = Field(..., description="Blockchain network")
    maxAmountRequired: str = Field(..., description="Maximum amount in atomic units")
    asset: str = Field(..., description="Token contract address/mint")
    payTo: str = Field(..., description="Recipient wallet address")
    resource: str = Field(..., description="Protected resource URL")
    maxTimeoutSeconds: int = Field(default=60, description="Payment validity window")
    description: Optional[str] = Field(None, description="Human-readable description")
    mimeType: Optional[str] = Field(None, description="Response content type")


class X402PaymentRequirements(BaseModel):
    """
    402 Payment Required Response
    Standard x402 protocol response
    """
    x402Version: int = Field(default=1, description="x402 protocol version")
    error: str = Field(default="Payment required", description="Error message")
    accepts: List[X402Accept] = Field(..., description="Accepted payment methods")


class SolanaPayload(BaseModel):
    """
    Solana payment payload
    Contains partially-signed transaction
    """
    transaction: str = Field(..., description="Base64-encoded Solana transaction")


class X402PaymentPayload(BaseModel):
    """
    Payment payload sent in X-PAYMENT header
    Client sends this after creating payment
    """
    x402Version: int = Field(default=1, description="x402 protocol version")
    scheme: X402Scheme = Field(..., description="Payment scheme used")
    network: X402Network = Field(..., description="Blockchain network used")
    payload: SolanaPayload = Field(..., description="Network-specific payment data")


class X402PaymentResponse(BaseModel):
    """
    Payment settlement response
    Sent in X-PAYMENT-RESPONSE header
    """
    success: bool = Field(..., description="Whether settlement succeeded")
    transaction: Optional[str] = Field(None, description="On-chain transaction hash")
    network: Optional[X402Network] = Field(None, description="Network where settled")
    payer: Optional[str] = Field(None, description="Payer's wallet address")
    errorReason: Optional[str] = Field(None, description="Error reason if failed")


class VerifyRequest(BaseModel):
    """
    Request to /verify endpoint
    Verifies payment signature and validity
    """
    paymentPayload: X402PaymentPayload = Field(..., description="Payment from client")
    paymentRequirements: X402Accept = Field(..., description="Expected payment details")


class VerifyResponse(BaseModel):
    """
    Response from /verify endpoint
    """
    valid: bool = Field(..., description="Whether payment is valid")
    reason: Optional[str] = Field(None, description="Failure reason if invalid")
    payer: Optional[str] = Field(None, description="Payer's wallet address")
    amount: Optional[str] = Field(None, description="Payment amount verified")


class SettleRequest(BaseModel):
    """
    Request to /settle endpoint
    Settles payment on blockchain
    """
    paymentPayload: X402PaymentPayload = Field(..., description="Payment from client")
    paymentRequirements: X402Accept = Field(..., description="Expected payment details")


class SettleResponse(BaseModel):
    """
    Response from /settle endpoint
    """
    success: bool = Field(..., description="Whether settlement succeeded")
    transaction: Optional[str] = Field(None, description="On-chain transaction hash")
    network: Optional[X402Network] = Field(None, description="Network where settled")
    payer: Optional[str] = Field(None, description="Payer's wallet address")
    errorReason: Optional[str] = Field(None, description="Error reason if failed")


class NetworkInfo(BaseModel):
    """
    Supported network information
    """
    network: X402Network = Field(..., description="Network identifier")
    chainId: Optional[str] = Field(None, description="Chain ID if applicable")
    rpcUrl: str = Field(..., description="RPC endpoint URL")
    explorerUrl: str = Field(..., description="Block explorer URL")
    nativeCurrency: Dict[str, Any] = Field(..., description="Native currency info")
    supported: bool = Field(default=True, description="Whether network is active")


class SupportedNetworksResponse(BaseModel):
    """
    Response from /supported endpoint
    Lists all supported blockchain networks
    """
    networks: List[NetworkInfo] = Field(..., description="Supported networks")


class MerchantResource(BaseModel):
    """
    Merchant resource for discovery
    """
    resource: str = Field(..., description="Protected resource URL")
    merchant: str = Field(..., description="Merchant identifier")
    description: Optional[str] = Field(None, description="Resource description")
    accepts: List[X402Accept] = Field(..., description="Accepted payment methods")
    category: Optional[str] = Field(None, description="Resource category")
    tags: List[str] = Field(default_factory=list, description="Resource tags")


class DiscoveryResponse(BaseModel):
    """
    Response from /discovery/resources endpoint
    Lists available merchants and resources
    """
    resources: List[MerchantResource] = Field(..., description="Available resources")
    total: int = Field(..., description="Total number of resources")
    page: int = Field(default=1, description="Current page")
    pageSize: int = Field(default=20, description="Resources per page")
