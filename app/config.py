from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_provider: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_store_dir: str = "chroma_db"
    upload_dir: str = "uploads"
    chunk_size: int = 900
    chunk_overlap: int = 150
    min_relevance_score: float = 0.18

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def vector_store_path(self) -> Path:
        return Path(self.vector_store_dir) / "rag.sqlite3"

    @property
    def upload_path(self) -> Path:
        return Path(self.upload_dir)


@lru_cache
def get_settings() -> Settings:
    return Settings()
