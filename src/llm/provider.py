"""
LLM provider abstraction.

@help.category LLM Integration
@help.title LLM Provider
@help.description Abstraction layer for Large Language Model providers.
Currently supports Ollama for local LLM inference. Easy to extend for other providers.
"""
from langchain_ollama import ChatOllama
from ..config.settings import get_settings


def get_llm():
    """
    Get LLM instance based on configuration.
    
    @help.title Get LLM Function
    @help.description Factory function that returns configured LLM instance.
    Reads settings to determine provider and model. Currently supports Ollama only.
    @help.example
        llm = get_llm()
        response = llm.invoke("What is 2+2?")
        print(response.content)
    @help.requirements Ollama must be running and model must be pulled.
    """
    settings = get_settings()
    
    if settings.llm_provider.lower() == "ollama":
        return ChatOllama(
            model=settings.llm_model,
            base_url=settings.ollama_base_url
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
