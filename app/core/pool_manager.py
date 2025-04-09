from typing import Optional
from app.services.craw4ai_pool import CrawlerPool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class PoolManager:
    _instance: Optional['PoolManager'] = None
    _pool: Optional[CrawlerPool] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def initialize_pool(cls):
        if cls._pool is None:
            logger.info("Initializing crawler pool with config: %s", settings.__dict__)
            cls._pool = CrawlerPool(
                n_crawlers=settings.MAX_CONCURRENT_REQUESTS,
                browser_config=None,
                crawler_run_config=None,
                dispatcher=None
            )
            await cls._pool.init()
            logger.info("Crawler pool initialized successfully")

    @classmethod
    async def get_pool(cls) -> CrawlerPool:
        if cls._pool is None:
            await cls.initialize_pool()
        return cls._pool

    @classmethod
    async def close_pool(cls):
        if cls._pool is not None:
            logger.info("Closing crawler pool")
            cls._pool = None
            logger.info("Crawler pool closed successfully")