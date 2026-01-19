"""Unit tests for FIFO memory implementation."""
import pytest
from src.memory.fifo_memory import FIFOMemory
from src.memory.base import Message


class TestFIFOMemory:
    """Test FIFO memory implementation."""
    
    def test_initialization(self):
        """Test FIFO memory initialization."""
        memory = FIFOMemory(window_size=5, token_budget=4000)
        assert memory.window_size == 5
        assert memory.token_budget == 4000
        assert len(memory.buffer) == 0
    
    def test_add_message(self):
        """Test adding messages to FIFO buffer."""
        memory = FIFOMemory(window_size=3)
        msg = Message(role="user", content="Hello")
        memory.add_message(msg)
        
        assert len(memory.buffer) == 1
        assert memory.buffer[0] == msg
        assert memory.metrics.total_messages_processed == 1
        assert msg.token_count > 0
    
    def test_window_size_limit(self):
        """Test that FIFO respects window size."""
        memory = FIFOMemory(window_size=2)
        
        # Add 5 messages (window_size * 2 = 4 max)
        for i in range(5):
            msg = Message(role="user", content=f"Message {i}")
            memory.add_message(msg)
        
        # Should only keep last 4 messages (window_size * 2)
        assert len(memory.buffer) == 4
        assert memory.buffer[0].content == "Message 1"
        assert memory.buffer[-1].content == "Message 4"
        assert "Message 0" not in [m.content for m in memory.buffer]
    
    def test_get_context(self):
        """Test getting context from FIFO buffer."""
        memory = FIFOMemory(window_size=3)
        
        msg1 = Message(role="user", content="First")
        msg2 = Message(role="assistant", content="Second")
        msg3 = Message(role="user", content="Third")
        
        memory.add_message(msg1)
        memory.add_message(msg2)
        memory.add_message(msg3)
        
        context = memory.get_context()
        assert len(context) == 3
        assert context[0] == msg1
        assert context[1] == msg2
        assert context[2] == msg3
    
    def test_get_context_ignores_query(self):
        """Test that query parameter is ignored in FIFO."""
        memory = FIFOMemory(window_size=3)
        
        msg1 = Message(role="user", content="First")
        msg2 = Message(role="assistant", content="Second")
        
        memory.add_message(msg1)
        memory.add_message(msg2)
        
        context_with_query = memory.get_context(query="test query")
        context_without_query = memory.get_context()
        
        assert len(context_with_query) == len(context_without_query)
        assert context_with_query == context_without_query
    
    def test_get_formatted_history(self):
        """Test formatted history output."""
        memory = FIFOMemory(window_size=3)
        
        msg1 = Message(role="user", content="Hello")
        msg2 = Message(role="assistant", content="Hi there")
        
        memory.add_message(msg1)
        memory.add_message(msg2)
        
        history = memory.get_formatted_history()
        assert "Human: Hello" in history
        assert "Assistant: Hi there" in history
    
    def test_clear(self):
        """Test clearing FIFO buffer."""
        memory = FIFOMemory(window_size=3)
        
        for i in range(3):
            msg = Message(role="user", content=f"Message {i}")
            memory.add_message(msg)
        
        assert len(memory.buffer) == 3
        memory.clear()
        assert len(memory.buffer) == 0
        assert memory.metrics.total_messages_processed == 0
        assert memory.metrics.messages_in_context == 0
    
    def test_metrics_update(self):
        """Test that metrics are updated correctly."""
        memory = FIFOMemory(window_size=3, token_budget=1000)
        
        msg1 = Message(role="user", content="Hello world")
        msg2 = Message(role="assistant", content="Hi there")
        
        memory.add_message(msg1)
        memory.add_message(msg2)
        
        assert memory.metrics.messages_in_context == 2
        assert memory.metrics.total_tokens_used > 0
        assert memory.metrics.token_utilization_pct > 0
        assert memory.metrics.total_messages_processed == 2
    
    def test_eviction_tracking(self):
        """Test that evicted messages are tracked."""
        memory = FIFOMemory(window_size=2)
        
        # Add 5 messages, should evict 1
        for i in range(5):
            msg = Message(role="user", content=f"Message {i}")
            memory.add_message(msg)
        
        # Should have evicted at least 1 message
        assert memory.metrics.messages_evicted >= 1
    
    def test_token_counting(self):
        """Test that tokens are counted for messages."""
        memory = FIFOMemory(window_size=3)
        
        msg = Message(role="user", content="This is a test message")
        memory.add_message(msg)
        
        assert msg.token_count > 0
        assert memory.metrics.total_tokens_used > 0
    
    def test_retrieval_latency(self):
        """Test that retrieval latency is tracked."""
        memory = FIFOMemory(window_size=3)
        
        msg = Message(role="user", content="Test")
        memory.add_message(msg)
        
        assert memory.metrics.retrieval_latency_ms >= 0
