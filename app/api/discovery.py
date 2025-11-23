"""
/discovery/resources Endpoint
Discovery API for finding available merchants and resources
"""

from fastapi import APIRouter, Query
import logging

from app.models.x402 import DiscoveryResponse, MerchantResource

logger = logging.getLogger(__name__)

router = APIRouter(tags=["x402"])


# In-memory registry of merchants (will be database-backed in future)
# For now, merchants can register via separate admin API (future enhancement)
MERCHANT_REGISTRY: list[MerchantResource] = []


@router.get("/discovery/resources", response_model=DiscoveryResponse)
async def discover_resources(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Resources per page"),
    category: str = Query(default=None, description="Filter by category"),
    search: str = Query(default=None, description="Search in description"),
):
    """
    Discover available x402-enabled resources

    Returns a paginated list of merchants and resources that accept x402 payments.

    **Query Parameters:**
    - `page` - Page number (default: 1)
    - `page_size` - Resources per page (default: 20, max: 100)
    - `category` - Filter by category (optional)
    - `search` - Search term for descriptions (optional)

    **Response:**
    ```json
    {
      "resources": [
        {
          "resource": "https://example.com/api/premium-content",
          "merchant": "example-merchant",
          "description": "Premium AI-generated content",
          "accepts": [
            {
              "scheme": "exact",
              "network": "solana",
              "maxAmountRequired": "50000",
              "asset": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
              "payTo": "merchant_wallet",
              "resource": "https://example.com/api/premium-content",
              "maxTimeoutSeconds": 60
            }
          ],
          "category": "AI",
          "tags": ["ai", "content", "premium"]
        }
      ],
      "total": 1,
      "page": 1,
      "pageSize": 20
    }
    ```

    **Use Cases:**
    - Marketplaces can display available services
    - Aggregators can index x402 resources
    - Users can discover what they can access with x402
    """
    try:
        # Start with all resources
        filtered_resources = MERCHANT_REGISTRY.copy()

        # Filter by category if provided
        if category:
            filtered_resources = [
                r for r in filtered_resources
                if r.category and r.category.lower() == category.lower()
            ]

        # Search in descriptions if provided
        if search:
            search_lower = search.lower()
            filtered_resources = [
                r for r in filtered_resources
                if (r.description and search_lower in r.description.lower()) or
                   (r.merchant and search_lower in r.merchant.lower())
            ]

        total = len(filtered_resources)

        # Pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_resources = filtered_resources[start_idx:end_idx]

        logger.info(f"Discovery: returning {len(paginated_resources)} of {total} resources")

        return DiscoveryResponse(
            resources=paginated_resources,
            total=total,
            page=page,
            pageSize=page_size
        )

    except Exception as e:
        logger.error(f"Discovery endpoint error: {str(e)}")
        # Return empty list on error
        return DiscoveryResponse(
            resources=[],
            total=0,
            page=page,
            pageSize=page_size
        )


def register_merchant(resource: MerchantResource):
    """
    Register a merchant resource (internal use)
    In production, this would be a protected admin endpoint
    """
    MERCHANT_REGISTRY.append(resource)
    logger.info(f"Registered merchant resource: {resource.merchant}")


def unregister_merchant(resource_url: str):
    """
    Unregister a merchant resource (internal use)
    """
    global MERCHANT_REGISTRY
    MERCHANT_REGISTRY = [r for r in MERCHANT_REGISTRY if r.resource != resource_url]
    logger.info(f"Unregistered merchant resource: {resource_url}")
