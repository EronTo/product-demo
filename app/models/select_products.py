from typing import List
from pydantic import BaseModel, Field
from app.models.product import ProductRecommendation

class SelectProductsResponse(BaseModel):
    selectProducts: List[ProductRecommendation] = Field(..., description="推荐产品列表")