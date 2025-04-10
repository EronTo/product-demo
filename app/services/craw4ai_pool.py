import asyncio
import logging
import time
from typing import List, Any, Optional, Tuple, Dict
import os
import hashlib
import json
import aiofiles
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy


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
        dispatcher: Optional[MemoryAdaptiveDispatcher] = None,
        cache_dir: Optional[str] = None
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

        if cache_dir is None:
            self.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
        else:
            self.cache_dir = cache_dir
            
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        self.cache_files_map = {}
        self._load_cache_files_map()

    def _load_cache_files_map(self):
        try:
            if os.path.exists(self.cache_dir):
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.json'):
                        self.cache_files_map[filename] = True
                logger.info(f"Loaded {len(self.cache_files_map)} cache file names into memory")
        except Exception as e:
            logger.error(f"Error loading cache files: {e}")
    
    def add_to_cache_map(self, filename):
        self.cache_files_map[filename] = True    

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
            stream=True,
            scraping_strategy=LXMLWebScrapingStrategy()  # 使用LXML策略提高性能
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


    async def crawl_fastest(self, urls: List[str], count: int = 1, min_word_count: int = 100) -> List[Any]:
        """
        Crawl multiple URLs and return the fastest results that meet word count criteria.
        Uses local file cache when available to improve performance.
        
        Args:
            urls: List of URLs to crawl
            count: Number of results to return
            min_word_count: Minimum word count required for a valid result
                    
        Returns:
            List of fastest results meeting the word count criteria or top results by word count
        """
        # Initialize crawler if needed
        if not self.initialized:
            await self.init()
        
        start_time = time.time()
        valid_results = [] 
        all_results = []  
        
        # --- STEP 1: Prepare URLs and hash mapping ---
        url_hash_map = {url: hashlib.md5(url.encode()).hexdigest() for url in urls}
        
        # --- STEP 2: Process cached URLs ---
        urls_to_crawl = await self._process_cached_urls(url_hash_map, valid_results, all_results, count, min_word_count)
        
        # If we already have enough valid results or nothing to crawl, return results
        if len(valid_results) >= count or not urls_to_crawl:
            if len(valid_results) >= count:
                return valid_results[:count]
            else:
                all_results.sort(key=lambda x: getattr(x, 'word_count', 0), reverse=True)
                return all_results[:count]
        
        # --- STEP 3: Crawl remaining URLs ---
        crawler = await self._get_available_crawler()
        try:
            # Add any new results to our collections
            new_valid_results, new_all_results = await self._crawl_urls(
                crawler, urls_to_crawl, min_word_count, count - len(valid_results), start_time
            )
            valid_results.extend(new_valid_results)
            all_results.extend(new_all_results)
            
            # Return appropriate results
            if len(valid_results) >= count:
                return valid_results[:count]
            else:
                logger.info(f"Only found {len(valid_results)} valid results, returning top {count} results by word count")
                all_results.sort(key=lambda x: getattr(x, 'word_count', 0), reverse=True)
                return all_results[:count]
        finally:
            # Always release the crawler back to pool
            await self._release_crawler(crawler)
            
            end_time = time.time()
            total_time = end_time - start_time
            logger.info(f"Fastest crawling completed in {total_time:.2f} seconds")

    async def _process_cached_url(self, url: str, url_hash: str) -> Tuple[Optional[Any], int]:
        """
        Process a single cached URL, loading from file if available.
        
        Args:
            url: The URL to process
            url_hash: The MD5 hash of the URL
            
        Returns:
            Tuple of (result object, word count) or (None, 0) if cache not found/valid
        """
        cache_filename = f"{url_hash}.json"
        cache_file = os.path.join(self.cache_dir, cache_filename)
        
        if cache_filename not in self.cache_files_map:
            return None, 0
        
        try:
            # Try with aiofiles for async I/O
            try:
                async with aiofiles.open(cache_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    cache_data = json.loads(content)
            except ImportError:
                # Fall back to sync I/O if aiofiles not available
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
            
            # Create result object from cache data
            result = type('CachedResult', (), {})()
            result.url = url
            result.success = True
            
            # Add cached content to result
            if 'markdown' in cache_data:
                markdown_result = type('MarkdownGenerationResult', (), {})()
                markdown_result.raw_markdown = cache_data['markdown']
                result.markdown = markdown_result
            
            if 'html' in cache_data:
                result.html = cache_data['html']
            if 'cleaned_html' in cache_data:
                result.cleaned_html = cache_data['cleaned_html']
            
            # Calculate word count
            word_count = len(cache_data["markdown"])
            result.word_count = word_count
            result.from_cache = True
            logger.info(f"Loaded from cache: {url} with {word_count} words")
            
            return result, word_count
        except Exception as e:
            logger.error(f"Error loading cache for {url}: {e}")
            return None, 0

    async def _process_cached_urls(self, url_hash_map: Dict[str, str], 
                                valid_results: List[Any], 
                                all_results: List[Any],
                                count: int, 
                                min_word_count: int) -> List[str]:
        """
        Process URLs that might be cached, add valid results to collections.
        
        Args:
            url_hash_map: Mapping of URLs to their hash values
            valid_results: List to store valid results (modified in-place)
            all_results: List to store all results (modified in-place)
            count: Number of results needed
            min_word_count: Minimum word count threshold
            
        Returns:
            List of URLs that need to be crawled (not in cache or invalid)
        """
        urls_to_crawl = []
        
        # Separate URLs with and without cache
        urls_with_cache = []
        
        for url, url_hash in url_hash_map.items():
            cache_filename = f"{url_hash}.json"
            if cache_filename in self.cache_files_map:
                urls_with_cache.append((url, url_hash))
            else:
                urls_to_crawl.append(url)
        
        # Process URLs with cache in batches
        batch_size = 10
        for i in range(0, len(urls_with_cache), batch_size):
            batch = urls_with_cache[i:i + batch_size]
            batch_tasks = []
            
            # Create tasks for this batch
            for url, url_hash in batch:
                task = asyncio.create_task(self._process_cached_url(url, url_hash))
                batch_tasks.append((url, task))
            
            # Wait for all tasks in this batch
            for url, task in batch_tasks:
                try:
                    result, word_count = await task
                    if result:
                        all_results.append(result)
                        if word_count >= min_word_count:
                            valid_results.append(result)
                            # Return early if we have enough results
                            if len(valid_results) >= count:
                                logger.info(f"Found {len(valid_results)} valid results from cache, returning early.")
                                break
                    else:
                        urls_to_crawl.append(url)
                except Exception as e:
                    logger.error(f"Error processing cache for {url}: {e}")
                    urls_to_crawl.append(url)
            
            # Break early if we have enough results
            if len(valid_results) >= count:
                break
        
        return urls_to_crawl

    async def _crawl_urls(self, crawler: AsyncWebCrawler, 
                        urls: List[str], 
                        min_word_count: int,
                        needed_count: int,
                        start_time: float) -> Tuple[List[Any], List[Any]]:
        """
        Crawl a list of URLs using the provided crawler.
        
        Args:
            crawler: The crawler to use
            urls: List of URLs to crawl
            min_word_count: Minimum word count threshold
            needed_count: Number of valid results needed
            start_time: Start time for logging
            
        Returns:
            Tuple of (valid_results, all_results)
        """
        valid_results = []
        all_results = []
        
        # Create tasks for all URLs
        tasks = []
        for url in urls:
            task = asyncio.create_task(crawler.arun(
                url=url,
                config=self.crawler_run_config
            ))
            task.url = url
            tasks.append(task)
        
        # Wait for tasks to complete
        pending = set(tasks)
        
        while pending and len(valid_results) < needed_count:
            done, pending = await asyncio.wait(
                pending, 
                return_when=asyncio.FIRST_COMPLETED,
                timeout=None
            )
            
            # Process completed tasks
            for task in done:
                try:
                    result = task.result()
                    
                    # Extract markdown content and calculate word count
                    word_count = 0
                    markdown_content = None
                    
                    if hasattr(result, 'markdown') and result.markdown:
                        if hasattr(result.markdown, 'raw_markdown'):
                            markdown_content = result.markdown.raw_markdown
                            word_count = len(markdown_content.split())
                        else:
                            markdown_content = str(result.markdown)
                            word_count = len(markdown_content.split())
                    
                    # Cache the result
                    if markdown_content and hasattr(result, 'url'):
                        await self._cache_result(result, markdown_content)
                    
                    # Add to result collections
                    result.word_count = word_count
                    all_results.append(result)
                    
                    if word_count >= min_word_count:
                        valid_results.append(result)
                        logger.info(f"Found valid result for {task.url} with {word_count} words in {time.time() - start_time:.2f}s")
                    else:
                        logger.info(f"Result for {task.url} has only {word_count} words, minimum required is {min_word_count}")
                    
                    # Break early if we have enough results
                    if len(valid_results) >= needed_count:
                        break
                except Exception as e:
                    logger.error(f"Error crawling URL {task.url}: {e}")
            
            # Break early if we have enough results
            if len(valid_results) >= needed_count:
                break
        
        # Cancel remaining tasks
        for task in pending:
            if not task.done():
                task.cancel()
        
        # Handle cancelled tasks
        for task in pending:
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.debug(f"Task for {getattr(task, 'url', 'unknown')} cancelled with error: {e}")
        
        return valid_results, all_results

    async def _cache_result(self, result: Any, markdown_content: str) -> None:
        """
        Cache crawler result to file.
        
        Args:
            result: Crawler result to cache
            markdown_content: Markdown content to save
        """
        try:
            url_hash = hashlib.md5(result.url.encode()).hexdigest()
            cache_filename = f"{url_hash}.json"
            cache_file = os.path.join(self.cache_dir, cache_filename)
            
            cache_data = {
                'url': result.url,
                'timestamp': time.time(),
                'markdown': markdown_content
            }
            
            # Optionally save HTML content with size limits
            if hasattr(result, 'html') and result.html:
                cache_data['html'] = result.html[:10000]
            if hasattr(result, 'cleaned_html') and result.cleaned_html:
                cache_data['cleaned_html'] = result.cleaned_html[:10000]
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            # Update global cache mapping
            self.add_to_cache_map(cache_filename)
            
            logger.info(f"Cached result for {result.url}")
        except Exception as e:
            logger.error(f"Error caching result for {result.url}: {e}")

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
        urls = [
            "https://zhuanlan.zhihu.com/p/262459884",
            "https://github.com/unclecode/crawl4ai?tab=readme-ov-file",
            "https://zhuanlan.zhihu.com/p/27956936120"
        ]
        results = await pool.crawl_fastest(urls, count=1, min_word_count=1000)
        for i, result in enumerate(results):
            print(result.markdown.raw_markdown)
            # if result.success:
            #     logger.info(result.markdown.raw_markdown)
            # else:
            #     logger.error(f"Failed to crawl URL: {result.url}, Error: {result.error_message}")
        # await process_results(results)
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")


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