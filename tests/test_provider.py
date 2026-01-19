"""Unit tests for LLM provider."""
import pytest
from unittest.mock import patch, Mock
from src.llm.provider import get_llm


class TestLLMProvider:
    """Test LLM provider functionality."""
    
    @patch('src.llm.provider.get_settings')
    @patch('src.llm.provider.ChatOllama')
    def test_get_llm_ollama(self, mock_chat_ollama, mock_get_settings):
        """Test getting Ollama LLM instance."""
        # Mock settings
        mock_settings = Mock()
        mock_settings.llm_provider = "ollama"
        mock_settings.llm_model = "tinyllama"
        mock_settings.ollama_base_url = "http://localhost:11434"
        mock_get_settings.return_value = mock_settings
        
        # Mock ChatOllama
        mock_llm_instance = Mock()
        mock_chat_ollama.return_value = mock_llm_instance
        
        llm = get_llm()
        
        # Verify ChatOllama was called with correct parameters
        mock_chat_ollama.assert_called_once_with(
            model="tinyllama",
            base_url="http://localhost:11434"
        )
        assert llm == mock_llm_instance
    
    @patch('src.llm.provider.get_settings')
    def test_get_llm_unsupported_provider(self, mock_get_settings):
        """Test that unsupported providers raise ValueError."""
        mock_settings = Mock()
        mock_settings.llm_provider = "unsupported"
        mock_get_settings.return_value = mock_settings
        
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            get_llm()
    
    @patch('src.llm.provider.get_settings')
    @patch('src.llm.provider.ChatOllama')
    def test_get_llm_case_insensitive(self, mock_chat_ollama, mock_get_settings):
        """Test that provider name is case insensitive."""
        mock_settings = Mock()
        mock_settings.llm_provider = "OLLAMA"  # Uppercase
        mock_settings.llm_model = "tinyllama"
        mock_settings.ollama_base_url = "http://localhost:11434"
        mock_get_settings.return_value = mock_settings
        
        mock_llm_instance = Mock()
        mock_chat_ollama.return_value = mock_llm_instance
        
        llm = get_llm()
        
        # Should still work with uppercase
        mock_chat_ollama.assert_called_once()
        assert llm == mock_llm_instance
    
    @patch('src.llm.provider.get_settings')
    @patch('src.llm.provider.ChatOllama')
    def test_get_llm_custom_model(self, mock_chat_ollama, mock_get_settings):
        """Test getting LLM with custom model."""
        mock_settings = Mock()
        mock_settings.llm_provider = "ollama"
        mock_settings.llm_model = "llama2"
        mock_settings.ollama_base_url = "http://localhost:11434"
        mock_get_settings.return_value = mock_settings
        
        mock_llm_instance = Mock()
        mock_chat_ollama.return_value = mock_llm_instance
        
        llm = get_llm()
        
        mock_chat_ollama.assert_called_once_with(
            model="llama2",
            base_url="http://localhost:11434"
        )
        assert llm == mock_llm_instance
    
    @patch('src.llm.provider.get_settings')
    @patch('src.llm.provider.ChatOllama')
    def test_get_llm_custom_base_url(self, mock_chat_ollama, mock_get_settings):
        """Test getting LLM with custom base URL."""
        mock_settings = Mock()
        mock_settings.llm_provider = "ollama"
        mock_settings.llm_model = "tinyllama"
        mock_settings.ollama_base_url = "http://custom:8080"
        mock_get_settings.return_value = mock_settings
        
        mock_llm_instance = Mock()
        mock_chat_ollama.return_value = mock_llm_instance
        
        llm = get_llm()
        
        mock_chat_ollama.assert_called_once_with(
            model="tinyllama",
            base_url="http://custom:8080"
        )
        assert llm == mock_llm_instance
