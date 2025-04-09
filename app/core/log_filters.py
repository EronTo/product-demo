import logging
from app.core.context import get_request_id

class TraceIDFilter(logging.Filter):
    """
    日志过滤器，用于在日志记录中添加trace_id
    """
    def filter(self, record):
        trace_id = get_request_id()
        record.trace_id = trace_id if trace_id else '-'
        return True