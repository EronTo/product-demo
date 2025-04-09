from typing import List
from pydantic import BaseModel, Field
from app.models.product import ProductRecommendation

class SelectProductsResponse(BaseModel):
    """
    产品推荐响应模型
    
    属性:
        selectProducts: 推荐产品列表
    """
    selectProducts: List[ProductRecommendation] = Field(..., description="推荐产品列表")