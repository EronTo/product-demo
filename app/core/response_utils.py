from typing import Any, Optional, TypeVar, Union
from fastapi import HTTPException
from app.models.response import ResponseModel, ErrorResponse
from app.core.context import get_request_id

T = TypeVar('T')

class ResponseUtils:
    """统一的响应工具类"""

    @staticmethod
    def success(data: T, code: int = 0) -> ResponseModel[T]:
        """生成成功响应

        Args:
            data: 响应数据
            code: 响应状态码，默认为0（成功）

        Returns:
            ResponseModel: 包含code、data和traceId的统一响应
        """
        return ResponseModel(
            code=code,
            data=data,
            traceId=get_request_id() or '-'
        )

    @staticmethod
    def error(message: str, code: int = 1) -> ResponseModel[ErrorResponse]:
        """生成错误响应

        Args:
            message: 错误信息
            code: 错误状态码，默认为1

        Returns:
            ResponseModel: 包含错误信息的统一响应
        """
        return ResponseModel(
            code=code,
            data=ErrorResponse(detail=message),
            traceId=get_request_id() or '-'
        )

    @staticmethod
    def handle_exception(exc: Exception) -> ResponseModel[ErrorResponse]:
        """处理异常并生成统一的错误响应

        Args:
            exc: 捕获的异常

        Returns:
            ResponseModel: 包含错误信息的统一响应
        """
        if isinstance(exc, HTTPException):
            return ResponseUtils.error(
                message=str(exc.detail),
                code=exc.status_code
            )
        # 其他类型的异常统一返回500错误
        return ResponseUtils.error(
            message=str(exc),
            code=500
        )