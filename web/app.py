"""Streamlit application for memory buffer comparison."""
import streamlit as st
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.memory.base import Message
from src.memory.fifo_memory import FIFOMemory
from src.memory.priority_memory import PriorityMemory
from src.memory.hybrid_memory import HybridMemory
from src.llm.provider import get_llm
from src.config.settings import get_settings


# Page configuration
st.set_page_config(
    page_title="Memory Buffer Comparison",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "memories" not in st.session_state:
    settings = get_settings()
    st.session_state.memories = {
        "FIFO": FIFOMemory(
            window_size=settings.fifo_window_size,
            token_budget=settings.context_window_budget
        ),
        "Priority": PriorityMemory(
            top_k=settings.priority_top_k,
            token_budget=settings.context_window_budget,
            persist_directory=settings.chroma_persist_dir
        ),
        "Hybrid": HybridMemory(
            max_token_limit=settings.hybrid_token_limit,
            token_budget=settings.context_window_budget
        )
    }
    st.session_state.messages = []
    st.session_state.active_strategy = "FIFO"
    st.session_state.llm = None

# Initialize LLM
if st.session_state.llm is None:
    try:
        with st.spinner("Initializing LLM..."):
            st.session_state.llm = get_llm()
            # Test connection
            test_response = st.session_state.llm.invoke("test")
    except Exception as e:
        st.error(f"Failed to initialize LLM: {e}")
        st.info("""
        **Troubleshooting:**
        1. Make sure Ollama is running: `ollama serve`
        2. Pull the model: `ollama pull tinyllama`
        3. Check Ollama is accessible at the configured URL
        """)
        st.stop()


def display_metrics(memory, strategy_name):
    """Display metrics for a memory strategy."""
    metrics = memory.get_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Messages Processed", metrics.total_messages_processed)
        st.metric("Messages in Context", metrics.messages_in_context)
    
    with col2:
        st.metric("Messages Evicted", metrics.messages_evicted)
        st.metric("Summarizations", metrics.summarization_count)
    
    with col3:
        st.metric("Tokens Used", f"{metrics.total_tokens_used}/{metrics.context_token_budget}")
        st.metric("Utilization", f"{metrics.token_utilization_pct:.1f}%")
    
    with col4:
        st.metric("Retrieval Latency", f"{metrics.retrieval_latency_ms:.2f}ms")


def display_context(memory, strategy_name):
    """Display current context for a memory strategy."""
    context = memory.get_context()
    
    if not context:
        st.info("No messages in context yet.")
        return
    
    st.subheader(f"Context ({len(context)} messages)")
    
    for i, msg in enumerate(context):
        with st.expander(f"Message {i+1}: {msg.role.title()} ({msg.token_count} tokens)"):
            st.write(msg.content)
            st.caption(f"Timestamp: {msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            if hasattr(msg, 'priority_score') and msg.priority_score > 0:
                st.caption(f"Priority Score: {msg.priority_score:.3f}")


def process_message(user_input: str):
    """Process user message through all memory strategies."""
    user_msg = Message(
        role="user",
        content=user_input,
        timestamp=datetime.utcnow()
    )
    
    # Add to all memories
    for memory in st.session_state.memories.values():
        memory.add_message(user_msg)
    
    # Get active memory's context
    active_memory = st.session_state.memories[st.session_state.active_strategy]
    history = active_memory.get_formatted_history(query=user_input)
    
    # Build prompt
    prompt = f"""You are a helpful assistant. Use the conversation history to provide contextually relevant responses.

Conversation History:
{history}

Current query: {user_input}

Response:"""
    
    # Generate response
    try:
        with st.spinner("Thinking..."):
            response = st.session_state.llm.invoke(prompt)
            response_content = response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        response_content = f"Error generating response: {e}"
    
    # Create assistant message
    assistant_msg = Message(
        role="assistant",
        content=response_content,
        timestamp=datetime.utcnow()
    )
    
    # Add response to all memories
    for memory in st.session_state.memories.values():
        memory.add_message(assistant_msg)
    
    # Store in session
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "assistant", "content": response_content})
    
    return response_content


# Main UI
st.title("🧠 Memory Buffer Comparison Tool")
st.markdown("Compare FIFO, Priority, and Hybrid memory strategies for LLM-powered chatbots")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    
    # Strategy selection
    strategy = st.selectbox(
        "Active Strategy",
        ["FIFO", "Priority", "Hybrid"],
        index=["FIFO", "Priority", "Hybrid"].index(st.session_state.active_strategy)
    )
    st.session_state.active_strategy = strategy
    
    st.divider()
    
    # Clear button
    if st.button("Clear All Memories", type="secondary"):
        for memory in st.session_state.memories.values():
            memory.clear()
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # Model info
    settings = get_settings()
    st.info(f"**Model:** {settings.llm_model}\n\n**Provider:** {settings.llm_provider}")

# Main content area
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Comparison", "🔍 Memory State"])

with tab1:
    # Chat interface
    st.subheader(f"Chatting with {st.session_state.active_strategy} Strategy")
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Process and display response
        response = process_message(prompt)
        with st.chat_message("assistant"):
            st.write(response)
        
        st.rerun()

with tab2:
    st.subheader("Strategy Comparison")
    
    # Comparison metrics
    col1, col2, col3 = st.columns(3)
    
    for i, (name, memory) in enumerate(st.session_state.memories.items()):
        with [col1, col2, col3][i]:
            st.markdown(f"### {name}")
            metrics = memory.get_metrics()
            
            st.metric("Messages in Context", metrics.messages_in_context)
            st.metric("Tokens Used", metrics.total_tokens_used)
            st.metric("Messages Evicted", metrics.messages_evicted)
            st.metric("Utilization", f"{metrics.token_utilization_pct:.1f}%")
            st.metric("Latency", f"{metrics.retrieval_latency_ms:.2f}ms")
            
            if name == "Hybrid":
                st.metric("Summarizations", metrics.summarization_count)
    
    # Comparison chart
    st.divider()
    st.subheader("Token Usage Comparison")
    
    import pandas as pd
    
    data = {
        "Strategy": list(st.session_state.memories.keys()),
        "Tokens Used": [m.get_metrics().total_tokens_used for m in st.session_state.memories.values()],
        "Messages in Context": [m.get_metrics().messages_in_context for m in st.session_state.memories.values()],
        "Utilization %": [m.get_metrics().token_utilization_pct for m in st.session_state.memories.values()]
    }
    
    df = pd.DataFrame(data)
    st.bar_chart(df.set_index("Strategy")[["Tokens Used", "Messages in Context"]])

with tab3:
    st.subheader("Memory State Inspection")
    
    strategy_tabs = st.tabs(list(st.session_state.memories.keys()))
    
    for i, (name, memory) in enumerate(st.session_state.memories.items()):
        with strategy_tabs[i]:
            st.markdown(f"### {name} Memory State")
            
            # Metrics
            display_metrics(memory, name)
            
            st.divider()
            
            # Context
            display_context(memory, name)
            
            st.divider()
            
            # Formatted history preview
            st.subheader("Formatted History (for LLM)")
            formatted = memory.get_formatted_history()
            st.code(formatted if formatted else "No history yet", language="text")

# Footer
st.divider()
st.caption("Memory Buffer Comparison Tool - Demonstrating FIFO, Priority, and Hybrid memory strategies")
