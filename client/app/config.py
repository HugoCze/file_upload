import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Client application settings.
    
    Attributes:
        API_URL: URL of the API service.
        FILE_SIZE: Size of the test file to generate in bytes.
        TIMEOUT: Request timeout in seconds.
        FILE_EXTENSIONS: List of allowed file extensions.
    """
    API_URL: str = os.environ.get("API_URL", "http://localhost:8000")
    FILE_SIZE: int = int(os.environ.get("FILE_SIZE", 1024 * 1024 * 1024))  # Default: 1GB
    TIMEOUT: int = int(os.environ.get("TIMEOUT", 3600))  # Default: 1 hour
    FILE_EXTENSIONS: List[str] = ["txt", "pdf", "csv", "xlsx", "docx", "zip"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()