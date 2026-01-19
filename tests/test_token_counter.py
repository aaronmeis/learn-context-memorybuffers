"""Unit tests for token counter utility."""
import pytest
from unittest.mock import patch
from src.utils.token_counter import count_tokens, TIKTOKEN_AVAILABLE


class TestTokenCounter:
    """Test token counting utility."""
    
    def test_count_tokens_with_tiktoken(self):
        """Test token counting when tiktoken is available."""
        if TIKTOKEN_AVAILABLE:
            text = "Hello world"
            count = count_tokens(text)
            assert count > 0
            assert isinstance(count, int)
    
    @patch('src.utils.token_counter.TIKTOKEN_AVAILABLE', False)
    def test_count_tokens_fallback(self):
        """Test token counting fallback when tiktoken is unavailable."""
        text = "Hello world"
        count = count_tokens(text)
        # Fallback uses len(text) // 4
        expected = len(text) // 4
        assert count == expected
        assert isinstance(count, int)
    
    def test_count_tokens_empty_string(self):
        """Test token counting with empty string."""
        count = count_tokens("")
        assert count == 0
    
    def test_count_tokens_long_text(self):
        """Test token counting with longer text."""
        text = "This is a longer piece of text that should have more tokens. " * 10
        count = count_tokens(text)
        assert count > 0
    
    def test_count_tokens_special_characters(self):
        """Test token counting with special characters."""
        text = "Hello! @#$%^&*() World 123"
        count = count_tokens(text)
        assert count > 0
    
    def test_count_tokens_multiline(self):
        """Test token counting with multiline text."""
        text = """This is line one.
This is line two.
This is line three."""
        count = count_tokens(text)
        assert count > 0
    
    @patch('src.utils.token_counter.TIKTOKEN_AVAILABLE', True)
    def test_count_tokens_tiktoken_exception_handling(self):
        """Test that exceptions in tiktoken are handled gracefully."""
        with patch('tiktoken.encoding_for_model', side_effect=Exception("Encoding error")):
            text = "Test text"
            count = count_tokens(text)
            # Should fall back to approximation
            expected = len(text) // 4
            assert count == expected
    
    def test_count_tokens_consistency(self):
        """Test that token counting is consistent."""
        text = "Hello world"
        count1 = count_tokens(text)
        count2 = count_tokens(text)
        assert count1 == count2
    
    def test_count_tokens_different_models(self):
        """Test token counting with different model names."""
        text = "Hello world"
        count1 = count_tokens(text, model="gpt-3.5-turbo")
        count2 = count_tokens(text, model="gpt-4")
        # Both should return valid counts
        assert count1 > 0
        assert count2 > 0
