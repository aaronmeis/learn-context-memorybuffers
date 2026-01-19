"""
Streamlit application for memory buffer comparison.

@help.category Application
@help.title Web Application
@help.description Interactive Streamlit web application for comparing memory buffer strategies.
Features chat interface, real-time metrics, strategy comparison, automated testing, and memory state inspection.

The application provides:
- Individual tabs for each memory strategy (FIFO, Priority, Hybrid) with dedicated chat interfaces
- Automated testing functionality that runs test sequences across all strategies
- Comprehensive comparison dashboard with metrics, charts, and recommendations
- Visual indicators showing which messages are in context vs evicted
- Export functionality for test results (JSON and CSV)
- Strategy recommendations based on test results

@help.example
    Run the application:
    streamlit run web/app.py
    
    Then:
    1. Select a strategy tab (FIFO, Priority, or Hybrid)
    2. Chat with the LLM to test the memory strategy
    3. Run automated tests from the sidebar
    4. View comparison results in the Comparison tab
    5. Export test results for analysis

@help.use_case Best for:
- Understanding how different memory strategies work
- Comparing token usage and context retention
- Testing memory behavior with different conversation patterns
- Learning about LLM memory management trade-offs
"""
import streamlit as st
from datetime import datetime
import sys
import os
import re

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.memory.base import Message
from src.memory.fifo_memory import FIFOMemory
from src.memory.priority_memory import PriorityMemory
from src.memory.hybrid_memory import HybridMemory
from src.llm.provider import get_llm
from src.config.settings import get_settings
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


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
            persist_directory=settings.chroma_persist_dir,
            chroma_server_url=settings.chroma_server_url
        ),
        "Hybrid": HybridMemory(
            max_token_limit=settings.hybrid_token_limit,
            token_budget=settings.context_window_budget
        )
    }
    st.session_state.messages = []
    st.session_state.active_strategy = "FIFO"
    st.session_state.llm = None
    st.session_state.test_running = False
    st.session_state.test_results = None

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


def clean_llm_response(text: str) -> str:
    """
    Aggressively clean LLM response to remove conversation history format echoes.
    The tinyllama model sometimes echoes the conversation history format in its responses.
    This function removes all "Human:" and "Assistant:" labels and extracts only the actual response.
    
    @help.title Clean LLM Response Function
    @help.description Removes conversation history format artifacts from LLM responses.
    Handles cases where the model echoes "Human:" or "Assistant:" prefixes or embeds
    full conversation history in its output. Uses regex patterns and line-by-line processing
    to extract only the actual response content.
    """
    if not text:
        return text
    
    original_text = text
    text = text.strip()
    
    # Remove "Conversation History:" prefix if present
    text = re.sub(r'^Conversation History:\s*', '', text, flags=re.IGNORECASE)
    
    # Split into lines for processing
    lines = text.split('\n')
    cleaned_lines = []
    found_assistant_content = False
    
    # Strategy: Find the last "Assistant:" response and everything after it that's not formatted
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Skip lines that are conversation history format
        if re.match(r'^(Human|Assistant):\s+', line_stripped, re.IGNORECASE):
            # Extract content after "Assistant:" label (this is the actual response)
            if re.match(r'^Assistant:\s+', line_stripped, re.IGNORECASE):
                content = re.sub(r'^Assistant:\s+', '', line_stripped, flags=re.IGNORECASE)
                if content:
                    cleaned_lines.append(content)
                    found_assistant_content = True
            # Skip "Human:" lines entirely
            continue
        
        # If we've found assistant content, keep all subsequent non-formatted lines
        if found_assistant_content:
            cleaned_lines.append(line)
        # If we haven't found assistant content yet, keep non-formatted lines
        # (might be the actual response before any formatting)
        elif not re.match(r'^(Human|Assistant):', line_stripped, re.IGNORECASE):
            cleaned_lines.append(line)
    
    # Join and clean
    cleaned = '\n'.join(cleaned_lines).strip()
    
    # Remove any remaining leading "Human:" or "Assistant:" prefixes
    cleaned = re.sub(r'^(Human|Assistant):\s*', '', cleaned, flags=re.IGNORECASE)
    
    # If cleaning removed everything or result is too short, try simpler approach:
    # Just remove all lines with "Human:" or "Assistant:" prefixes
    if not cleaned or (len(cleaned) < 20 and len(original_text) > 50):
        lines = original_text.split('\n')
        cleaned_lines = []
        for line in lines:
            line_stripped = line.strip()
            # Keep lines that don't start with "Human:" or "Assistant:"
            if not re.match(r'^(Human|Assistant):\s+', line_stripped, re.IGNORECASE):
                cleaned_lines.append(line)
        cleaned = '\n'.join(cleaned_lines).strip()
        # Remove "Conversation History:" if still present
        cleaned = re.sub(r'^Conversation History:\s*', '', cleaned, flags=re.IGNORECASE)
    
    return cleaned if cleaned else original_text.strip()


