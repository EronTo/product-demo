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
        modified_query = query
        
        if site_filter:
            modified_query += f" {site_filter}"
        
        if exclude_sites:
            sites = exclude_sites.split()
            for site in sites:
                if site.startswith("site:"):
                    modified_query += f" -site:{site[5:]}"
                else:
                    modified_query += f" -{site}"
        
        params = {
            "key": settings.GOOGLE_API_KEY,
            "cx": settings.GOOGLE_CX_ID,
            "q": modified_query,
            "num": num_results
        }
        
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
                return GoogleSearchResult(items=[], searchInformation={"totalResults": "0"})
            
            return GoogleSearchResult(**data)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Google search request failed: {str(e)}")
            return GoogleSearchResult(items=[], searchInformation={"totalResults": "0"})