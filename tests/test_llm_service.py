import pytest
from unittest.mock import AsyncMock, patch
from app.services.llm_service import LLMService
from app.core.config import settings

# @pytest.mark.asyncio
# async def test_get_product_recommendations_real_api():
#     # 使用真实API进行网球鞋推荐测试
#     llm_service = LLMService()
#     result = await llm_service.get_product_recommendations("我需要一双网球鞋")
    
#     print("测试结果11：", result)
    

@pytest.mark.asyncio
async def test_select_best_products_from_web():
    user_query = "寻找适合硬地球场的男士网球鞋"
    web_search_result = """
    1. Asics Gel-Resolution 8 - 适合硬地球场，缓震优秀
    2. Nike Air Zoom Vapor Pro - 轻量灵活
    3. Adidas Barricade - 高支撑性
    """
    
    llm_service = LLMService()
    result = await llm_service.select_best_products_from_web(
        user_query=user_query,
        web_search_result=web_search_result,
        num_products=3
    )
    
    print("\n测试结果:", result)
    # assert result is not None
    # assert isinstance(result, str)
    # assert len(result.strip()) > 0
    # assert "推荐" in result or "建议" in result  # 验证包含推荐关键词
    # assert "Asics" in result or "Nike" in result  # 验证包含产品品牌
    