def process_message(user_input: str, skip_display: bool = False):
    """
    Process user message through all memory strategies.
    
    @help.title Process Message Function
    @help.description Processes a user message by adding it to all memory strategies,
    generating an LLM response using the active strategy's context, and updating
    all memories with the response. Uses LangChain message format to prevent format echo.
    
    @help.example
        response = process_message("What was the budget?")
        # Message added to FIFO, Priority, and Hybrid memories
        # Response generated using active strategy's context
        # Response cleaned and returned
    
    @help.performance Response time depends on LLM inference speed and active strategy
    (Priority is slower due to semantic search, FIFO is fastest).
    """
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
    context_messages = active_memory.get_context(query=user_input)
    
    # Build messages using LangChain format (better for preventing format echo)
    messages = [SystemMessage(content="You are a helpful assistant. Provide clear, direct responses without echoing conversation history format.")]
    
    # Add conversation history as proper message objects
    for msg in context_messages:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))
    
    # Add current user query
    messages.append(HumanMessage(content=user_input))
    
    # Generate response
    try:
        response = st.session_state.llm.invoke(messages)
        response_content = response.content if hasattr(response, 'content') else str(response)
        
        # Aggressively clean response to remove any format echoes
        response_content = clean_llm_response(response_content)
        
        # If cleaning removed everything, fall back to original
        if not response_content or len(response_content.strip()) < 3:
            response_content = response.content if hasattr(response, 'content') else str(response)
            response_content = response_content.strip()
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
    
    # Store in session (only if not skipping display)
    if not skip_display:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": response_content})
    
    return response_content


