from fastapi import FastAPI
from app.api.endpoints.products import recommendation_service
import asyncio

async def init_app(app: FastAPI):
    """Initialize application resources on startup."""
    await recommendation_service.init()
    
def setup_startup_handler(app: FastAPI):
    """Setup application startup handler."""
    app.add_event_handler("startup", lambda: asyncio.create_task(init_app(app)))
