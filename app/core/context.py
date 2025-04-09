import uuid
import contextvars
from typing import Optional

_request_id_var = contextvars.ContextVar("request_id", default=None)


def generate_request_id() -> str:
    """
    生成一个唯一的请求ID
    
    Returns:
        str: 唯一的请求ID
    """
    return str(uuid.uuid4())


def get_request_id() -> Optional[str]:
    """
    获取当前请求的ID
    
    Returns:
        Optional[str]: 当前请求的ID，如果不存在则返回None
    """
    return _request_id_var.get()


def set_request_id(request_id: Optional[str] = None) -> str:
    """
    设置当前请求的ID
    
    Args:
        request_id: 要设置的请求ID，如果为None则自动生成
        
    Returns:
        str: 设置的请求ID
    """
    if request_id is None:
        request_id = generate_request_id()
    _request_id_var.set(request_id)
    return request_id


def clear_request_id() -> None:
    """
    清除当前请求的ID
    """
    _request_id_var.set(None)