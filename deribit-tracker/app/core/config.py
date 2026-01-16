from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/deribit_db"
    SYNC_DATABASE_URL: str = "postgresql://user:password@localhost:5432/deribit_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Deribit
    DERIBIT_API_URL: str = "https://test.deribit.com/api/v2/public"
    DERIBIT_BASE_URL: str = "https://test.deribit.com"
    
    # App
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    ALLOWED_TICKERS: str = "BTC,ETH"  # Храним как строку
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    @property
    def allowed_tickers_list(self) -> List[str]:
        """Get allowed tickers as list."""
        # Фильтруем пустые строки и возвращаем как есть
        return [ticker.strip().upper() for ticker in self.ALLOWED_TICKERS.split(",") if ticker.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()