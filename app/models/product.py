from pydantic import BaseModel, Field, HttpUrl
from typing import Optional

class ProductBase(BaseModel):
    """
    Base product model with common attributes.
    """
    product_name: str
    product_id: str
    price: str
    main_image: str
    product_url: str
    
class ProductRecommendation(ProductBase):
    """
    Product recommendation model with additional recommendation text.
    """
    origin_recommendation: str = Field(..., description="Original recommendation from the model")
    recommendation: str = Field(..., description="Enhanced recommendation")

class ProductQuery(BaseModel):
    """
    Query model for product recommendations.
    """
    user_query: str = Field(..., description="User query string")
    web_search: bool = Field(True, description="Flag to indicate if web search should be used")
    nums_return: Optional[int] = Field(None, description="Number of results to return")