from typing import Optional
import logging
import requests
from app.core.config import settings
from app.models.combine_search import CombineSearchResponse, SearchData

logger = logging.getLogger(__name__)

class ProductClient:
    """Client for handling product-related API requests."""

    async def get_category_products(
        query: Optional[str] = None,
        current: int = 1,
        page_size: int = 5
    ) -> CombineSearchResponse:
        """Fetch products from the category API.

        Args:
            query: Search query string
            current: Current page number
            page_size: Number of items per page

        Returns:
            CombineSearchResponse object containing the search results
        """
        try:
            url = f"{settings.PRODUCT_API_BASE_URL}/product-service/product/no-auth/combineSearch"
            params = {
                "query": query,
                "current": current,
                "pageSize": page_size
            }

            try:
                headers = {
                    "Referer": settings.API_REFERER,
                    "accept-language": "zh_CN"
                }
                response = requests.get(url, params=params, headers=headers)
                if response.status_code == 200:
                    return CombineSearchResponse(**response.json())
                else:
                    logger.error(f"Failed to fetch products: {response.status_code}")
                    return CombineSearchResponse(
                        code=response.status_code,
                        message=f"Failed to fetch products: {response.status_code}",
                        data=SearchData(records=[], total=0, pageSize=page_size, current=current, totalPages=0),
                        traceId=None,
                        placeholder=None,
                        success=False
                    )
            except requests.RequestException as e:
                logger.error(f"Error fetching products: {str(e)}")
                return CombineSearchResponse(
                    code=500,
                    message=str(e),
                    data=SearchData(records=[], total=0, pageSize=page_size, current=current, totalPages=0),
                    traceId=None,
                    placeholder=None,
                    success=False
                )

        except Exception as e:
            logger.error(f"Error in get_category_products: {str(e)}")
            raise
            
    @staticmethod
    async def combine_search(
        query: Optional[str] = None,
        current: Optional[int] = 1,
        page_size: Optional[int] = 10,
        image_url: Optional[str] = None
    ) -> CombineSearchResponse:
        logger.info(f"Processing combine search request: query='{query}', current={current}, page_size={page_size}, image_url='{image_url}'")
        try:
            return await ProductClient.get_category_products(
                query=query,
                current=current,
                page_size=page_size
            )

        except Exception as e:
            logger.error(f"Error in combine search: {str(e)}")
            return CombineSearchResponse(
                code=500,
                message=str(e),
                traceId=None,
                placeholder=None,
                success=False
            )