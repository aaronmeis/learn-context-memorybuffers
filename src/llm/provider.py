"""LLM provider abstraction."""
from langchain_ollama import ChatOllama
from ..config.settings import get_settings


def get_llm():
    """Get LLM instance based on configuration."""
    settings = get_settings()
    
    if settings.llm_provider.lower() == "ollama":
        return ChatOllama(
            model=settings.llm_model,
            base_url=settings.ollama_base_url
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
