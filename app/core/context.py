import uuid
import contextvars
from typing import Optional

_request_id_var = contextvars.ContextVar("request_id", default=None)


def generate_request_id() -> str:
    return str(uuid.uuid4())


def get_request_id() -> Optional[str]:
    return _request_id_var.get()


def set_request_id(request_id: Optional[str] = None) -> str:
    if request_id is None:
        request_id = generate_request_id()
    _request_id_var.set(request_id)
    return request_id


def clear_request_id() -> None:
    _request_id_var.set(None)