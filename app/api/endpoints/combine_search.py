from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from app.services.recommendation import RecommendationService
from app.models.combine_search import CombineSearchResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/product/no-auth/combineSearch", response_model=CombineSearchResponse)
async def combine_search(
    query: Optional[str] = Query(None, description="电商商品URL或商品搜索关键词"),
    current: Optional[int] = Query(1, description="当前页码"),
    page_size: Optional[int] = Query(10, description="分页大小"),
    image_url: Optional[str] = Query(None, description="商品图片URL")
):
    """
    组合搜索接口
    
    Args:
        query: 电商商品URL或商品搜索关键词
        current: 当前页码
        page_size: 每页数量
        image_url: 商品图片URL
        
    Returns:
        CombineSearchResponse: 组合搜索响应
    """
    try:
        if current < 1:
            raise HTTPException(status_code=400, detail="当前页码必须大于0")
        if page_size < 1:
            raise HTTPException(status_code=400, detail="每页数量必须大于0")
            
        response = await RecommendationService.combine_search(
            query=query,
            current=current,
            page_size=page_size,
            image_url=image_url
        )
        
        return response
        
    except Exception as e:
        logger.error(f"组合搜索请求处理失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"组合搜索请求处理失败: {str(e)}"
        )