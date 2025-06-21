from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Application
    app_name: str = "Personal Finance API"
    version: str = "1.0.0"
    debug: bool = False
    
    # Database
    database_url: str = "sqlite:///./finance.db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # External APIs
    currency_api_key: Optional[str] = None
    currency_api_url: str = "https://api.exchangerate-api.com/v4/latest"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
