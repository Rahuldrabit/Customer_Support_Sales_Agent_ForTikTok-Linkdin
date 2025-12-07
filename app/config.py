"""Application configuration management."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "AI Customer Support Agent"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/customer_agent_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # LLM Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    llm_provider: str = "mock"  # Options: openrouter, openai, anthropic, chatgpt, claude, mock
    
    # OpenRouter Configuration
    openrouter_model: str = "anthropic/claude-3-haiku"  # Default model for OpenRouter
    openrouter_site_url: Optional[str] = None  # Optional: Your site URL for OpenRouter rankings
    openrouter_app_name: Optional[str] = None  # Optional: Your app name for OpenRouter rankings

    # Agent Configuration
    agent_max_tokens: int = 500
    agent_temperature: float = 0.7
    agent_timeout_seconds: int = 30
    agent_prompt_variant: str = "A"  # Options: A, B (for A/B testing)
    agent_default_language: str = "en"
    agent_auto_detect_language: bool = True

    # TikTok Integration
    tiktok_client_key: Optional[str] = None
    tiktok_client_secret: Optional[str] = None
    tiktok_webhook_secret: Optional[str] = None

    # LinkedIn Integration
    linkedin_client_id: Optional[str] = None
    linkedin_client_secret: Optional[str] = None

    # Rate Limiting
    tiktok_rate_limit: int = 60  # requests per minute
    linkedin_rate_limit: int = 100  # requests per minute

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    # Monitoring
    enable_metrics: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
