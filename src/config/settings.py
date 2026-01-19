"""
Application settings using Pydantic.

@help.category Configuration
@help.title Application Settings
@help.description Centralized configuration management using Pydantic Settings. 
All application settings can be configured via environment variables or .env file.
@help.example
    from src.config.settings import get_settings
    settings = get_settings()
    print(settings.llm_model)  # Output: tinyllama
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application configuration.
    
    @help.title Settings Class
    @help.description Main configuration class that loads settings from environment variables
    or .env file. Uses Pydantic for validation and type safety.
    """
    
    # LLM Configuration
    # @help.title LLM Configuration
    # @help.description Settings for Large Language Model provider and model selection
    ollama_base_url: str = "http://localhost:11434"
    # @help.description Base URL for Ollama API endpoint. Default is localhost on standard port.
    llm_model: str = "tinyllama"
    # @help.description Name of the Ollama model to use. tinyllama is the smallest, fastest model.
    llm_provider: str = "ollama"
    # @help.description LLM provider name. Currently only 'ollama' is supported.
    
    # Embedding Configuration
    # @help.title Embedding Configuration
    # @help.description Settings for text embedding models used in semantic search
    embedding_model: str = "all-MiniLM-L6-v2"
    # @help.description Sentence Transformers model for generating embeddings. 
    # all-MiniLM-L6-v2 is a lightweight, fast model suitable for local use.
    
    # ChromaDB Configuration
    # @help.title ChromaDB Configuration
    # @help.description Settings for vector database used in Priority memory strategy
    chroma_persist_dir: str = "./chroma_data"
    # @help.description Local directory path for ChromaDB persistence. 
    # Used when not connecting to a ChromaDB server.
    chroma_server_url: Optional[str] = None  # e.g., "http://localhost:8000" or "http://chromadb:8000"
    # @help.description Optional ChromaDB server URL for remote vector storage. 
    # Set to None for local file-based storage, or provide URL like "http://localhost:8000"
    
    # Memory Configuration
    # @help.title Memory Strategy Configuration
    # @help.description Parameters controlling memory buffer behavior for each strategy
    fifo_window_size: int = 5
    # @help.description Number of message pairs (user+assistant) to keep in FIFO buffer.
    # Older messages are automatically evicted when limit is reached.
    priority_top_k: int = 5
    # @help.description Number of most relevant messages to retrieve in Priority strategy.
    # Uses semantic similarity search to find top K relevant messages.
    hybrid_token_limit: int = 500
    # @help.description Token threshold for Hybrid strategy. When recent messages exceed this,
    # older messages are summarized using the LLM.
    context_window_budget: int = 4000
    # @help.description Total token budget for context window. Used for utilization calculations
    # and metrics tracking across all memory strategies.
    
    # Logging
    # @help.title Logging Configuration
    log_level: str = "INFO"
    # @help.description Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """
    Get application settings.
    
    @help.title Get Settings Function
    @help.description Singleton function that returns the application settings instance.
    Settings are loaded from .env file or environment variables.
    @help.example
        settings = get_settings()
        if settings.llm_provider == "ollama":
            print(f"Using Ollama model: {settings.llm_model}")
    """
    return Settings()
