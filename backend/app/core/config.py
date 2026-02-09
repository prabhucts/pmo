"""
Configuration settings for the application
"""
from pydantic_settings import BaseSettings
from typing import List, Union
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "PMO Operations Solution"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./pmo.db"  # Default to SQLite for easy setup
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS as list"""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        return self.ALLOWED_ORIGINS
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB
    UPLOAD_DIR: str = "uploads"
    
    # Business Rules (defaults)
    DEFAULT_STORY_POINT_HOURS: int = 13
    DEFAULT_SPRINT_WEEKS: int = 2
    DEFAULT_WORKING_DAYS_PER_WEEK: int = 5
    DEFAULT_HOURS_PER_DAY: int = 8
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
