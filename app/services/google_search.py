import logging
from typing import Optional, List
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
        exclude_sites: Optional[List] = None,
        date_restrict: Optional[str] = None,
        num_results: int = 8,
        language: Optional[str] = None,
        country: Optional[str] = None
    ) -> GoogleSearchResult:
        
        modified_query = query
        
        if site_filter:
            modified_query += f" site:{site_filter}"  # Corrected to use 'site:' for inclusion
        
        if exclude_sites:
            for site in exclude_sites:
                modified_query += f" -site:{site}"
        
        logger.info(f"query: {query}, site_filter: {site_filter}, exclude_sites: {exclude_sites}, language: {language}, country: {country}, date_restrict: {date_restrict}, num_results: {num_results}, modified_query: {modified_query}")
         
        params = {
            "key": settings.GOOGLE_API_KEY,
            "cx": settings.GOOGLE_CX_ID,
            "q": modified_query,
            "num": num_results
        }
        
        # if language:
        #     params["lr"] = f"lang_{language}"
        # else:
        #     # 默认设置为简体中文
        #     params["lr"] = "lang_zh-CN"
        
        params["cr"] = "countryCN"
        
        # 添加界面语言设置，简体中文为"zh-CN"
        # params["hl"] = "zh-CN"
        
        if date_restrict:
            params["dateRestrict"] = date_restrict
        
        logger.info(f"Google search params: {params}")
        
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