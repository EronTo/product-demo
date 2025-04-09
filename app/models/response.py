from typing import Any, Generic, Optional, TypeVar, Dict
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel


# 定义泛型类型变量
T = TypeVar('T')

class ResponseModel(GenericModel, Generic[T]):
    """
    统一的API响应模型
    
    属性:
        code: 响应状态码，0表示成功，非0表示错误
        data: 响应数据，泛型类型
        traceId: 请求跟踪ID，用于日志追踪
    """
    code: int = Field(0, description="响应状态码，0表示成功，非0表示错误")
    data: T = Field(..., description="响应数据")
    traceId: str = Field(..., description="请求跟踪ID")

class ErrorResponse(BaseModel):
    """
    错误响应模型
    
    属性:
        detail: 错误详情
    """
    detail: str = Field(..., description="错误详情")