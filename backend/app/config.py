from __future__ import annotations

from enum import Enum
from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    OLLAMA = "ollama"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_list_separator=",",
    )

    # app
    app_name: str = "GermanGPT Tutor"
    app_version: str = "1.0.0"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    secret_key: str = "change_me_in_production"

    # auth
    jwt_secret: str = "jwt_change_me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10080

    # database
    database_url: str = Field(
        default="postgresql+asyncpg://germangpt:secret@localhost:5432/germangpt"
    )

    # redis
    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_password: str = ""

    # qdrant vector store
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "germangpt_knowledge"
    qdrant_vector_size: int = 1536

    # llm providers
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    default_llm_provider: LLMProvider = LLMProvider.ANTHROPIC
    default_chat_model: str = "claude-sonnet-4-6"
    default_embedding_model: str = "text-embedding-3-small"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2048

    # ollama (local models)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # voice
    openai_whisper_model: str = "whisper-1"
    tts_provider: Literal["openai", "elevenlabs", "azure"] = "openai"
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "pNInz6obpgDQGcFmaJgB"
    max_audio_size_mb: int = 25

    # rate limiting
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 20

    # cors
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    # observability
    langsmith_api_key: str = ""
    langsmith_project: str = "germangpt-tutor"
    langchain_tracing_v2: bool = False
    sentry_dsn: str = ""

    # feature flags
    enable_voice: bool = True
    enable_games: bool = True
    enable_multiplayer: bool = False
    enable_analytics: bool = True
    enable_rag: bool = True

    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
