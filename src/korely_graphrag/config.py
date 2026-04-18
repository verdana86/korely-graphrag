"""Runtime configuration loaded from environment variables / .env."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(
        default="postgresql+psycopg2://korely:korely@localhost:5433/korely_graphrag",
        description="Postgres connection string. Must point to a database with the pgvector extension.",
    )

    llm_provider: str = Field(default="gemini", description="LLM provider: 'gemini' (Ollama coming soon).")
    gemini_api_key: str | None = Field(default=None, description="Required when llm_provider=gemini.")

    gemini_chat_model: str = Field(
        default="gemini-2.5-flash",
        description="Model used for entity extraction. Default targets the Gemini free tier.",
    )
    gemini_embedding_model: str = Field(
        default="gemini-embedding-001",
        description="Embedding model. Output dim must match the schema (default: 1536).",
    )
    embedding_dim: int = Field(default=1536)

    chunk_size_chars: int = Field(default=2800, description="~700 tokens.")
    chunk_overlap_chars: int = Field(default=420, description="~15% overlap.")
    min_chars_for_chunking: int = Field(default=4000)

    max_entities_per_doc: int = Field(default=10)
    min_entity_importance: float = Field(default=0.5)


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
