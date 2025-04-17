from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

class BaseConfig(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Product Recommendation API"
    
    USE_MOCK_DATA: bool = True
    
    DEFAULT_NUM_RECOMMENDATIONS: int = 5
    
    MAX_NUM_RECOMMENDATIONS: int = 3
    
    LOG_LEVEL: str = "INFO"
    LOG_TO_FILE: bool = True
    
    BACKEND_CORS_ORIGINS: list = ["*"]

    MAX_CONCURRENT_REQUESTS: int = 2
    
    PRODUCT_API_BASE_URL: str = "https://api.example.xyz"
    
    GOOGLE_API_KEY: Optional[str] = "API_KEY_PLACEHOLDER"
    GOOGLE_CX_ID: str = "CX_ID_PLACEHOLDER"
    
    API_REFERER: str = "https://www.example.ai/"
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> list:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


class AIConfig(BaseSettings):
    OPENAI_API_KEY: Optional[str] = "API_KEY_PLACEHOLDER"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"

    DOUBAO_API_KEY: Optional[str] = "API_KEY_PLACEHOLDER"
    DOUBAO_BASE_URL: str = "https://api.siliconflow.cn/v1/"
    DOUBAO_MODEL: str = "Qwen/Qwen2.5-7B-Instruct"

    VLLM_API_KEY: Optional[str] = "API_KEY_PLACEHOLDER"
    VLLM_BASE_URL: str = "http://0.0.0.0:8000/v1/"
    VLLM_MODEL: str = "Qwen/Qwen2.5-7B-Instruct"

    ALI_API_KEY: Optional[str] = "API_KEY_PLACEHOLDER"
    ALI_BASE_API: Optional[str] = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/"
    ALI_MODEL: Optional[str] = "qwen-turbo"
    ALI_MODEL_2: Optional[str] = "qwen-turbo"

    SILICONFLOW_API_KEY: Optional[str] = "API_KEY_PLACEHOLDER"
    SILICONFLOW_BASE_URL: Optional[str] = "https://api.siliconflow.cn/v1/"
    SILICONFLOW_MODEL: Optional[str] = "Qwen/Qwen2.5-7B-Instruct"

    OLLAMA_API_KEY: Optional[str] = "API_KEY_PLACEHOLDER"
    OLLAMA_BASE_URL: Optional[str] = "http://0.0.0.0:11343/v1/"
    OLLAMA_MODEL: Optional[str] = "qwen2.5:3b"
    
    OPENAI_TIMEOUT: int = 30
    
    OPENAI_RATE_LIMIT_RPM: int = 60
    
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0

    CRAWLER_SERVICE_URL: str = "http://0.0.0.0:8082"
    
    @field_validator("OPENAI_API_KEY", mode="before")
    @classmethod
    def validate_openai_api_key(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            logger.warning("OPENAI_API_KEY is not set. Some features may not work.")
        return v
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


class Settings(BaseConfig, AIConfig):
    pass


settings = Settings()