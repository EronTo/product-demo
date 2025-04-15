from typing import List, Optional
from pydantic import BaseModel, Field

class MainImage(BaseModel):
    """商品主图模型"""
    width: Optional[int] = None
    height: Optional[int] = None
    url: Optional[str] = None

class MainVideo(BaseModel):
    """商品视频模型"""
    videoUrl: Optional[str] = None
    vodUrl: Optional[str] = None
    previewUrl: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None

class ImageCollection(BaseModel):
    """商品图片集合模型"""
    width: Optional[int] = None
    height: Optional[int] = None
    url: Optional[str] = None

class ImgDetail(BaseModel):
    """商品详情图模型"""
    width: Optional[int] = None
    height: Optional[int] = None
    url: Optional[str] = None

class OptionValue(BaseModel):
    """商品选项值模型"""
    value: Optional[str] = None
    image: Optional[str] = None
    imageWidth: Optional[str] = None
    imageHeight: Optional[str] = None

class ProductOption(BaseModel):
    """商品选项模型"""
    name: Optional[str] = None
    type: Optional[int] = None
    optionValues: Optional[List[OptionValue]] = None

class ProductAttribute(BaseModel):
    """商品属性模型"""
    name: Optional[str] = None
    value: Optional[str] = None

class Product(BaseModel):
    """商品模型"""
    shopCode: Optional[str] = None
    productCode: Optional[str] = None
    productName: Optional[str] = None
    tenantCode: Optional[str] = None
    brandName: Optional[str] = None
    mainImg: Optional[List[MainImage]] = None
    mainVideo: Optional[List[MainVideo]] = None
    imgCollection: Optional[List[ImageCollection]] = None
    textDetail: Optional[str] = None
    imgDetail: Optional[List[ImgDetail]] = None
    categoryId: Optional[int] = None
    productOptions: Optional[List[ProductOption]] = None
    productAttrs: Optional[List[ProductAttribute]] = None
    sourcePlatform: Optional[str] = None
    platformUrl: Optional[str] = None
    platformProductId: Optional[str] = None
    skuCode: Optional[str] = None
    sellPriceCur: Optional[str] = None
    sellPrice: Optional[str] = None
    targetSellPrice: Optional[str] = None
    targetSellCur: Optional[str] = None

class SearchData(BaseModel):
    """搜索数据模型"""
    records: Optional[List[Product]] = None
    total: Optional[int] = None
    pageSize: Optional[int] = None
    current: Optional[int] = None
    totalPages: Optional[int] = None

class CombineSearchResponse(BaseModel):
    """组合搜索响应模型"""
    code: Optional[int] = None
    message: Optional[str] = None
    data: Optional[SearchData] = None
    traceId: Optional[str] = None
    placeholder: Optional[str] = None
    success: Optional[bool] = None