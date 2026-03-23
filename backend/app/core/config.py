"""Application configuration using Pydantic BaseSettings."""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    app_name: str = "Agentic SDR API"
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    # Database settings
    database_url: str = "postgresql+asyncpg://elogia_user:elogia_password@postgres:5432/elogia_db"
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173", "https://elogia.muradmadi.com", "https://api.muradmadi.com"]
    
    # Logging
    log_level: str = "INFO"
    
    # Alembic
    alembic_db_url: str = "postgresql+asyncpg://elogia_user:elogia_password@postgres:5432/elogia_db"
    
    # Clay Webhook Integration
    clay_webhook_url: str = "https://api.clay.com/v3/sources/webhook/pull-in-data-from-a-webhook-5ed7a29a-3a2c-4d01-ae22-f877fc4d5197"
    clay_webhook_auth_token: str = "b0684b655aeef49899f2"
    
    # n8n Webhook Integration
    n8n_shredder_webhook_url: str = "http://localhost:5678/webhook/content-shredder"
    
    # Public Base URL (used for callback URLs in both Clay and n8n webhooks)
    public_base_url: str = "https://api.muradmadi.com"
    
    # Storage directory for uploaded PDFs
    storage_dir: str = "storage/pdfs"
    
    # AI API Keys
    anthropic_api_key: str = ""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
settings = Settings()
