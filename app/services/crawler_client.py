import logging
import httpx
import asyncio
import json
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl

from app.core.config import settings

logger = logging.getLogger(__name__)


class CrawlRequest(BaseModel):
    urls: List[str] = Field(..., description="要爬取的URL列表")
    min_word_count: Optional[int] = Field(100, description="最小字数要求")
    count: Optional[int] = Field(1, description="需要返回的结果数量")
    use_cache: Optional[bool] = Field(True, description="是否使用缓存")
    extra_config: Optional[Dict[str, Any]] = Field(None, description="额外配置参数")


class MarkdownResult(BaseModel):
    """Markdown结果模型"""
    url: str
    content: str
    word_count: int
    from_cache: bool
    success: bool
    timestamp: float


class CrawlResponse(BaseModel):
    """爬取响应模型"""
    success: bool = Field(True, description="是否成功")
    message: str = Field("", description="消息")
    total_count: int = Field(0, description="总结果数")
    processed_urls: int = Field(0, description="处理的URL数量")
    elapsed_time: float = Field(0, description="耗时（秒）")
    results: List[MarkdownResult] = Field([], description="Markdown结果列表")
    trace_id: Optional[str] = Field(None, description="跟踪ID")


class CrawlerClient:
    """爬虫服务客户端，用于与爬虫服务通信"""
    
    def __init__(self, base_url: str = None, timeout: int = 60):
        """
        初始化爬虫客户端
        
        Args:
            base_url: 爬虫服务基础URL
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url or settings.CRAWLER_SERVICE_URL
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
        
    async def crawl(
        self, 
        urls: List[str], 
        count: int = 1, 
        min_word_count: int = 100,
        use_cache: bool = True
    ) -> CrawlResponse:
        """
        爬取URL列表
        
        Args:
            urls: 要爬取的URL列表
            count: 需要返回的结果数量
            min_word_count: 最小字数要求
            use_cache: 是否使用缓存
            
        Returns:
            爬取响应对象
        """
        try:
            request = CrawlRequest(
                urls=urls,
                count=count,
                min_word_count=min_word_count,
                use_cache=use_cache
            )
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/crawler/crawl",
                json=request.model_dump(),
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            return CrawlResponse(**response.json())
            
        except httpx.HTTPStatusError as e:
            logger.error(f"爬虫服务HTTP错误: {e.response.status_code} {e.response.text}")
            return CrawlResponse(
                success=False,
                message=f"爬虫服务HTTP错误: {e.response.status_code}",
            )
        except httpx.RequestError as e:
            logger.error(f"爬虫服务请求错误: {str(e)}")
            return CrawlResponse(
                success=False,
                message=f"爬虫服务请求错误: {str(e)}",
            )
        except Exception as e:
            logger.error(f"爬虫服务调用异常: {str(e)}")
            return CrawlResponse(
                success=False,
                message=f"爬虫服务调用异常: {str(e)}",
            )
            
    async def crawl_fastest(
        self, 
        urls: List[str], 
        count: int = 1, 
        min_word_count: int = 100,
        use_cache: bool = True
    ) -> CrawlResponse:
        """
        快速爬取URL列表
        
        Args:
            urls: 要爬取的URL列表
            count: 需要返回的结果数量
            min_word_count: 最小字数要求
            use_cache: 是否使用缓存
            
        Returns:
            爬取响应对象
        """
        try:
            request = CrawlRequest(
                urls=urls,
                count=count,
                min_word_count=min_word_count,
                use_cache=use_cache
            )
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/crawler/crawl/fastest",
                json=request.model_dump(),
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            return CrawlResponse(**response.json())
            
        except httpx.HTTPStatusError as e:
            logger.error(f"爬虫服务HTTP错误: {e.response.status_code} {e.response.text}")
            return CrawlResponse(
                success=False,
                message=f"爬虫服务HTTP错误: {e.response.status_code}",
            )
        except httpx.RequestError as e:
            logger.error(f"爬虫服务请求错误: {str(e)}")
            return CrawlResponse(
                success=False,
                message=f"爬虫服务请求错误: {str(e)}",
            )
        except Exception as e:
            logger.error(f"爬虫服务调用异常: {str(e)}")
            return CrawlResponse(
                success=False,
                message=f"爬虫服务调用异常: {str(e)}",
            )
            
    async def get_status(self) -> Dict[str, Any]:
        """
        获取爬虫服务状态
        
        Returns:
            状态信息
        """
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/crawler/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取爬虫服务状态异常: {str(e)}")
            return {
                "success": False,
                "message": f"获取爬虫服务状态异常: {str(e)}",
            }
            
    async def clear_cache(self) -> Dict[str, Any]:
        """
        清除爬虫服务缓存
        
        Returns:
            响应信息
        """
        try:
            response = await self.client.post(f"{self.base_url}/api/v1/crawler/clear-cache")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"清除爬虫服务缓存异常: {str(e)}")
            return {
                "success": False,
                "message": f"清除爬虫服务缓存异常: {str(e)}",
            }


# 创建单例爬虫客户端实例
crawler_client = CrawlerClient()


# 示例使用方法
async def example_usage():
    """爬虫客户端使用示例"""
    try:
        # 初始化客户端
        client = CrawlerClient(base_url="http://crawler-service:8082")
        
        # 爬取URL列表
        urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3"
        ]
        
        # 使用快速爬取
        response = await client.crawl_fastest(
            urls=urls,
            count=2,  # 需要2个结果
            min_word_count=500,  # 至少500字
            use_cache=True  # 使用缓存
        )
        
        if response.success:
            logger.info(f"爬取成功，获取到 {len(response.results)} 个结果")
            for i, result in enumerate(response.results):
                logger.info(f"结果 {i+1}: {result.url} ({result.word_count} 字)")
                # 处理结果内容
                # ...
        else:
            logger.error(f"爬取失败: {response.message}")
        
        # 关闭客户端
        await client.close()
        
    except Exception as e:
        logger.error(f"示例执行异常: {str(e)}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())