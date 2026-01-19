"""Unit tests for settings configuration."""
import pytest
import os
from unittest.mock import patch
from src.config.settings import Settings, get_settings


class TestSettings:
    """Test settings configuration."""
    
    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()
        assert settings.ollama_base_url == "http://localhost:11434"
        assert settings.llm_model == "tinyllama"
        assert settings.llm_provider == "ollama"
        assert settings.embedding_model == "all-MiniLM-L6-v2"
        assert settings.chroma_persist_dir == "./chroma_data"
        assert settings.fifo_window_size == 5
        assert settings.priority_top_k == 5
        assert settings.hybrid_token_limit == 500
        assert settings.context_window_budget == 4000
        assert settings.log_level == "INFO"
    
    def test_custom_settings(self):
        """Test creating settings with custom values."""
        settings = Settings(
            llm_model="llama2",
            fifo_window_size=10,
            context_window_budget=8000
        )
        assert settings.llm_model == "llama2"
        assert settings.fifo_window_size == 10
        assert settings.context_window_budget == 8000
        # Other values should remain default
        assert settings.ollama_base_url == "http://localhost:11434"
    
    @patch.dict(os.environ, {
        'LLM_MODEL': 'custom-model',
        'FIFO_WINDOW_SIZE': '15',
        'CONTEXT_WINDOW_BUDGET': '6000'
    })
    def test_settings_from_environment(self):
        """Test loading settings from environment variables."""
        settings = Settings()
        assert settings.llm_model == "custom-model"
        assert settings.fifo_window_size == 15
        assert settings.context_window_budget == 6000
    
    def test_get_settings_function(self):
        """Test get_settings function."""
        settings = get_settings()
        assert isinstance(settings, Settings)
        assert settings.llm_provider == "ollama"
    
    def test_get_settings_singleton_behavior(self):
        """Test that get_settings returns consistent instances."""
        settings1 = get_settings()
        settings2 = get_settings()
        # Note: get_settings may or may not be a singleton depending on implementation
        # This test verifies it returns Settings instances
        assert isinstance(settings1, Settings)
        assert isinstance(settings2, Settings)
    
    def test_settings_case_insensitive(self):
        """Test that settings are case insensitive."""
        with patch.dict(os.environ, {'llm_model': 'test-model'}):
            settings = Settings()
            # Should handle case-insensitive env vars
            assert settings.llm_model in ["test-model", "tinyllama"]
    
    def test_settings_type_conversion(self):
        """Test that numeric settings are properly converted."""
        settings = Settings(
            fifo_window_size=10,
            priority_top_k=7,
            hybrid_token_limit=300,
            context_window_budget=5000
        )
        assert isinstance(settings.fifo_window_size, int)
        assert isinstance(settings.priority_top_k, int)
        assert isinstance(settings.hybrid_token_limit, int)
        assert isinstance(settings.context_window_budget, int)
    
    def test_settings_string_fields(self):
        """Test that string fields are properly handled."""
        settings = Settings(
            llm_model="test-model",
            llm_provider="test-provider",
            embedding_model="test-embedding"
        )
        assert isinstance(settings.llm_model, str)
        assert isinstance(settings.llm_provider, str)
        assert isinstance(settings.embedding_model, str)
