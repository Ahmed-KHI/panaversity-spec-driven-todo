"""
Application configuration.
[Task]: T-003 (Configuration)
[From]: spec.md §11, plan.md §4
[Updated]: T-014 (Phase III - Add OpenAI API key)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str
    
    # Security
    BETTER_AUTH_SECRET: str
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # Application
    APP_NAME: str = "Todo Management API"
    APP_VERSION: str = "5.0.0"
    
    # Phase III: OpenAI
    OPENAI_API_KEY: str
    
    # Phase V: Dapr Integration
    DAPR_HTTP_ENDPOINT: str = "http://localhost:3500"
    DAPR_GRPC_ENDPOINT: str = "http://localhost:50001"
    KAFKA_ENABLED: str = "false"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
