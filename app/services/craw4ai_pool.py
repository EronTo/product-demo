import asyncio
import logging
import time
from typing import List, Any, Optional

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher


logger = logging.getLogger(__name__)

class CrawlerPool:
    """
    A pool of AsyncWebCrawler instances for efficient crawling operations.
    """
    
    def __init__(
        self, 
        n_crawlers: int = 10,
        browser_config: Optional[BrowserConfig] = None,
        crawler_run_config: Optional[CrawlerRunConfig] = None,
        dispatcher: Optional[MemoryAdaptiveDispatcher] = None
    ):
        """
        Initialize crawler pool with n crawler instances.
        
        Args:
            n_crawlers: Number of crawler instances to create
            browser_config: Optional browser configuration
            crawler_run_config: Optional crawler run configuration
            dispatcher: Optional memory adaptive dispatcher
        """
        self.n_crawlers = n_crawlers
        self.browser_config = browser_config or self._default_browser_config()
        self.crawler_run_config = crawler_run_config or self._default_crawler_run_config()
        self.dispatcher = dispatcher or self._default_dispatcher()
        self.crawlers = []
        self.available_crawlers = []
        self.lock = asyncio.Lock()
        self.initialized = False
    
    @staticmethod
    def _default_browser_config() -> BrowserConfig:
        """Create default browser configuration."""
        return BrowserConfig(
            headless=True,
            text_mode=True,
            light_mode=True,
            viewport_width=800,
            viewport_height=600,
            extra_args=[
                "--disable-extensions",
                "--disable-default-apps",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--disable-infobars"
            ]
        )
    
    @staticmethod
    def _default_crawler_run_config() -> CrawlerRunConfig:
        """Create default crawler run configuration."""
        markdown_generator = DefaultMarkdownGenerator(
            options={
                "ignore_images": True,
                "ignore_links": True,
                "body_width": 0
            }
        )
        
        return CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            wait_until="domcontentloaded",
            page_timeout=5000,
            excluded_tags=["script", "style", "svg", "img", "iframe", "noscript", "footer", "header", "nav", "aside"],
            word_count_threshold=30,
            markdown_generator=markdown_generator,
            stream=False
        )
        
    @staticmethod
    def _default_dispatcher() -> MemoryAdaptiveDispatcher:
        """Create default memory adaptive dispatcher."""
        return MemoryAdaptiveDispatcher(
            memory_threshold_percent=90.0,
            check_interval=5,
            max_session_permit=10,
        )
    
    async def init(self):
        """Initialize the crawler pool by creating n crawler instances."""
        if self.initialized:
            logger.info("Crawler pool already initialized")
            return
        
        tasks = []
        for i in range(self.n_crawlers):
            tasks.append(self._create_crawler(i))
        
        # Concurrently create all crawlers
        await asyncio.gather(*tasks)
        
        self.initialized = True
        logger.info(f"Crawler pool initialized with {len(self.crawlers)} available crawlers")
    
    async def _create_crawler(self, index: int):
        """Create a single crawler instance.
        
        Args:
            index: Crawler index for logging purposes
        """
        try:
            logger.info(f"Creating crawler {index+1}/{self.n_crawlers}...")
            crawler = AsyncWebCrawler(config=self.browser_config)
            await crawler.__aenter__()
            
            async with self.lock:
                self.crawlers.append(crawler)
                self.available_crawlers.append(crawler)
            
            logger.info(f"Crawler {index+1} successfully created")
        except Exception as e:
            logger.error(f"Error creating crawler {index+1}: {e}")
            raise
    
    async def _get_available_crawler(self):
        """Get an available crawler from the pool."""
        async with self.lock:
            while not self.available_crawlers:
                # Wait for a crawler to become available
                await asyncio.sleep(0.1)
            
            crawler = self.available_crawlers.pop()
            return crawler
    
    async def _release_crawler(self, crawler):
        """Release a crawler back to the available pool."""
        async with self.lock:
            self.available_crawlers.append(crawler)
    
    async def crawl(self, urls: List[str]) -> List[Any]:
        """
        Crawl a list of URLs using available crawlers from the pool.
        
        Args:
            urls: List of URLs to crawl
            
        Returns:
            List containing the results for each URL
        """
        if not self.initialized:
            await self.init()
        start_time = time.time()
        
        # Get a crawler from the pool
        crawler = await self._get_available_crawler()
        results = []
        try:
            # Use arun_many with the dispatcher
            results = await crawler.arun_many(
                urls=urls,
                config=self.crawler_run_config,
                dispatcher=self.dispatcher
            )
        except Exception as e:
            logger.error(f"Error during crawling: {e}")
            # Rethrow the exception after logging
            raise
        finally:
            await self._release_crawler(crawler)
        print("Crawling completed")
        end_time = time.time()
        total_time = end_time - start_time
        logger.info(f"Crawling completed in {total_time:.2f} seconds")
        
        return results


async def process_results(results: List[Any]):
    """Process and display crawling results.
    
    Args:
        results: List of crawling results
    """
    for i, result in enumerate(results):
        logger.info(f"Result {i+1}:")
        
        if not hasattr(result, 'success') or not result.success:
            error_msg = getattr(result, 'error_message', 'Unknown error')
            logger.error(f"Crawling failed: {error_msg}")
            continue
            
        if not hasattr(result, 'markdown') or not result.markdown:
            logger.warning(f"Result has no markdown attribute: {result}")
            continue
            
        # Extract and display markdown content
        markdown_content = ""
        if hasattr(result.markdown, 'raw_markdown'):
            markdown_content = result.markdown.raw_markdown
        else:
            markdown_content = str(result.markdown)
            
        # Only display first 1000 chars
        preview = markdown_content[:1000] + "..." if len(markdown_content) > 1000 else markdown_content
        logger.info(f"Markdown content (preview):\n{preview}")

async def main():
    """Example usage of the crawler pool."""
    pool = None
    try:
        pool = CrawlerPool(n_crawlers=3)
        await pool.init()
        
        # Example URL to crawl
        urls = ["https://zhuanlan.zhihu.com/p/262459884"]
        results = await pool.crawl(urls)
        await process_results(results)
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
    finally:
        if pool and pool.initialized:
            await pool.close()


if __name__ == "__main__":
    # Run the main function in an event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(main())
    except Exception as e:
        logger.error(f"Runtime error: {e}", exc_info=True)
    finally:
        loop.close()
        logger.info("Event loop closed")