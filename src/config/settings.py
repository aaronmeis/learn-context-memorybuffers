"""Application settings using Pydantic."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration."""
    
    # LLM Configuration
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "tinyllama"
    llm_provider: str = "ollama"
    
    # Embedding Configuration
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # ChromaDB Configuration
    chroma_persist_dir: str = "./chroma_data"
    
    # Memory Configuration
    fifo_window_size: int = 5
    priority_top_k: int = 5
    hybrid_token_limit: int = 500
    context_window_budget: int = 4000
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
