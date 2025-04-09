import logging
import logging.config
import logging.handlers
import os
from pathlib import Path
import sys
import time
import threading
from concurrent_log_handler import ConcurrentRotatingFileHandler
from logging.handlers import TimedRotatingFileHandler
from app.core.context import get_request_id
from app.core.log_filters import TraceIDFilter

# 使用单例模式确保日志只初始化一次
_LOGGER_INITIALIZED = False
_LOGGER_LOCK = threading.Lock()

class CustomFormatter(logging.Formatter):
    """
    Custom formatter to add colors and extra information to logs
    """
    grey = "\x1b[38;20m"
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_str = "%(asctime)s | %(levelname)8s | %(trace_id)s | %(name)s:%(lineno)d | %(process)d | %(thread)d | %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: green + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset
    }

    def format(self, record):
        # 添加trace_id到日志记录中
        if not hasattr(record, 'trace_id'):
            trace_id = get_request_id()
            record.trace_id = trace_id if trace_id else '-'
        
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def setup_logging(log_level=logging.INFO, log_to_file=True):
    """
    Setup logging configuration for the application
    
    Args:
        log_level: Minimum log level to display
        log_to_file: Whether to log to a file
        
    Returns:
        Logger instance
    """
    global _LOGGER_INITIALIZED
    
    # 使用锁确保线程安全
    with _LOGGER_LOCK:
        if _LOGGER_INITIALIZED:
            return logging.getLogger(__name__)
        
        # 创建logs目录（如果不存在）
        logs_dir = Path("logs")
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # 使用固定的日志文件名，TimedRotatingFileHandler会自动添加日期后缀
        log_file = logs_dir / "app.log"
        
        # 基本配置
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s | %(levelname)8s | %(trace_id)s | %(name)s:%(lineno)d | %(process)d | %(thread)d | %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "simple": {
                    "format": "%(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": log_level,
                    "formatter": "default",
                    # "stream": sys.stdout,
                },
                "null": {
                    "class": "logging.NullHandler",
                },
            },
            "loggers": {
                "": {  # Root logger
                    "handlers": ["console"],
                    "level": log_level,
                    "propagate": True,
                },
                "uvicorn": {
                    "handlers": ["console"],
                    "level": logging.INFO,
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["console"],
                    "level": logging.INFO,
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["console"],
                    "level": logging.INFO,
                    "propagate": False,
                },
            },
        }
        
        # 添加文件处理器（如果需要）
        if log_to_file:
            try:
                # 使用TimedRotatingFileHandler实现按天轮换日志
                config["handlers"]["file"] = {
                    "class": "logging.handlers.TimedRotatingFileHandler",
                    "level": log_level,
                    "formatter": "default",
                    "filename": str(log_file),
                    "when": "midnight",  # 每天午夜轮换
                    "interval": 1,  # 每1天轮换一次
                    "backupCount": 10,  # 保留最近10天的日志
                    "encoding": "utf8",
                    "delay": True,  # 延迟创建文件直到第一次写入
                }
            except ImportError:
                # 如果导入失败，使用标准的TimedRotatingFileHandler
                config["handlers"]["file"] = {
                    "class": "logging.handlers.TimedRotatingFileHandler",
                    "level": log_level,
                    "formatter": "default",
                    "filename": str(log_file),
                    "when": "midnight",  # 每天午夜轮换
                    "interval": 1,  # 每1天轮换一次
                    "backupCount": 10,  # 保留最近10天的日志
                    "encoding": "utf8",
                    "delay": True,  # 延迟创建文件直到第一次写入
                }
            
            # 确保所有logger都使用文件处理器
            config["loggers"][""]["handlers"].append("file")
            config["loggers"]["uvicorn"]["handlers"].append("file")
            config["loggers"]["uvicorn.error"]["handlers"].append("file")
            config["loggers"]["uvicorn.access"]["handlers"].append("file")
        
        # 应用配置
        logging.config.dictConfig(config)
        
        # 为控制台处理器添加彩色格式化器
        console_handler = logging.getLogger().handlers[0]
        console_handler.setFormatter(CustomFormatter())
        
        # 为所有处理器添加TraceIDFilter
        trace_filter = TraceIDFilter()
        for logger_name in config["loggers"]:
            logger_obj = logging.getLogger(logger_name)
            for handler in logger_obj.handlers:
                handler.addFilter(trace_filter)
        
        # 记录配置信息
        logger = logging.getLogger(__name__)
        logger.info(f"Logging initialized with level: {logging.getLevelName(log_level)}")
        if log_to_file:
            logger.info(f"Logging to file: {log_file}")
        
        # 标记日志系统已初始化
        _LOGGER_INITIALIZED = True
        
        return logger