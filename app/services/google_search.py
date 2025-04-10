import logging
from typing import Optional
import requests
from app.core.config import settings
from app.models.response import ResponseModel
from app.models.google_search import GoogleSearchResult

logger = logging.getLogger(__name__)


class GoogleSearchService:
    BASE_URL = "https://www.googleapis.com/customsearch/v1"

    def search(
        self,
        query: str,
        site_filter: Optional[str] = None,
        exclude_sites: Optional[str] = None,
        language: Optional[str] = None,
        date_restrict: Optional[str] = None,
        num_results: int = 8
    ) -> GoogleSearchResult:
        params = {
            "key": settings.GOOGLE_API_KEY,
            "cx": settings.GOOGLE_CX_ID,
            "q": query,
            "num": num_results
        }

        if site_filter:
            params["siteSearch"] = site_filter
        if exclude_sites:
            params["excludeTerms"] = exclude_sites
        if language:
            params["lr"] = f"lang_{language}"
        if date_restrict:
            params["dateRestrict"] = date_restrict

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                logger.error(f"Google API error: {data['error']['message']}")
                return GoogleSearchResult(**data)
            return GoogleSearchResult(**data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Google search request failed: {str(e)}")
            return ResponseModel(
                code=500,
                data=None,
                traceId="",
                detail=f"API请求失败: {str(e)}"
            )