"""
Network Configuration
Solana mainnet and devnet settings
"""

from app.models.x402 import X402Network, NetworkInfo


# Solana token mints
SOLANA_TOKENS = {
    "mainnet": {
        "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
        "SOL": "So11111111111111111111111111111111111111112"  # Wrapped SOL
    },
    "devnet": {
        "USDC": "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU",  # Devnet USDC
        "SOL": "So11111111111111111111111111111111111111112"
    }
}


# Network configurations
NETWORKS = {
    X402Network.SOLANA: NetworkInfo(
        network=X402Network.SOLANA,
        chainId=None,  # Solana doesn't use chainId
        rpcUrl="https://api.mainnet-beta.solana.com",
        explorerUrl="https://solscan.io",
        nativeCurrency={
            "name": "Solana",
            "symbol": "SOL",
            "decimals": 9
        },
        supported=True
    ),
    X402Network.SOLANA_DEVNET: NetworkInfo(
        network=X402Network.SOLANA_DEVNET,
        chainId=None,
        rpcUrl="https://api.devnet.solana.com",
        explorerUrl="https://solscan.io",
        nativeCurrency={
            "name": "Solana",
            "symbol": "SOL",
            "decimals": 9
        },
        supported=True
    )
}


def get_network_config(network: X402Network) -> NetworkInfo:
    """Get configuration for a specific network"""
    return NETWORKS.get(network)


def get_token_mint(network: X402Network, token_symbol: str) -> str:
    """Get token mint address for a network"""
    network_key = "mainnet" if network == X402Network.SOLANA else "devnet"
    return SOLANA_TOKENS.get(network_key, {}).get(token_symbol.upper())


def is_network_supported(network: X402Network) -> bool:
    """Check if network is supported"""
    config = NETWORKS.get(network)
    return config is not None and config.supported


# Token decimals
TOKEN_DECIMALS = {
    "SOL": 9,
    "USDC": 6,
    "USDT": 6
}


def get_token_decimals(token_symbol: str) -> int:
    """Get decimals for a token"""
    return TOKEN_DECIMALS.get(token_symbol.upper(), 6)  # Default to 6
