from typing import List, Optional
from pydantic import BaseModel, Field

class MainImage(BaseModel):
    """商品主图模型"""
    width: int
    height: int
    url: str

class MainVideo(BaseModel):
    """商品视频模型"""
    videoUrl: Optional[str] = None
    vodUrl: Optional[None] = None
    previewUrl: Optional[None] = None
    width: Optional[None] = None
    height: Optional[None] = None

class ImageCollection(BaseModel):
    """商品图片集合模型"""
    width: int
    height: int
    url: str

class ImgDetail(BaseModel):
    """商品详情图模型"""
    width: int
    height: int
    url: str

class OptionValue(BaseModel):
    """商品选项值模型"""
    value: str
    image: Optional[str] = None
    imageWidth: Optional[None] = None
    imageHeight: Optional[None] = None

class ProductOption(BaseModel):
    """商品选项模型"""
    name: str
    type: int
    optionValues: List[OptionValue]

class ProductAttribute(BaseModel):
    """商品属性模型"""
    name: str
    value: str

class Product(BaseModel):
    """商品模型"""
    shopCode: Optional[str] = None
    productCode: str
    productName: str
    tenantCode: str
    brandName: Optional[str] = None
    mainImg: Optional[List[MainImage]] = None
    mainVideo: Optional[List[MainVideo]] = None
    imgCollection: List[ImageCollection]
    textDetail: Optional[None] = None
    imgDetail: List[ImgDetail]
    categoryId: int
    productOptions: List[ProductOption]
    productAttrs: List[ProductAttribute]
    sourcePlatform: str
    platformUrl: str
    platformProductId: str
    skuCode: str
    sellPriceCur: str
    sellPrice: str
    targetSellPrice: str
    targetSellCur: str

class SearchData(BaseModel):
    """搜索数据模型"""
    records: List[Product]
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
    placeholder: Optional[None] = None
    success: Optional[bool] = None