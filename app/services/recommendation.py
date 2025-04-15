from typing import List, Optional, Dict, Tuple
from app.models.product import ProductRecommendation
from app.core.config import settings
import logging
from app.models.select_products import SelectProductsResponse
from app.services.product_client import ProductClient
from typing import List
from app.services.google_search import GoogleSearchService
from app.services.llm_service import LLMService
from app.services.crawler_client import crawler_client  # 导入新的爬虫客户端
import asyncio
from app.core.text_util import process_text
from time import perf_counter, time

logger = logging.getLogger(__name__)


EXCLUDED_SITES = [
        # 社交媒体和问答平台
        "zhihu.com/column",
        "zhihu.com/question",
        "www.bilibili.com",
        "m.bilibili.com",
        "www.douyin.com",
        "www.reddit.com",
        "m.weibo.cn",
        
        # 电商平台
        "www.jd.com",
        "www.mi.com",
        "www.taobao.com",
        "www.tmall.com",
        "my.world.taobao.com",
        "jv-cn.com",
        "www.nike.com.cn/",
        
        # 新闻媒体
        "sports.sina.com.cn/",
        
        # 政府网站
        "gov.cn",
        ".gov.",
        "www.gov.",
        "moe.gov.cn",
        "miit.gov.cn",
        "mfa.gov.cn",
        
        # 官方网站
        "apple.com",
        "www.apple.com",
        "support.apple.com",
        "developer.apple.com",
        "microsoft.com",
        "www.microsoft.com",
        "support.microsoft.com",
        "docs.microsoft.com",
        "google.com/about",
        "about.google",

        "steampowered.com",
        "hxdsb.com",
        "sonystyle.com.cn",
        "getyourguide.com",
    ]

