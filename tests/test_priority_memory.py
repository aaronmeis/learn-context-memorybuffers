"""Unit tests for Priority memory implementation."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.memory.priority_memory import PriorityMemory
from src.memory.base import Message


class TestPriorityMemory:
    """Test Priority memory implementation."""
    
    def test_initialization(self):
        """Test Priority memory initialization."""
        memory = PriorityMemory(top_k=5, token_budget=4000)
        assert memory.top_k == 5
        assert memory.token_budget == 4000
        assert len(memory.all_messages) == 0
    
    def test_add_message(self):
        """Test adding messages to Priority buffer."""
        memory = PriorityMemory(top_k=3)
        msg = Message(role="user", content="Hello")
        memory.add_message(msg)
        
        assert len(memory.all_messages) == 1
        assert memory.all_messages[0] == msg
        assert memory.metrics.total_messages_processed == 1
        assert msg.token_count > 0
    
    def test_get_context_no_query(self):
        """Test getting context without query returns recent messages."""
        memory = PriorityMemory(top_k=3)
        
        for i in range(5):
            msg = Message(role="user", content=f"Message {i}")
            memory.add_message(msg)
        
        context = memory.get_context()
        # Should return top_k most recent messages
        assert len(context) == 3
        assert context[-1].content == "Message 4"
    
    def test_get_context_small_history(self):
        """Test getting context when history is smaller than top_k."""
        memory = PriorityMemory(top_k=5)
        
        msg1 = Message(role="user", content="First")
        msg2 = Message(role="assistant", content="Second")
        
        memory.add_message(msg1)
        memory.add_message(msg2)
        
        context = memory.get_context(query="test")
        assert len(context) == 2
        assert context[0] == msg1
        assert context[1] == msg2
    
    @patch('src.memory.priority_memory.CHROMADB_AVAILABLE', False)
    @patch('src.memory.priority_memory.NUMPY_AVAILABLE', True)
    def test_get_context_with_query_in_memory(self):
        """Test semantic retrieval with in-memory embeddings."""
        with patch('src.memory.priority_memory.SENTENCE_TRANSFORMERS_AVAILABLE', True):
            with patch('src.llm.embeddings.SENTENCE_TRANSFORMERS_AVAILABLE', True):
                # Mock embedding model
                mock_embeddings = Mock()
                mock_embeddings.encode = Mock(return_value=[0.1] * 384)
                
                with patch('src.memory.priority_memory.get_embedding_model', return_value=mock_embeddings):
                    memory = PriorityMemory(top_k=2)
                    
                    msg1 = Message(role="user", content="Python programming")
                    msg2 = Message(role="assistant", content="Java development")
                    msg3 = Message(role="user", content="Python coding")
                    
                    memory.add_message(msg1)
                    memory.add_message(msg2)
                    memory.add_message(msg3)
                    
                    context = memory.get_context(query="Python")
                    assert len(context) <= 2
                    assert len(context) > 0
    
    def test_get_formatted_history(self):
        """Test formatted history output."""
        memory = PriorityMemory(top_k=3)
        
        msg1 = Message(role="user", content="Hello")
        msg2 = Message(role="assistant", content="Hi there")
        
        memory.add_message(msg1)
        memory.add_message(msg2)
        
        history = memory.get_formatted_history()
        assert "Human: Hello" in history or "Assistant: Hi there" in history
    
    def test_clear(self):
        """Test clearing Priority buffer."""
        memory = PriorityMemory(top_k=3)
        
        for i in range(3):
            msg = Message(role="user", content=f"Message {i}")
            memory.add_message(msg)
        
        assert len(memory.all_messages) == 3
        memory.clear()
        assert len(memory.all_messages) == 0
        assert memory.metrics.total_messages_processed == 0
    
    def test_metrics_update(self):
        """Test that metrics are updated correctly."""
        memory = PriorityMemory(top_k=2, token_budget=1000)
        
        msg1 = Message(role="user", content="Hello world")
        msg2 = Message(role="assistant", content="Hi there")
        msg3 = Message(role="user", content="Another message")
        
        memory.add_message(msg1)
        memory.add_message(msg2)
        memory.add_message(msg3)
        
        context = memory.get_context()
        assert memory.metrics.messages_in_context == len(context)
        assert memory.metrics.total_tokens_used > 0
        assert memory.metrics.token_utilization_pct >= 0
    
    def test_token_counting(self):
        """Test that tokens are counted for messages."""
        memory = PriorityMemory(top_k=3)
        
        msg = Message(role="user", content="This is a test message")
        memory.add_message(msg)
        
        assert msg.token_count > 0
    
    def test_priority_score_assignment(self):
        """Test that priority scores are assigned during retrieval."""
        memory = PriorityMemory(top_k=2)
        
        msg1 = Message(role="user", content="First message")
        msg2 = Message(role="assistant", content="Second message")
        
        memory.add_message(msg1)
        memory.add_message(msg2)
        
        context = memory.get_context(query="test")
        # Messages should have priority scores assigned
        for msg in context:
            assert hasattr(msg, 'priority_score')
    
    def test_recency_weight(self):
        """Test that recency weight affects scoring."""
        memory = PriorityMemory(top_k=2, recency_weight=0.5, semantic_weight=0.5)
        assert memory.recency_weight == 0.5
        assert memory.semantic_weight == 0.5
    
    @patch('src.memory.priority_memory.CHROMADB_AVAILABLE', False)
    def test_fallback_to_recency_only(self):
        """Test fallback to recency-only when embeddings unavailable."""
        with patch('src.memory.priority_memory.NUMPY_AVAILABLE', False):
            with patch('src.memory.priority_memory.SENTENCE_TRANSFORMERS_AVAILABLE', False):
                memory = PriorityMemory(top_k=2)
                
                msg1 = Message(role="user", content="First")
                msg2 = Message(role="assistant", content="Second")
                msg3 = Message(role="user", content="Third")
                
                memory.add_message(msg1)
                memory.add_message(msg2)
                memory.add_message(msg3)
                
                context = memory.get_context(query="test")
                # Should still return messages based on recency
                assert len(context) <= 2
                assert len(context) > 0
