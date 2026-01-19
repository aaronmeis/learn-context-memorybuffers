"""Pytest configuration and fixtures."""
import pytest
from datetime import datetime
from src.memory.base import Message


@pytest.fixture
def sample_message():
    """Fixture for creating a sample message."""
    return Message(role="user", content="Hello, world!")


@pytest.fixture
def sample_messages():
    """Fixture for creating multiple sample messages."""
    return [
        Message(role="user", content="First message"),
        Message(role="assistant", content="Second message"),
        Message(role="user", content="Third message"),
        Message(role="assistant", content="Fourth message"),
        Message(role="user", content="Fifth message"),
    ]


@pytest.fixture
def fifo_memory():
    """Fixture for creating a FIFO memory instance."""
    from src.memory.fifo_memory import FIFOMemory
    return FIFOMemory(window_size=5, token_budget=4000)


@pytest.fixture
def priority_memory():
    """Fixture for creating a Priority memory instance."""
    from src.memory.priority_memory import PriorityMemory
    return PriorityMemory(top_k=5, token_budget=4000)


@pytest.fixture
def hybrid_memory():
    """Fixture for creating a Hybrid memory instance."""
    from unittest.mock import Mock, patch
    from src.memory.hybrid_memory import HybridMemory
    
    with patch('src.memory.hybrid_memory.get_llm') as mock_get_llm:
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm
        return HybridMemory(max_token_limit=500, token_budget=4000)