def run_automated_tests():
    """
    Run automated tests for all memory strategies.
    
    @help.title Run Automated Tests Function
    @help.description Executes predefined test sequences for each memory strategy
    (FIFO, Priority, Hybrid) independently. Tests include memory retention and context
    relevance scenarios. Returns structured results with metrics and conversation flows.
    
    @help.example
        test_results = run_automated_tests()
        # Returns dict with keys: "FIFO", "Priority", "Hybrid"
        # Each contains "test_sequences" and "final_metrics"
    
    @help.use_case Use this to compare how different strategies handle the same
    conversation patterns and identify which strategy performs best for your use case.
    """
    # Test sequences
    test_sequences = {
        "Memory Retention Test": [
            "My budget is $50,000",
            "Deadline is March 2025",
            "Team has 5 developers",
            "Using Python and React",
            "Any timeline concerns?",
            "What was the budget?"
        ],
        "Context Relevance Test": [
            "I'm planning a vacation to Japan",
            "I love sushi",
            "Budget is $3000",
            "What restaurants do you recommend?"
        ]
    }
    
    results = {}
    original_strategy = st.session_state.active_strategy
    
    # Test each strategy independently
    for strategy_name in ["FIFO", "Priority", "Hybrid"]:
        # Clear ALL memories before testing this strategy (ensures clean state)
        for memory in st.session_state.memories.values():
            memory.clear()
        
        st.session_state.active_strategy = strategy_name
        
        strategy_results = {
            "test_sequences": {},
            "final_metrics": None
        }
        
        # Run each test sequence
        for test_name, messages in test_sequences.items():
            sequence_results = []
            
            # Process each message in the sequence
            for i, user_msg in enumerate(messages):
                # Process message (skip display for automated testing)
                # Note: process_message adds to ALL memories, but we're testing each strategy separately
                response = process_message(user_msg, skip_display=True)
                sequence_results.append({
                    "user": user_msg,
                    "assistant": response,
                    "message_index": i + 1
                })
            
            # Get final metrics after the sequence for THIS strategy
            memory = st.session_state.memories[strategy_name]
            if hasattr(memory, '_update_metrics'):
                memory._update_metrics()
            
            strategy_results["test_sequences"][test_name] = sequence_results
        
        # Get final metrics after all test sequences
        memory = st.session_state.memories[strategy_name]
        if hasattr(memory, '_update_metrics'):
            memory._update_metrics()
        strategy_results["final_metrics"] = memory.get_metrics()
        
        results[strategy_name] = strategy_results
    
    # Restore original strategy
    # DON'T clear memories - preserve test results for comparison
    st.session_state.active_strategy = original_strategy
    
    return results


# Main UI
st.title("🧠 Memory Buffer Comparison Tool")
st.markdown("Compare FIFO, Priority, and Hybrid memory strategies for LLM-powered chatbots")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Strategy selection
    strategy = st.selectbox(
        "Active Strategy",
        ["FIFO", "Priority", "Hybrid"],
        index=["FIFO", "Priority", "Hybrid"].index(st.session_state.active_strategy),
        help="Select which memory strategy to use for the chat conversation"
    )
    st.session_state.active_strategy = strategy
    
    # Clear button
    if st.button("🗑️ Clear All Memories", type="secondary", use_container_width=True):
        for memory in st.session_state.memories.values():
            memory.clear()
        st.session_state.messages = []
        st.session_state.test_results = None
        st.rerun()
    
    st.divider()
    
    # Automated test button
    st.markdown("**Automated Testing**")
    if st.button("🧪 Run Automated Tests", type="primary", use_container_width=True):
        # Clear chat messages for clean test
        st.session_state.messages = []
        st.session_state.test_running = True
        st.session_state.test_results = None
        
        with st.spinner("Running automated tests for all strategies... This may take a minute."):
            try:
                test_results = run_automated_tests()
                st.session_state.test_results = test_results
                st.session_state.test_running = False
                st.success("✅ Tests completed! Check the Comparison tab for results.")
                st.rerun()
            except Exception as e:
                st.error(f"Test failed: {e}")
                st.session_state.test_running = False
        st.caption("⚠️ Tests will clear current conversation")
    
    if st.session_state.test_running:
        st.info("⏳ Tests are running... Please wait.")
    
    st.divider()
    
    # Model info (compact)
    settings = get_settings()
    st.caption("**Model:** " + settings.llm_model + " | **Provider:** " + settings.llm_provider)
    st.caption("**GPU:** Enabled")
    
    st.divider()
    
    # Consolidated info section
    with st.expander("ℹ️ About This Tool"):
        st.markdown("""
        **Memory Strategies:**
        - **FIFO:** Keeps most recent N messages (simple, fast)
        - **Priority:** Uses semantic search to find relevant messages
        - **Hybrid:** Combines recent messages with LLM summaries
        
        **Metrics Tracked:**
        Messages processed, tokens used, evictions, latency
        
        **Quick Test:**
        1. "My budget is $50,000"
        2. "Team has 5 developers"  
        3. "What was the budget?" ← Tests memory retention
        
        Use strategy tabs to test each one, then check **Comparison** tab for results.
        """)

