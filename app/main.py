import sys
import os
import logging

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import uvicorn
from app.core.context import set_request_id, clear_request_id, get_request_id

from app.core.config import settings
from app.core.pool_manager import PoolManager
from app.core.logging_config import setup_logging
from app.api.endpoints import products
from app.startup import setup_startup_handler

logger = setup_logging(
    log_level=getattr(logging, settings.LOG_LEVEL),
    log_to_file=True
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for product recommendations based on user queries",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup startup handler
setup_startup_handler(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all requests and their processing time.
    """

    trace_id = request.headers.get("X-Trace-ID")
    trace_id = set_request_id(trace_id)
    
    start_time = time.time()
    
    # Get client IP
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path} from {client_ip} - Trace ID: {trace_id}")
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(f"Response: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s - Trace ID: {trace_id}")
        
        # Add processing time and trace ID headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Trace-ID"] = trace_id
        
        return response
    except Exception as e:
        # Log error
        logger.error(f"Error processing request: {request.method} {request.url.path} - {str(e)} - Trace ID: {trace_id}")
        
        # Return error response with unified format
        error_response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "data": {"detail": "Internal server error"},
                "traceId": trace_id
            },
        )
        error_response.headers["X-Trace-ID"] = trace_id
        return error_response
    finally:
        clear_request_id()

# HTTPException handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Exception handler for HTTPException to ensure unified response format.
    """
    logger.error(f"HTTP exception: {str(exc)}", exc_info=True)
    trace_id = get_request_id() or '-'
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "data": {"detail": str(exc.detail)},
            "traceId": trace_id
        },
        headers=exc.headers,
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to log all unhandled exceptions.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    trace_id = get_request_id() or '-'
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "data": {"detail": "An unexpected error occurred"},
            "traceId": trace_id
        },
    )

# Include routers
app.include_router(products.router, prefix=f"{settings.API_V1_STR}")

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint that returns a welcome message.
    """
    logger.debug("Root endpoint called")
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

# Health check endpoint
@app.get("/health")
async def health():
    """
    Health check endpoint.
    """
    logger.debug("Health check endpoint called")
    return {"status": "healthy"}

# Run the application using uvicorn
if __name__ == "__main__":
    logger.info("Starting application")
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8081, 
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )