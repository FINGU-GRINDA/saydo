from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    
    # Google OAuth
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    
    # Firebase Admin SDK
    firebase_project_id: str
    firebase_private_key_id: str
    firebase_private_key: str
    firebase_client_email: str
    firebase_client_id: str
    firebase_auth_uri: str
    firebase_token_uri: str
    firebase_auth_provider_cert_url: str
    firebase_client_cert_url: str
    
    # Deepgram
    deepgram_api_key: str = "demo-key"
    
    # Recall.ai (optional for cloud meeting bots)
    recall_ai_api_key: str = ""
    recall_ai_region: str = "us-west-2"
    
    # Zoom
    zoom_client_id: str = "demo-zoom-id"
    zoom_client_secret: str = "demo-zoom-secret"
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Server
    frontend_url: str
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # Redis (optional)
    redis_url: str = "redis://localhost:6379"

    
    class Config:
        env_file = ".env"
        extra = "allow"
        env_file_encoding = "utf-8"
        case_sensitive = False  # Allow case-insensitive environment variable names


settings = Settings()