# Main content area - Restructured with tabs for each strategy
tab_fifo, tab_priority, tab_hybrid, tab_comparison = st.tabs(["🔄 FIFO", "🎯 Priority", "🔀 Hybrid", "📊 Comparison"])

def render_chat_interface(strategy_name: str):
    """Render chat interface for a specific strategy."""
    st.subheader(f"Chatting with {strategy_name} Strategy")
    
    # Update active strategy when viewing this tab
    if st.session_state.active_strategy != strategy_name:
        st.session_state.active_strategy = strategy_name
    
    # Legend for visual indicators
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("**Legend:**")
    with col2:
        st.markdown("Normal text = In context | <span style='color: #666; font-style: italic;'>*Italic gray*</span> = Evicted", unsafe_allow_html=True)
    
    st.divider()
    
    # Get active memory's context to determine which messages are in context
    active_memory = st.session_state.memories[strategy_name]
    context_messages = active_memory.get_context()
    # Create a set of (role, content) tuples for quick lookup
    context_set = {(msg.role, msg.content) for msg in context_messages}
    
    # Display chat history with visual indicators
    for msg in st.session_state.messages:
        is_in_context = (msg["role"], msg["content"]) in context_set
        
        with st.chat_message(msg["role"]):
            # Apply visual styling based on context status
            if is_in_context:
                # Message is in active context - display normally
                st.write(msg["content"])
            else:
                # Message has been evicted - display with italic and muted color
                st.markdown(f'<span style="color: #666; font-style: italic;">{msg["content"]}</span>', unsafe_allow_html=True)
                st.caption("⚠️ Evicted from context")
    
    # Chat input - use unique key to avoid duplicate element ID error
    if prompt := st.chat_input("Type your message here...", key=f"chat_input_{strategy_name.lower()}"):
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Process and display response
        response = process_message(prompt)
        with st.chat_message("assistant"):
            st.write(response)
        
        st.rerun()
    
    # Show metrics for this strategy
    st.divider()
    st.subheader(f"{strategy_name} Metrics")
    memory = st.session_state.memories[strategy_name]
    if hasattr(memory, '_update_metrics'):
        memory._update_metrics()
    metrics = memory.get_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Messages Processed", metrics.total_messages_processed)
        st.metric("Messages in Context", metrics.messages_in_context)
    with col2:
        st.metric("Messages Evicted", metrics.messages_evicted)
        st.metric("Tokens Used", metrics.total_tokens_used)
    with col3:
        st.metric("Utilization", f"{metrics.token_utilization_pct:.1f}%")
        st.metric("Latency", f"{metrics.retrieval_latency_ms:.2f}ms")
    with col4:
        if strategy_name == "Hybrid":
            st.metric("Summarizations", metrics.summarization_count)
    
    # Show memory state
    st.divider()
    st.subheader("Memory State")
    display_context(memory, strategy_name)

with tab_fifo:
    render_chat_interface("FIFO")

with tab_priority:
    render_chat_interface("Priority")

with tab_hybrid:
    render_chat_interface("Hybrid")

