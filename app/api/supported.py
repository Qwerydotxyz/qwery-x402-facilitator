"""
/supported Endpoint
Lists supported blockchain networks
"""

from fastapi import APIRouter
import logging

from app.models.x402 import SupportedNetworksResponse
from app.models.network import NETWORKS

logger = logging.getLogger(__name__)

router = APIRouter(tags=["x402"])


@router.get("/supported", response_model=SupportedNetworksResponse)
async def get_supported_networks():
    """
    Get list of supported blockchain networks

    Returns information about all blockchain networks supported by this facilitator.

    **Response:**
    ```json
    {
      "networks": [
        {
          "network": "solana",
          "chainId": null,
          "rpcUrl": "https://api.mainnet-beta.solana.com",
          "explorerUrl": "https://solscan.io",
          "nativeCurrency": {
            "name": "Solana",
            "symbol": "SOL",
            "decimals": 9
          },
          "supported": true
        },
        {
          "network": "solana-devnet",
          "chainId": null,
          "rpcUrl": "https://api.devnet.solana.com",
          "explorerUrl": "https://solscan.io",
          "nativeCurrency": {
            "name": "Solana",
            "symbol": "SOL",
            "decimals": 9
          },
          "supported": true
        }
      ]
    }
    ```

    Use this endpoint to:
    - Discover which networks are available
    - Get RPC URLs for each network
    - Get block explorer URLs
    - Check network status
    """
    try:
        networks_list = [network for network in NETWORKS.values()]

        logger.info(f"Returning {len(networks_list)} supported networks")

        return SupportedNetworksResponse(
            networks=networks_list
        )

    except Exception as e:
        logger.error(f"Supported endpoint error: {str(e)}")
        # Return empty list on error rather than failing
        return SupportedNetworksResponse(networks=[])
