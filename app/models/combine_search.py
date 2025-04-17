from typing import List, Optional, Any
from pydantic import BaseModel, Field

class MainImage(BaseModel):
    width: Optional[Any] = None
    height: Optional[Any] = None
    url: Optional[Any] = None

class MainVideo(BaseModel):
    videoUrl: Optional[Any] = None
    vodUrl: Optional[Any] = None
    previewUrl: Optional[Any] = None
    width: Optional[Any] = None
    height: Optional[Any] = None

class ImageCollection(BaseModel):
    width: Optional[Any] = None
    height: Optional[Any] = None
    url: Optional[Any] = None

class ImgDetail(BaseModel):
    width: Optional[Any] = None
    height: Optional[Any] = None
    url: Optional[Any] = None

class OptionValue(BaseModel):
    value: Optional[Any] = None
    image: Optional[Any] = None
    imageWidth: Optional[Any] = None
    imageHeight: Optional[Any] = None

class ProductOption(BaseModel):
    name: Optional[Any] = None
    type: Optional[Any] = None
    optionValues: Optional[List[OptionValue]] = None

class ProductAttribute(BaseModel):
    name: Optional[Any] = None
    value: Optional[Any] = None

class Product(BaseModel):
    shopCode: Optional[Any] = None
    productCode: Optional[Any] = None
    productName: Optional[Any] = None
    tenantCode: Optional[Any] = None
    brandName: Optional[Any] = None
    mainImg: Optional[List[MainImage]] = None
    mainVideo: Optional[List[MainVideo]] = None
    imgCollection: Optional[List[ImageCollection]] = None
    textDetail: Optional[Any] = None
    imgDetail: Optional[List[ImgDetail]] = None
    categoryId: Optional[Any] = None
    productOptions: Optional[List[ProductOption]] = None
    productAttrs: Optional[List[ProductAttribute]] = None
    sourcePlatform: Optional[Any] = None
    platformUrl: Optional[Any] = None
    platformProductId: Optional[Any] = None
    skuCode: Optional[Any] = None
    sellPriceCur: Optional[Any] = None
    sellPrice: Optional[Any] = None
    targetSellPrice: Optional[Any] = None
    targetSellCur: Optional[Any] = None

class SearchData(BaseModel):
    records: Optional[List[Product]] = None
    total: Optional[Any] = None
    pageSize: Optional[Any] = None
    current: Optional[Any] = None
    totalPages: Optional[Any] = None

class CombineSearchResponse(BaseModel):
    code: Optional[Any] = None
    message: Optional[Any] = None
    data: Optional[SearchData] = None
    traceId: Optional[Any] = None
    placeholder: Optional[Any] = None
    success: Optional[bool] = None