with tab_comparison:
    st.subheader("Strategy Comparison")
    
    # Show test results if available
    if st.session_state.test_results:
        st.success("✅ Automated test results available")
        
        # Quick summary cards at the top
        st.markdown("### Quick Summary")
        summary_cols = st.columns(3)
        
        total_messages = sum(
            st.session_state.test_results[s]["final_metrics"].total_messages_processed 
            for s in st.session_state.test_results.keys()
        ) // len(st.session_state.test_results) if st.session_state.test_results else 0
        
        total_tokens = sum(
            st.session_state.test_results[s]["final_metrics"].total_tokens_used 
            for s in st.session_state.test_results.keys()
        )
        
        avg_latency = sum(
            st.session_state.test_results[s]["final_metrics"].retrieval_latency_ms 
            for s in st.session_state.test_results.keys()
        ) / len(st.session_state.test_results) if st.session_state.test_results else 0
        
        with summary_cols[0]:
            st.metric("Total Messages Tested", total_messages)
        with summary_cols[1]:
            st.metric("Total Tokens Used", f"{total_tokens:,}")
        with summary_cols[2]:
            st.metric("Avg Latency", f"{avg_latency:.2f}ms")
        
        st.markdown("---")
        
        # Display test results for each strategy
        for strategy_name, strategy_data in st.session_state.test_results.items():
            metrics = strategy_data["final_metrics"]
            
            # Determine if this strategy is a "winner" in any category
            all_metrics = {name: st.session_state.test_results[name]["final_metrics"] 
                          for name in st.session_state.test_results.keys()}
            
            is_most_efficient = metrics.total_tokens_used == min(m.total_tokens_used for m in all_metrics.values())
            is_best_retention = metrics.messages_in_context == max(m.messages_in_context for m in all_metrics.values())
            is_fastest = metrics.retrieval_latency_ms == min(m.retrieval_latency_ms for m in all_metrics.values())
            
            # Build badge string
            badges = []
            if is_most_efficient:
                badges.append("🏆 Most Efficient")
            if is_best_retention:
                badges.append("📚 Best Retention")
            if is_fastest:
                badges.append("⚡ Fastest")
            
            badge_text = " | ".join(badges) if badges else ""
            expander_title = f"📊 {strategy_name} Test Results"
            if badge_text:
                expander_title += f" - {badge_text}"
            
            with st.expander(expander_title, expanded=True):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Messages Processed", metrics.total_messages_processed)
                with col2:
                    st.metric("Messages in Context", metrics.messages_in_context)
                with col3:
                    st.metric("Tokens Used", metrics.total_tokens_used)
                with col4:
                    st.metric("Utilization", f"{metrics.token_utilization_pct:.1f}%")
                
                # Show test sequence results
                for test_name, sequence_results in strategy_data["test_sequences"].items():
                    st.markdown(f"**{test_name}**")
                    with st.container():
                        for result in sequence_results:
                            st.markdown(f"**Q{result['message_index']}:** {result['user']}")
                            response_preview = result['assistant'][:200] + "..." if len(result['assistant']) > 200 else result['assistant']
                            st.markdown(f"*Response:* {response_preview}")
                    st.divider()
        
        st.markdown("---")
    
    # Refresh metrics for all strategies to ensure they're up to date
    # Use test results if available, otherwise use current memory state
    for name, memory in st.session_state.memories.items():
        if hasattr(memory, '_update_metrics'):
            memory._update_metrics()
    
    # Comparison metrics - use test results if available, otherwise current state
    st.subheader("Metrics Comparison")
    
    # Determine which metrics to use
    use_test_results = st.session_state.test_results is not None
    
    col1, col2, col3 = st.columns(3)
    
    for i, (name, memory) in enumerate(st.session_state.memories.items()):
        with [col1, col2, col3][i]:
            st.markdown(f"### {name}")
            
            # Use test results if available, otherwise current metrics
            if use_test_results and name in st.session_state.test_results:
                metrics = st.session_state.test_results[name]["final_metrics"]
            else:
                metrics = memory.get_metrics()
            
            st.metric("Messages Processed", metrics.total_messages_processed)
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
    
    # Build data from test results or current state
    strategies = []
    tokens_used = []
    messages_in_context = []
    utilization = []
    
    for name, memory in st.session_state.memories.items():
        strategies.append(name)
        if use_test_results and name in st.session_state.test_results:
            metrics = st.session_state.test_results[name]["final_metrics"]
        else:
            metrics = memory.get_metrics()
        tokens_used.append(metrics.total_tokens_used)
        messages_in_context.append(metrics.messages_in_context)
        utilization.append(metrics.token_utilization_pct)
    
    data = {
        "Strategy": strategies,
        "Tokens Used": tokens_used,
        "Messages in Context": messages_in_context,
        "Utilization %": utilization
    }
    
    df = pd.DataFrame(data)
    st.bar_chart(df.set_index("Strategy")[["Tokens Used", "Messages in Context"]])
    
    # What This Means section
    st.divider()
    st.subheader("📖 What This Means")
    
    with st.expander("Understanding the Metrics", expanded=True):
        st.markdown("""
        **Key Metrics Explained:**
        
        - **Messages Processed**: Total number of messages (user + assistant) that have been added to memory
        - **Messages in Context**: Number of messages currently retained and available for the LLM to use
        - **Tokens Used**: Total tokens consumed by messages in the current context window
        - **Messages Evicted**: Messages removed from memory due to window size limits or summarization
        - **Utilization**: Percentage of the token budget currently being used
        - **Latency**: Time taken to retrieve/process context (lower is better)
        """)
    
    with st.expander("Strategy Differences", expanded=True):
        st.markdown("""
        **FIFO (First-In-First-Out)**
        - Keeps only the most recent N messages
        - **High token usage**: Includes full message content
        - **Fast**: Simple sliding window, no complex processing
        - **May lose important context**: Older messages are evicted regardless of importance
        - **Best for**: Short conversations, predictable memory needs
        
        **Priority (Semantic Search)**
        - Uses vector similarity to find relevant messages
        - **Low token usage**: Only retrieves top-K most relevant messages
        - **Slower**: Requires embedding computation and similarity search
        - **Preserves important context**: Can remember older messages if they're relevant
        - **Best for**: Long conversations, when context relevance matters more than recency
        
        **Hybrid (Summary Buffer)**
        - Combines recent messages with LLM-generated summaries
        - **Moderate token usage**: Recent messages + compressed summaries
        - **Moderate speed**: Summarization adds overhead but reduces token count
        - **Balanced approach**: Preserves detail in recent messages, compresses older ones
        - **Best for**: Long conversations where both detail and efficiency matter
        """)
    
    with st.expander("Interpreting the Chart", expanded=True):
        st.markdown("""
        **Token Usage Comparison Chart:**
        
        - **Higher bars** = More tokens used = More context available but higher cost
        - **Lower bars** = Fewer tokens used = More efficient but potentially less context
        
        **What to Look For:**
        
        1. **FIFO** typically shows the highest token usage because it keeps full recent messages
        2. **Priority** shows lower token usage because it only retrieves relevant messages (top-K)
        3. **Hybrid** falls in between, balancing recent detail with summarized history
        
        **Trade-offs:**
        - More tokens = Better context retention but higher API costs
        - Fewer tokens = Lower costs but may miss important context
        - The "best" strategy depends on your use case: conversation length, importance of older context, and token budget constraints
        """)
    
    # Strategy Recommendations based on metrics
    st.divider()
    st.subheader("💡 Recommendations")
    
    if use_test_results:
        # Analyze test results and provide recommendations
        recommendations = []
        
        # Find most efficient (lowest tokens)
        efficiency_winner = min(st.session_state.memories.keys(), 
                               key=lambda x: st.session_state.test_results[x]["final_metrics"].total_tokens_used 
                               if x in st.session_state.test_results else float('inf'))
        
        # Find best context retention (most messages in context)
        retention_winner = max(st.session_state.memories.keys(),
                              key=lambda x: st.session_state.test_results[x]["final_metrics"].messages_in_context
                              if x in st.session_state.test_results else 0)
        
        # Find fastest (lowest latency)
        speed_winner = min(st.session_state.memories.keys(),
                          key=lambda x: st.session_state.test_results[x]["final_metrics"].retrieval_latency_ms
                          if x in st.session_state.test_results else float('inf'))
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Most Efficient:** {efficiency_winner}\n\nLowest token usage, best for cost-sensitive applications.")
        
        with col2:
            st.info(f"**Best Retention:** {retention_winner}\n\nMost messages in context, best for complex conversations.")
        
        with col3:
            st.info(f"**Fastest:** {speed_winner}\n\nLowest latency, best for real-time applications.")
        
        # Overall recommendation
        st.markdown("---")
        
        # Calculate a composite score (lower is better for efficiency)
        strategy_scores = {}
        for name in st.session_state.memories.keys():
            if name in st.session_state.test_results:
                metrics = st.session_state.test_results[name]["final_metrics"]
                # Score: balance between efficiency and retention
                # Lower tokens + higher retention = better score
                efficiency_score = metrics.total_tokens_used / max(metrics.messages_in_context, 1)
                strategy_scores[name] = {
                    "score": efficiency_score,
                    "tokens": metrics.total_tokens_used,
                    "retention": metrics.messages_in_context,
                    "latency": metrics.retrieval_latency_ms
                }
        
        if strategy_scores:
            # Best overall (lowest score = best efficiency/retention balance)
            best_overall = min(strategy_scores.keys(), key=lambda x: strategy_scores[x]["score"])
            
            st.success(f"""
            **🏆 Recommended Strategy: {best_overall}**
            
            Based on the test results, **{best_overall}** provides the best balance of:
            - Token efficiency: {strategy_scores[best_overall]['tokens']} tokens used
            - Context retention: {strategy_scores[best_overall]['retention']} messages in context
            - Response speed: {strategy_scores[best_overall]['latency']:.2f}ms latency
            """)
    else:
        st.info("Run automated tests to get personalized strategy recommendations based on your use case.")
    
    # Export functionality
    st.divider()
    st.subheader("📥 Export Results")
    
    if use_test_results:
        import json
        
        # Prepare export data
        export_data = {
            "test_timestamp": datetime.utcnow().isoformat(),
            "strategies": {}
        }
        
        for name, data in st.session_state.test_results.items():
            metrics = data["final_metrics"]
            export_data["strategies"][name] = {
                "metrics": {
                    "messages_processed": metrics.total_messages_processed,
                    "messages_in_context": metrics.messages_in_context,
                    "tokens_used": metrics.total_tokens_used,
                    "messages_evicted": metrics.messages_evicted,
                    "utilization_percent": metrics.token_utilization_pct,
                    "latency_ms": metrics.retrieval_latency_ms,
                    "summarizations": getattr(metrics, 'summarization_count', 0)
                },
                "test_sequences": data["test_sequences"]
            }
        
        # JSON export
        json_str = json.dumps(export_data, indent=2)
        st.download_button(
            label="📄 Download Results as JSON",
            data=json_str,
            file_name=f"memory_comparison_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
        
        # CSV export for metrics
        import pandas as pd
        csv_data = []
        for name, data in st.session_state.test_results.items():
            metrics = data["final_metrics"]
            csv_data.append({
                "Strategy": name,
                "Messages Processed": metrics.total_messages_processed,
                "Messages in Context": metrics.messages_in_context,
                "Tokens Used": metrics.total_tokens_used,
                "Messages Evicted": metrics.messages_evicted,
                "Utilization %": metrics.token_utilization_pct,
                "Latency (ms)": metrics.retrieval_latency_ms,
                "Summarizations": getattr(metrics, 'summarization_count', 0)
            })
        
        csv_df = pd.DataFrame(csv_data)
        csv_str = csv_df.to_csv(index=False)
        st.download_button(
            label="📊 Download Metrics as CSV",
            data=csv_str,
            file_name=f"memory_comparison_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Run automated tests to enable export functionality.")

# Footer
st.divider()
st.caption("Memory Buffer Comparison Tool - Demonstrating FIFO, Priority, and Hybrid memory strategies")
