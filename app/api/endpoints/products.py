from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional

import logging

from app.services.recommendation import RecommendationService
from app.core.config import settings
from app.core.response_utils import ResponseUtils

logger = logging.getLogger(__name__)

router = APIRouter()

recommendation_service = RecommendationService()

@router.post("/chat/completion")
async def web_recommendations(
    user_query: str,
    num_products: int = Query(3, gt=0, le=settings.MAX_NUM_RECOMMENDATIONS)
):
    """
    基于网络搜索和网页内容分析的推荐流程，使用流式响应返回结果
    
    Args:
        user_query: 用户查询语句
        num_products: 需要推荐的商品数量
            
    Returns:
        StreamingResponse: 流式响应对象
    """
    
    if not user_query.strip():
        raise HTTPException(status_code=400, detail="用户查询不能为空")

    async def generate():
        try:
            logger.info(f"开始处理流式推荐请求: {user_query}")
            stream_response = await recommendation_service.recommendations_web(
                user_query = user_query,
                num_products = num_products
            )
            
            for chunk in stream_response:
                if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    if content:
                        logger.debug(f"发送数据: {content}")
                        yield content
                    
        except Exception as e:
            logger.error(f"流式处理出错: {e}", exc_info=True)
            yield "处理您的请求时发生错误，请稍后再试。"
    
    return StreamingResponse(
        generate(),
        media_type='text/plain; charset=utf-8'
    )

@router.get("/recommendations")
async def get_product_recommendations(
    user_query: str = Query(..., description="User's search query"),
    web_search: bool = Query(True, description="Whether to use web search"),
    nums_return: Optional[int] = Query(
        None, 
        description=f"Number of recommendations to return (default: {settings.DEFAULT_NUM_RECOMMENDATIONS}, max: {settings.MAX_NUM_RECOMMENDATIONS})"
    )
):
    try:
        # Log request
        logger.info(f"Received request for product recommendations: query='{user_query}'")
        
        # Validate nums_return
        if nums_return is not None and nums_return <= 0:
            raise HTTPException(status_code=400, detail="nums_return must be a positive integer")
            
        # Get recommendations from service
        recommendations = await recommendation_service.get_product_recommendations(
            user_query=user_query,
            web_search=web_search,
            nums_return=nums_return
        )
        
        # 返回响应数据
        return ResponseUtils.success(data=recommendations)
        
    except Exception as e:
        # Log error
        logger.error(f"Error processing recommendation request: {str(e)}")
        # Re-raise as HTTP exception with unified error format
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing recommendation request: {str(e)}"
        )