"""Unit tests for base memory class."""
import pytest
from datetime import datetime
from src.memory.base import BaseMemory, Message, MemoryMetrics


class ConcreteMemory(BaseMemory):
    """Concrete implementation for testing abstract base class."""
    
    def __init__(self, token_budget: int = 4000):
        super().__init__(token_budget)
        self.messages = []
    
    def add_message(self, message: Message) -> None:
        """Add message to storage."""
        self.messages.append(message)
    
    def get_context(self, query: str = None) -> list[Message]:
        """Return all messages."""
        return self.messages
    
    def get_formatted_history(self, query: str = None) -> str:
        """Format messages."""
        return "\n".join([f"{m.role}: {m.content}" for m in self.messages])
    
    def clear(self) -> None:
        """Clear all messages."""
        self.messages.clear()
        self.metrics = MemoryMetrics(context_token_budget=self.token_budget)


class TestMessage:
    """Test Message model."""
    
    def test_message_creation(self):
        """Test creating a message."""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert isinstance(msg.timestamp, datetime)
        assert msg.token_count == 0
        assert msg.priority_score == 0.0
        assert msg.metadata == {}
    
    def test_message_with_metadata(self):
        """Test message with custom metadata."""
        msg = Message(
            role="assistant",
            content="Hi there",
            metadata={"source": "test"}
        )
        assert msg.metadata == {"source": "test"}


class TestMemoryMetrics:
    """Test MemoryMetrics model."""
    
    def test_metrics_defaults(self):
        """Test default metric values."""
        metrics = MemoryMetrics()
        assert metrics.total_messages_processed == 0
        assert metrics.messages_in_context == 0
        assert metrics.messages_evicted == 0
        assert metrics.total_tokens_used == 0
        assert metrics.context_token_budget == 4000
        assert metrics.token_utilization_pct == 0.0
        assert metrics.retrieval_latency_ms == 0.0
        assert metrics.summarization_count == 0
    
    def test_metrics_custom_budget(self):
        """Test metrics with custom token budget."""
        metrics = MemoryMetrics(context_token_budget=8000)
        assert metrics.context_token_budget == 8000


class TestBaseMemory:
    """Test BaseMemory abstract class."""
    
    def test_initialization(self):
        """Test base memory initialization."""
        memory = ConcreteMemory(token_budget=5000)
        assert memory.token_budget == 5000
        assert isinstance(memory.metrics, MemoryMetrics)
        assert memory.metrics.context_token_budget == 5000
    
    def test_default_token_budget(self):
        """Test default token budget."""
        memory = ConcreteMemory()
        assert memory.token_budget == 4000
    
    def test_add_message(self):
        """Test adding messages."""
        memory = ConcreteMemory()
        msg = Message(role="user", content="Test")
        memory.add_message(msg)
        assert len(memory.messages) == 1
        assert memory.messages[0] == msg
    
    def test_get_context(self):
        """Test getting context."""
        memory = ConcreteMemory()
        msg1 = Message(role="user", content="Hello")
        msg2 = Message(role="assistant", content="Hi")
        memory.add_message(msg1)
        memory.add_message(msg2)
        
        context = memory.get_context()
        assert len(context) == 2
        assert context[0] == msg1
        assert context[1] == msg2
    
    def test_get_formatted_history(self):
        """Test formatted history."""
        memory = ConcreteMemory()
        msg1 = Message(role="user", content="Hello")
        msg2 = Message(role="assistant", content="Hi")
        memory.add_message(msg1)
        memory.add_message(msg2)
        
        history = memory.get_formatted_history()
        assert "user: Hello" in history
        assert "assistant: Hi" in history
    
    def test_clear(self):
        """Test clearing memory."""
        memory = ConcreteMemory()
        msg = Message(role="user", content="Test")
        memory.add_message(msg)
        assert len(memory.messages) == 1
        
        memory.clear()
        assert len(memory.messages) == 0
        assert memory.metrics.total_messages_processed == 0
    
    def test_get_metrics(self):
        """Test getting metrics."""
        memory = ConcreteMemory()
        metrics = memory.get_metrics()
        assert isinstance(metrics, MemoryMetrics)
        assert metrics.context_token_budget == 4000
