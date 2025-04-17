import logging
from app.core.context import get_request_id

class TraceIDFilter(logging.Filter):
    def filter(self, record):
        trace_id = get_request_id()
        record.trace_id = trace_id if trace_id else '-'
        return True