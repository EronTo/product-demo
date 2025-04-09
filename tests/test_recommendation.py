import pytest
from app.services.product_client import ProductClient
from app.models.combine_search import CombineSearchResponse, SearchData, Product

@pytest.mark.asyncio
async def test_combine_search_with_nike_query():
    """测试组合搜索接口，使用'Nike'作为查询关键词"""
    # 设置测试参数
    query = "鞋"
    current = 1
    page_size = 10
    
    # 调用组合搜索接口
    response = await ProductClient.combine_search(
        query=query,
        current=current,
        page_size=page_size
    )
    # 验证响应是否为CombineSearchResponse类型
    assert isinstance(response, CombineSearchResponse)
    
    # 验证响应状态码和成功标志
    assert response.code == 0
    assert response.success is True
    
    # 验证返回的数据结构
    assert response.data is not None
    assert isinstance(response.data, SearchData)
    
    # 验证分页信息
    assert response.data.current == current
    assert response.data.pageSize == page_size
    assert response.data.total >= 0
    assert response.data.totalPages >= 0
    
    # 验证返回的商品列表
    assert isinstance(response.data.records, list)
    if response.data.records:
        product = response.data.records[0]
        assert isinstance(product, Product)
        # 验证商品的必要字段
        assert product.productName is not None
        assert product.productCode is not None
        assert product.sellPrice is not None