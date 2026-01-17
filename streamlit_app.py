"""
Streamlit Application for Multi-Agent Research System

Modern, sleek UI with real-time logging and agent communication display.
"""

import streamlit as st
from pathlib import Path
import sys
import time
import logging

try:
    from graph import app_graph
    from rag.document_manager import DocumentManager
    from utils.logger import StreamlitLogHandler
    from persistence import get_memory_manager
except ImportError as e:
    st.error(f"Import Error: {str(e)}")
    sys.exit(1)

# Setup logging for Streamlit app
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] [STREAMLIT] %(levelname)s: %(message)s', datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

# Configure page
st.set_page_config(
    page_title="Research Agent",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for awesome UI
st.markdown("""
<style>
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .main-header {
        font-size: 3em;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2em;
    }
    
    .subheader-text {
        font-size: 1.1em;
        color: #666;
        margin-bottom: 2em;
    }
    
    .agent-log {
        background-color: #f0f2f6;
        border-left: 4px solid #667eea;
        padding: 12px;
        border-radius: 4px;
        margin: 8px 0;
        font-family: 'Courier New', monospace;
        font-size: 0.9em;
    }
    
    .agent-start {
        background-color: #e8f5e9;
        border-left-color: #4caf50;
    }
    
    .agent-thinking {
        background-color: #fff3e0;
        border-left-color: #ff9800;
        font-style: italic;
    }
    
    .agent-end {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    
    .result-section {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .upload-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    
    .button-group {
        display: flex;
        gap: 10px;
        margin: 20px 0;
    }
    
    .stat-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
</style>
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("<div class='main-header'>🔬 AI Research Agent</div>", unsafe_allow_html=True)
    st.markdown("<div class='subheader-text'>Intelligent research powered by multi-agent AI with RAG</div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='text-align: right; margin-top: 20px;'>
        <small>🚀 LangGraph • Gemini API • FAISS RAG</small>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Sidebar
with st.sidebar:
    st.markdown("### 📚 Knowledge Base")
    
    if 'doc_manager' not in st.session_state:
        st.session_state.doc_manager = DocumentManager()
    
    # Upload section
    st.markdown("<div class='upload-box'><strong>Upload Documents</strong><br><small>PDFs, TXT, Markdown files</small></div>", unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Choose files",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if uploaded_files and st.button("📤 Ingest", use_container_width=True):
            with st.spinner("Processing..."):
                try:
                    temp_dir = Path("temp_uploads")
                    temp_dir.mkdir(exist_ok=True)
                    
                    file_paths = []
                    for uploaded_file in uploaded_files:
                        file_path = temp_dir / uploaded_file.name
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        file_paths.append(str(file_path))
                    
                    st.session_state.doc_manager.add_documents(file_paths)
                    st.success(f"✅ {len(uploaded_files)} file(s) ingested")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col2:
        if st.button("📂 Load KB", use_container_width=True):
            try:
                st.session_state.doc_manager.load_vectorstore()
                st.success("✅ Loaded")
            except:
                st.info("No KB found")
    
    st.divider()
    st.markdown("### ⚙️ Settings")
    
    show_logs = st.checkbox("Show Agent Logs", value=True)
    auto_scroll = st.checkbox("Auto-scroll logs", value=True)

st.divider()

# Main content - Two columns
col_input, col_status = st.columns([2, 1])

with col_input:
    st.markdown("### 🔍 Research Query")
    query = st.text_area(
        "What would you like to research?",
        height=100,
        placeholder="e.g., What are the latest advances in quantum computing?",
        label_visibility="collapsed"
    )

with col_status:
    st.markdown("### 📊 Status")
    status_placeholder = st.empty()

# Run button
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    run_button = st.button("🚀 Run Research", use_container_width=True, key="run_research")

with col2:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.pop('logs', None)
        st.session_state.pop('results', None)
        st.rerun()

st.divider()

# Logs section (if enabled)
logs_container = None
logs_placeholder = None

if show_logs:
    st.markdown("### 📝 Agent Communication Log")
    logs_container = st.container(border=True)
    logs_placeholder = logs_container.empty()
    
    # Initialize session state for logs if needed
    if 'streamlit_logs' not in st.session_state:
        st.session_state.streamlit_logs = []

# Results section
if run_button and query.strip():
    status_placeholder.warning("⏳ Research in progress...")
    
    try:
        # Clear previous logs in session state
        if 'streamlit_logs' not in st.session_state:
            st.session_state.streamlit_logs = []
        st.session_state.streamlit_logs.clear()
        
        # Clear logs from handler
        StreamlitLogHandler.clear_logs()
        
        # Run research
        progress = st.progress(0)
        
        # Run the agent graph
        result = app_graph.invoke({"query": query.strip()})
        
        # Get all logs from the handler
        all_logs = StreamlitLogHandler.get_logs()
        
        # Store logs in session state for persistence
        if all_logs:
            st.session_state.streamlit_logs = all_logs
        
        # Display logs in real-time if enabled
        if show_logs and logs_placeholder and (all_logs or st.session_state.get('streamlit_logs')):
            log_text = "\n".join(st.session_state.get('streamlit_logs', []))
            if log_text.strip():
                logs_placeholder.code(log_text, language="log")
            else:
                logs_placeholder.info("📌 No logs captured. Ensure agents are calling logging functions.")
        elif show_logs and logs_placeholder:
            logs_placeholder.info("📌 Research will display logs here...")
        
        progress.progress(100)
        status_placeholder.success("✅ Research Complete!")
        
        # Store results
        st.session_state.results = result
        
        # Save to MongoDB
        try:
            logger.info("Saving research to MongoDB...")
            memory_manager = get_memory_manager()
            
            research_id = memory_manager.save_research(
                query=query.strip(),
                research=result.get("research", ""),
                critique=result.get("critique", ""),
                final_answer=result.get("final_answer", ""),
                metadata={}
            )
            
            logger.info(f"✅ Research saved to MongoDB with ID: {research_id}")
            st.success(f"📦 Saved to MongoDB: {research_id}")
            
            # Store ID in session
            st.session_state.research_id = research_id
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save to MongoDB: {str(e)}")
            st.warning(f"⚠️ Could not save to MongoDB: {str(e)}\n\nNote: Make sure MongoDB is running. Results are still displayed above.")
            
    except Exception as e:
        status_placeholder.error(f"❌ Error: {str(e)}")
        st.error(f"Failed to complete research: {str(e)}")

# Display results
if 'results' in st.session_state and st.session_state.results:
    st.divider()
    result = st.session_state.results
    
    # Show MongoDB ID if available
    if 'research_id' in st.session_state:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"💾 **Research saved to database**: `{st.session_state.research_id}`")
        with col2:
            if st.button("📋 Copy ID", key="copy_id"):
                st.write(st.session_state.research_id)
    
    # Results in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Summary", "🔬 Research", "✍️ Critique", "📊 Full"])
    
    with tab1:
        st.markdown("### Final Summary")
        if "final_answer" in result:
            st.markdown(result["final_answer"])
        else:
            st.info("No summary available")
    
    with tab2:
        st.markdown("### Research Findings")
        if "research" in result:
            st.markdown(result["research"])
        else:
            st.info("No research data")
    
    with tab3:
        st.markdown("### Critical Review")
        if "critique" in result:
            st.markdown(result["critique"])
        else:
            st.info("No critique available")
    
    with tab4:
        st.markdown("### Raw Output")
        st.json(result)
    
    # Download option
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📥 Download Results",
            data=str(result),
            file_name="research_results.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        st.download_button(
            "📊 Download as JSON",
            data=str(result),
            file_name="research_results.json",
            mime="application/json",
            use_container_width=True
        )

st.divider()
st.markdown("""
<div style='text-align: center; color: #999; margin-top: 2em;'>
    <small>Built with Gemini API • LangGraph • FAISS • Streamlit</small><br>
    <small>Multi-Agent Research System v1.0</small>
</div>
""", unsafe_allow_html=True)
