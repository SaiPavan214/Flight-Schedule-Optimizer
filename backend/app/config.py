import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./airport_ops.db")
    database_url_async: str = os.getenv("DATABASE_URL_ASYNC", "sqlite:///./airport_ops.db")
    
    # Google Gemini AI
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # CORS
    allowed_origins: List[str] = [
        "https://flight-schedule-optimizer.vercel.app",
        "http://localhost:3000",  # Add localhost for development
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()
