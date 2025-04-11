from typing import List, Optional
from app.models import google_search
from app.models.product import ProductRecommendation
from app.core.config import settings
import logging
from app.models.select_products import SelectProductsResponse
from app.models.combine_search import CombineSearchResponse
from app.services.product_client import ProductClient
from typing import List
from app.services.google_search import GoogleSearchService
from app.services.llm_service import LLMService
from app.services.craw4ai_pool import CrawlerPool

logger = logging.getLogger(__name__)

class RecommendationService:
    """
    Service for handling product recommendations based on user queries.
    """
    
    def __init__(self):
        """Initialize the RecommendationService with required dependencies."""
        self.llm_service = LLMService()
        self.crawler_pool = CrawlerPool(n_crawlers=3)
        self.google_search = GoogleSearchService()
    
    async def init(self):
        """Initialize async resources."""
        await self.crawler_pool.init()
    
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

            # In a real implementation:
            # 1. Process user query
            # 2. If web_search is True, perform web search to find products
            # 3. Generate recommendations using language models
            
            # For now, return mock data
            if settings.USE_MOCK_DATA:
                return SelectProductsResponse(selectProducts=RecommendationService._get_mock_recommendations(nums_return))
            
            return SelectProductsResponse(selectProducts=[])
        except Exception as e:
            logger.error(f"Error in get_product_recommendations: {str(e)}")
            raise

    async def get_category_products(
        query: Optional[str] = None,
        current: int = 1,
        page_size: int = 5
    ) -> CombineSearchResponse:
        return await ProductClient.get_category_products(query, current, page_size)


    def _get_mock_recommendations(count: int) -> List[ProductRecommendation]:
        """
        Generate mock product recommendations for testing.
        
        Args:
            count: Number of recommendations to return
            
        Returns:
            List of mock product recommendations
        """
        mock_data = [
            ProductRecommendation(
                product_name="Asics亚瑟士网球鞋 RESOLUTION 8",
                product_id="SP01250405255",
                origin_recommendation="这款网球鞋以其出色的缓冲性和稳定性著称，特别适合追求稳定型的选手。鞋面设计提供了良好的支撑，适合长时间的训练和比赛。",
                recommendation="这款Asics亚瑟士网球鞋RESOLUTION 8非常适合您这位追求稳定型的男士网球选手。首先，它的设计注重稳定性，能够提供良好的支撑，这对于长时间的训练和比赛来说至关重要。鞋面采用的是高密度材料，能够提供全面的支撑，无论您是进行快速移动还是急停截击，都能保持脚部的稳定。此外，这款鞋采用了GEL缓震技术，能够在您进行高强度的比赛提供出色的缓震效果，有效减轻膝盖和脚踝的冲击，保护您的身体。鞋底采用了DURALAST高密度橡胶，具有出色的耐磨性和防滑性能，即使在硬地球场上也能保持良好的抓地力。也就是说，这款Asics亚瑟士网球鞋RESOLUTION 8不仅具备出色的稳定性和支撑性，还能够提供卓越的缓震和耐磨性能，非常适合您这样的网球选手。",
                main_image="https://img.alicdn.com/bao/uploaded/i2/2044146822/O1CN01HMIhkC20GWzaJGjYh_!!2044146822.jpg",
                price="619",
                product_url="https://item.taobao.com/item.htm?id=703046969236"
            ),
            ProductRecommendation(
                product_name="YONEX尤尼克斯 ECLIPSION4网球鞋",
                product_id="SP01250439793",
                origin_recommendation="全场地通用，缓震回弹，耐磨舒适，适合各种场地和比赛需求。鞋底设计提供了良好的抓地力，适合快速移动和急停。",
                recommendation="这款YONEX尤尼克斯ECLIPSION4网球鞋非常适合您这位追求舒适性和多功能性的男士网球选手。首先，它是一款全场地通用的网球鞋，无论是硬地球场还是泥地球场，都能适应自如。鞋底设计采用了先进的材料和技术，提供了出色的抓地力，无论您是在快速移动还是急停截击时，都能保持良好的稳定性。此外，这款鞋采用了ECLIPSION 4系列的专业设计，能够提供良好的缓震和回弹效果，确保您在比赛中能够迅速调整姿态，做出最佳反应。鞋面采用透气材料，确保在长时间的训练和比赛中也能保持脚部的干爽舒适。也就是说，这款YONEX尤尼克斯ECLIPSION4网球鞋不仅具备出色的抓地力和缓震性能，还能够适应多种比赛需求，非常适合您这样的网球选手。",
                main_image="https://img.alicdn.com/bao/uploaded/i1/2212450322936/O1CN01IU4kJV1XYjlik9aHK_!!2212450322936.jpg",
                price="559",
                product_url="https://item.taobao.com/item.htm?id=695925300499"
            ),
            ProductRecommendation(
                product_name="Asics亚瑟士网球鞋 RS9",
                product_id="SP01250405255",
                origin_recommendation="亚瑟士新款，缓震稳定舒适，特别适合快速进攻型球员。鞋面更灵活，延伸的DynaWall中足稳定科技使鞋更稳定，适合高强度比赛。",
                recommendation="这款Asics亚瑟士网球鞋RS9非常适合您这位追求快速进攻型打法的男士网球选手。首先，它采用了最新的缓震技术和稳定的DynaWall中足稳定科技，能够在高强度比赛中提供出色的舒适性和稳定性。鞋面采用了更灵活的设计，能够更好地适应快速的移动和变向，确保您在比赛中能够迅速做出反应。此外，这款鞋的鞋底采用了DURALAST高密度橡胶，具有出色的耐磨性和防滑性能，即使在硬地球场上也能保持良好的抓地力。也就是说，这款Asics亚瑟士网球鞋RS9不仅具备出色的缓震和稳定性，还能够适应快速进攻型的打法，非常适合您这样的网球选手。",
                main_image="https://img.alicdn.com/bao/uploaded/i2/2044146822/O1CN01HMIhkC20GWzaJGjYh_!!2044146822.jpg",
                price="619",
                product_url="https://item.taobao.com/item.htm?id=703046969236"
            ),
            ProductRecommendation(
                product_name="HEAD海德网球鞋 SPRINT PRO 3.5",
                product_id="SP01250467821",
                origin_recommendation="这款网球鞋专为职业选手设计，提供出色的稳定性和灵活性。适合快速移动和变向，耐磨防滑，适合各种场地使用。",
                recommendation="这款HEAD海德网球鞋SPRINT PRO 3.5非常适合您这位追求专业性能的男士网球选手。首先，它采用了专业级的设计理念，能够在保证稳定性的同时提供出色的灵活性，这对于高水平的比赛和训练至关重要。鞋面采用了轻量化的材料，减轻了脚部负担，同时保证了足够的支撑性。此外，这款鞋的鞋底采用了特殊的橡胶材料，具有出色的耐磨性和防滑性能，无论是硬地、红土还是草地球场，都能提供良好的抓地力。鞋垫采用了人体工学设计，能够有效减轻长时间比赛和训练对脚部的压力。也就是说，这款HEAD海德网球鞋SPRINT PRO 3.5不仅具备专业级的性能表现，还能够适应各种球场环境，非常适合您这样追求高水平表现的网球选手。",
                main_image="https://img.alicdn.com/bao/uploaded/i3/2212450322936/O1CN01S6s9Ty1XYjlbwOmRl_!!2212450322936.jpg",
                price="729",
                product_url="https://item.taobao.com/item.htm?id=698452784532"
            ),
            ProductRecommendation(
                product_name="Wilson威尔胜网球鞋 RUSH PRO 4.0",
                product_id="SP01250485723",
                origin_recommendation="威尔胜高端款，轻量化设计，提供极佳的稳定性和舒适度。特殊的鞋底纹路增强抓地力，适合快速移动和变向。",
                recommendation="这款Wilson威尔胜网球鞋RUSH PRO 4.0非常适合您这位追求轻量化和舒适度的男士网球选手。首先，它采用了轻量化的设计理念，在保证支撑性的同时显著减轻了鞋的重量，这对于提高移动速度和减少疲劳感至关重要。鞋面采用了透气的网布材质，确保在长时间的比赛和训练中保持脚部的干爽舒适。此外，这款鞋的鞋底设计了特殊的纹路，能够提供极佳的抓地力，无论是快速启动、急停还是变向，都能保持良好的控制力。鞋内采用了专业的缓震系统，能够有效吸收冲击力，减轻关节的压力。也就是说，这款Wilson威尔胜网球鞋RUSH PRO 4.0不仅具备出色的轻量化和舒适度，还能够提供极佳的稳定性和抓地力，非常适合您这样的网球选手。",
                main_image="https://img.alicdn.com/bao/uploaded/i4/2212450322936/O1CN01iOzREr1XYjlhK3bCo_!!2212450322936.jpg",
                price="789",
                product_url="https://item.taobao.com/item.htm?id=694356721423"
            )
        ]
        
        # Return the requested number of recommendations
        return mock_data[:count]


    async def recommendations_web(
        self,
        user_query: str,
        num_products: int = 3,
        stream: bool = True
    ):
        """
        基于网络搜索和网页内容分析的推荐流程
        
        Args:
            user_query: 用户查询语句
            num_products: 需要推荐的商品数量
            stream: 是否使用流式返回
            
        Returns:
            结构化推荐结果列表或字符串，或者在流式模式下返回流式响应
        """
        try:
            # 提取推荐词
            query_message = await self.llm_service.extract_user_needs(user_query)
            # 1. 执行Google搜索
            logger.info(f"执行Google搜索: {query_message}")
            google_search = GoogleSearchService()
            search_results = google_search.search(
                query_message,
                exclude_sites= "site:zhihu.com/column site:zhihu.com/question site:www.bilibili.com/ site:www.jd.com/ site:www.mi.com/ site:www.taobao.com/ site:www.tmall.com/ site:www.douyin.com/ site:https://m.bilibili.com/ site:https://www.reddit.com/"
            )
            logger.info(f"Google搜索结果: {search_results}")
            # 2. 提取并去重URL
            urls = list({result.formattedUrl for result in search_results.items})
            # urls = ['https://zhuanlan.zhihu.com/p/260093867', 'https://tw.my-best.com/114851', 'https://zhuanlan.zhihu.com/p/409731335']
            logger.info(f"提取的URL: {urls}")
            web_search_results = []
            try:
                results = await self.crawler_pool.crawl_fastest(urls, 3, 1000)
                for result in results:
                    if result is not None and result.markdown.raw_markdown is not None and len(result.markdown.raw_markdown) > 100:
                        web_search_results.append(result.markdown.raw_markdown[:5000])
            except Exception as crawl_error:
                logger.error(f"网页爬取失败: {str(crawl_error)}")
                raise crawl_error
            # 4. 调用LLM处理
            if stream:
                # 流式模式
                logger.info(f"使用流式模式处理推荐请求: {user_query}")
                return await self.llm_service.select_best_products_from_web(
                    user_query=user_query,
                    web_search_result=web_search_results,
                    num_products=num_products,
                    stream=True
                )
            else:
                recommendations = await self.llm_service.select_best_products_from_web(
                    user_query=user_query,
                    web_search_result=web_search_results,
                    num_products=num_products
                )
                return recommendations
            
        except Exception as e:
            logger.error(f"Web推荐流程异常: {str(e)}")
            raise e