class RecommendationService:
    """
    Service for handling product recommendations based on user queries.
    """
    
    def __init__(self):
        """Initialize the RecommendationService with required dependencies."""
        self.llm_service = LLMService()
        self.google_search = GoogleSearchService()
        self._category_products_cache: Dict[str, Tuple[List[List[str]], float]] = {}  # {query: (results, timestamp)}
        self._cache_ttl = 60 * 60 * 24 * 10  # 10天  
        self._max_cache_size = 500
        self._cache_access_history = []  
    
    async def init(self):
        pass
        
    def _clean_expired_cache(self):
        current_time = time()
        expired_keys = []
        
        for key, (_, timestamp) in self._category_products_cache.items():
            if current_time - timestamp > self._cache_ttl:
                expired_keys.append(key)
                
        for key in expired_keys:
            del self._category_products_cache[key]
            if key in self._cache_access_history:
                self._cache_access_history.remove(key)
                
        if expired_keys:
            logger.info(f"已清理 {len(expired_keys)} 个过期缓存项")
    
    def _update_cache_access_history(self, cache_key: str):
        if cache_key in self._cache_access_history:
            self._cache_access_history.remove(cache_key)
            
        self._cache_access_history.append(cache_key)
    
    def _apply_lru_policy(self):
        """应用LRU（最近最少使用）策略删除缓存项"""
        if not self._cache_access_history:
            return
            
        oldest_key = self._cache_access_history.pop(0)
        
        if oldest_key in self._category_products_cache:
            del self._category_products_cache[oldest_key]
            logger.info(f"LRU策略：已删除最久未使用的缓存项 {oldest_key}")
    
    async def get_product_recommendations(
        user_query: str, 
        web_search: bool = True, 
        nums_return: Optional[int] = None
    ) -> List[ProductRecommendation]:
        """
        Get product recommendations based on user query.
        
        Args:
            user_query: The user's search query
            web_search: Flag indicating whether to use web search
            nums_return: Number of recommendations to return
            
        Returns:
            List of product recommendations
        """
        try:
            # Log request parameters
            logger.info(f"Processing recommendation request: query='{user_query}', web_search={web_search}")
            
            # Determine how many recommendations to return
            if nums_return is None:
                nums_return = settings.DEFAULT_NUM_RECOMMENDATIONS
            else:
                nums_return = min(nums_return, settings.MAX_NUM_RECOMMENDATIONS)
                
            logger.info(f"Returning {nums_return} recommendations")

            return SelectProductsResponse(selectProducts=[])
        except Exception as e:
            logger.error(f"Error in get_product_recommendations: {str(e)}")
            raise

    async def get_category_products(
        self,
        query: Optional[str] = None,
        current: int = 1,
        page_size: int = 5
    ) -> List[List[str]]:
        response = await ProductClient.combine_search(
            query=query,
            current=current,
            page_size=page_size
        )
        if response and response.data and response.data.records:
            return [
                [product.productName, product.sellPriceCur, str(product.sellPrice)]
                for product in response.data.records
            ]
        return []


    async def recommendations_web(
        self,
        user_query: str,
        num_products: int = 3,
        stream: bool = True
    ):
        try:
            query_message, language, requirements = await self.llm_service.extract_user_needs(user_query)
            # 并发执行网页内容获取和商品库查询
            web_search_results, category_products = await asyncio.gather(
                self._fetch_web_content(query_message + " 购买 推荐", language="zh-CN"),
                self.get_category_products(query=query_message)
            )

            print("web_search_results", web_search_results)
            print("category_products", category_products)
            
            # 调用LLM处理
            if stream:
                # 流式模式
                logger.info(f"使用流式模式处理推荐请求: {user_query}")
                return await self.llm_service.select_best_products_from_web(
                    user_query=user_query,
                    web_search_result=web_search_results,
                    num_products=num_products,
                    language=language,
                    category_products=category_products,
                    stream=True
                )
            else:
                recommendations = await self.llm_service.select_best_products_from_web(
                    user_query=user_query,
                    web_search_result=web_search_results,
                    num_products=num_products,
                    language=language,
                    category_products=category_products,
                    stream=False
                )
                return recommendations
            
        except Exception as e:
            logger.error(f"Web推荐流程异常: {str(e)}")
            raise e

    async def _fetch_web_content(self, query_message: str, language: Optional[str] = None) -> List[str]:
        start_time = perf_counter()
        try:
            # 1. 执行Google搜索
            logger.info(f"执行Google搜索: {query_message}")
            search_results = self.google_search.search(
                query_message,
                # language=language,
                exclude_sites= EXCLUDED_SITES,
                num_results=5
            )
            logger.info(f"Google搜索结果: {search_results}")
            
            # 2. 提取并去重URL
            urls = list({result.formattedUrl for result in search_results.items})
            logger.info(f"提取的URL: {urls}, {len(urls)}")
            
            # 3. 使用爬虫客户端爬取网页内容
            web_search_results = []
            try:
                crawl_response = await crawler_client.crawl_fastest(
                    urls=urls,
                    count=3,
                    min_word_count=800
                )
                
                if crawl_response.success:
                    for result in crawl_response.results:
                        if result.success and result.content and len(result.content) > 50:
                            web_search_results.append(process_text(result.content[50:5000]))
                else:
                    logger.error(f"爬虫服务调用失败: {crawl_response.message}")
                    
            except Exception as crawl_error:
                logger.error(f"网页爬取失败: {str(crawl_error)}")
            
            return web_search_results
        finally:
            end_time = perf_counter()
            logger.info(f"_fetch_web_content执行时间: {end_time - start_time:.2f}秒")

    async def get_category_products(
        self,
        query: Optional[str] = None,
        current: int = 1,
        page_size: int = 5
    ) -> List[List[str]]:
        start_time = perf_counter()
        try:
            self._clean_expired_cache()
            
            cache_key = f"{query}_{current}_{page_size}"
            
            if cache_key in self._category_products_cache:
                cached_results, timestamp = self._category_products_cache[cache_key]
                if time() - timestamp < self._cache_ttl:
                    self._update_cache_access_history(cache_key)
                    logger.info(f"使用缓存的商品数据: {cache_key}")
                    return cached_results
            
            response = await ProductClient.combine_search(
                query=query,
                current=current,
                page_size=page_size
            )
            
            results = []
            if response and response.data and response.data.records:
                results = [
                    [product.productName, product.sellPriceCur, str(product.sellPrice)]
                    for product in response.data.records
                ]
            
            if len(self._category_products_cache) >= self._max_cache_size:
                self._apply_lru_policy()
                
            # 更新访问历史
            self._category_products_cache[cache_key] = (results, time())
            self._update_cache_access_history(cache_key)
            
            return results
        finally:
            end_time = perf_counter()
            logger.info(f"get_category_products执行时间: {end_time - start_time:.2f}秒")

    async def recommendations_web_v2( self,
        user_query: str,
        num_products: int = 3
    ):
        try:
            query_message, language, requirements = await self.llm_service.extract_user_needs(user_query)
            # 并发执行网页内容获取和商品库查询
            web_search_results, category_products = await asyncio.gather(
                self._fetch_web_content(query_message + " 购买 推荐", language="zh-CN"),
                self.get_category_products(query=query_message)
            )

            print("web_search_results", web_search_results)
            print("category_products", category_products)
            # 调用LLM服务并返回流式响应
            return self.llm_service.select_best_products_from_web_v2(
                user_query=user_query,
                web_search_result=web_search_results,
                num_products=num_products,
                language=language,
                category_products=category_products
            )
        except Exception as e:
            logger.error(f"Web推荐流程异常: {str(e)}")
            raise e