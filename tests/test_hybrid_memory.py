"""Unit tests for Hybrid memory implementation."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.memory.hybrid_memory import HybridMemory
from src.memory.base import Message


class TestHybridMemory:
    """Test Hybrid memory implementation."""
    
    def test_initialization(self):
        """Test Hybrid memory initialization."""
        with patch('src.memory.hybrid_memory.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_get_llm.return_value = mock_llm
            
            memory = HybridMemory(max_token_limit=500, token_budget=4000)
            assert memory.max_token_limit == 500
            assert memory.token_budget == 4000
            assert len(memory.recent_buffer) == 0
            assert memory.summary == ""
            assert memory.summary_token_count == 0
    
    def test_add_message(self):
        """Test adding messages to Hybrid buffer."""
        with patch('src.memory.hybrid_memory.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_get_llm.return_value = mock_llm
            
            memory = HybridMemory(max_token_limit=500)
            msg = Message(role="user", content="Hello")
            memory.add_message(msg)
            
            assert len(memory.recent_buffer) == 1
            assert len(memory.all_messages) == 1
            assert memory.recent_buffer[0] == msg
            assert memory.metrics.total_messages_processed == 1
            assert msg.token_count > 0
    
    def test_no_summarization_below_threshold(self):
        """Test that summarization doesn't trigger below threshold."""
        with patch('src.memory.hybrid_memory.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_get_llm.return_value = mock_llm
            
            memory = HybridMemory(max_token_limit=1000, summarize_threshold=0.8)
            
            # Add small messages that won't exceed threshold
            for i in range(3):
                msg = Message(role="user", content=f"Short message {i}")
                memory.add_message(msg)
            
            # Should not have triggered summarization
            assert memory.metrics.summarization_count == 0
            assert memory.summary == ""
    
    def test_summarization_trigger(self):
        """Test that summarization triggers when threshold is exceeded."""
        with patch('src.memory.hybrid_memory.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_response = Mock()
            mock_response.content = "Summary of conversation"
            mock_llm.invoke = Mock(return_value=mock_response)
            mock_get_llm.return_value = mock_llm
            
            memory = HybridMemory(max_token_limit=50, summarize_threshold=0.8)
            
            # Add messages that exceed threshold
            for i in range(10):
                msg = Message(
                    role="user" if i % 2 == 0 else "assistant",
                    content=f"This is a longer message that will use more tokens {i} " * 5
                )
                memory.add_message(msg)
            
            # Should have triggered summarization
            assert memory.metrics.summarization_count > 0
    
    def test_get_context(self):
        """Test getting context returns recent buffer."""
        with patch('src.memory.hybrid_memory.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_get_llm.return_value = mock_llm
            
            memory = HybridMemory(max_token_limit=500)
            
            msg1 = Message(role="user", content="First")
            msg2 = Message(role="assistant", content="Second")
            
            memory.add_message(msg1)
            memory.add_message(msg2)
            
            context = memory.get_context()
            assert len(context) == 2
            assert context[0] == msg1
            assert context[1] == msg2
    
    def test_get_formatted_history_without_summary(self):
        """Test formatted history without summary."""
        with patch('src.memory.hybrid_memory.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_get_llm.return_value = mock_llm
            
            memory = HybridMemory(max_token_limit=500)
            
            msg1 = Message(role="user", content="Hello")
            msg2 = Message(role="assistant", content="Hi there")
            
            memory.add_message(msg1)
            memory.add_message(msg2)
            
            history = memory.get_formatted_history()
            assert "Human: Hello" in history
            assert "Assistant: Hi there" in history
            assert "[Previous conversation summary:" not in history
    
    def test_get_formatted_history_with_summary(self):
        """Test formatted history with summary."""
        with patch('src.memory.hybrid_memory.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_response = Mock()
            mock_response.content = "Test summary"
            mock_llm.invoke = Mock(return_value=mock_response)
            mock_get_llm.return_value = mock_llm
            
            memory = HybridMemory(max_token_limit=50, summarize_threshold=0.8)
            memory.summary = "Test summary"
            
            msg = Message(role="user", content="Hello")
            memory.add_message(msg)
            
            history = memory.get_formatted_history()
            assert "[Previous conversation summary:" in history
            assert "Test summary" in history
    
    def test_clear(self):
        """Test clearing Hybrid buffer."""
        with patch('src.memory.hybrid_memory.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_get_llm.return_value = mock_llm
            
            memory = HybridMemory(max_token_limit=500)
            
            msg = Message(role="user", content="Test")
            memory.add_message(msg)
            memory.summary = "Some summary"
            
            memory.clear()
            assert len(memory.recent_buffer) == 0
            assert len(memory.all_messages) == 0
            assert memory.summary == ""
            assert memory.summary_token_count == 0
            assert memory.metrics.total_messages_processed == 0
    
    def test_metrics_update(self):
        """Test that metrics are updated correctly."""
        with patch('src.memory.hybrid_memory.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_get_llm.return_value = mock_llm
            
            memory = HybridMemory(max_token_limit=500, token_budget=1000)
            
            msg1 = Message(role="user", content="Hello world")
            msg2 = Message(role="assistant", content="Hi there")
            
            memory.add_message(msg1)
            memory.add_message(msg2)
            
            assert memory.metrics.messages_in_context == 2
            assert memory.metrics.total_tokens_used > 0
            assert memory.metrics.token_utilization_pct >= 0
    
    def test_summarization_failure_handling(self):
        """Test that summarization failures are handled gracefully."""
        with patch('src.memory.hybrid_memory.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_llm.invoke = Mock(side_effect=Exception("LLM error"))
            mock_get_llm.return_value = mock_llm
            
            memory = HybridMemory(max_token_limit=50, summarize_threshold=0.8)
            
            # Store initial buffer state
            initial_count = len(memory.recent_buffer)
            
            # Add messages that would trigger summarization
            for i in range(5):
                msg = Message(
                    role="user",
                    content=f"Long message that exceeds token limit {i} " * 10
                )
                memory.add_message(msg)
            
            # Buffer should still contain messages even if summarization fails
            assert len(memory.recent_buffer) > 0
    
    def test_summary_merging(self):
        """Test that summaries are merged when multiple summarizations occur."""
        with patch('src.memory.hybrid_memory.get_llm') as mock_get_llm:
            mock_llm = Mock()
            
            # First summary
            first_response = Mock()
            first_response.content = "First summary"
            
            # Merge response
            merge_response = Mock()
            merge_response.content = "Merged summary"
            
            mock_llm.invoke = Mock(side_effect=[first_response, merge_response])
            mock_get_llm.return_value = mock_llm
            
            memory = HybridMemory(max_token_limit=50, summarize_threshold=0.8)
            memory.summary = "Existing summary"
            
            # Trigger summarization
            for i in range(5):
                msg = Message(
                    role="user",
                    content=f"Long message {i} " * 10
                )
                memory.add_message(msg)
            
            # Should have attempted to merge summaries
            assert mock_llm.invoke.call_count >= 1
