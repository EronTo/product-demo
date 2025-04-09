import pytest
from app.services.craw4ai_pool import CrawlerPool, process_results

@pytest.mark.asyncio
async def test_crawler_pool_crawl():
    pool = CrawlerPool(n_crawlers=2)  
    await pool.init()
    """Test crawler pool crawling functionality."""
    urls = ["https://zhuanlan.zhihu.com/p/262459884"]
    results = await pool.crawl(urls)
    
    assert isinstance(results, list)
    assert len(results) == len(urls)

@pytest.mark.asyncio
async def test_process_results():
    """Test result processing functionality."""
    # Mock result with success
    class MockResult:
        def __init__(self, success=True, markdown_content="Test content"):
            self.success = success
            self.markdown = type('MockMarkdown', (), {'raw_markdown': markdown_content})()
    
    results = [MockResult()]
    await process_results(results)
    
    # Mock result with failure
    failed_result = MockResult(success=False)
    failed_result.error_message = "Test error"
    results = [failed_result]
    await process_results(results)
