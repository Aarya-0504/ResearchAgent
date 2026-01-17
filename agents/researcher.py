"""
Research Agent Module

This module contains the research agent responsible for conducting research
by combining web search results with RAG context.
"""

from utils.llm import call_gemini
from tools.web_search import web_search
from rag.document_manager import DocumentManager
from utils.logger import get_logger, log_agent_start, log_agent_thinking, log_agent_output, log_agent_end


logger = get_logger(__name__)


def research_agent(state: dict) -> dict:
    """
    Conduct research using web search and RAG retrieval.
    
    Thinking Process:
    1. Conduct web searches for the query
    2. Retrieve relevant documents from the RAG vector store
    3. Analyze both sources for credibility and relevance
    4. Synthesize comprehensive research findings
    
    Args:
        state (dict): Current state containing:
            - query (str): The research query
            - plan (str): Research plan from planner
            - Other state information from prior agents
    
    Returns:
        dict: Updated state with 'research' key containing research findings
    """
    query = state.get("query", "")
    plan = state.get("plan", "")
    
    log_agent_start(logger, "RESEARCHER", {"query": query, "has_plan": bool(plan)})
    
    # Web search phase
    thinking = f"Conducting web search for: {query}"
    log_agent_thinking(logger, thinking)
    
    logger.info("Searching the web...")
    search_results = web_search(query)
    logger.info("Web search completed")
    
    # RAG retrieval phase
    thinking = "Retrieving context from knowledge base..."
    log_agent_thinking(logger, thinking)
    
    rag_context = _get_rag_context(query)
    logger.info("RAG retrieval completed")
    
    # Synthesis thinking
    search_lines = len(search_results.split('\n'))
    thinking = f"""
Analyzing sources:
- Web search: {search_lines} lines of content
- Knowledge base: Retrieved relevant documents
- Task: Synthesize comprehensive research findings
"""
    log_agent_thinking(logger, thinking)
    
    # Create comprehensive research prompt
    prompt = f"""
Research Topic: {query}

Research Plan:
{plan}

Web Results:
{search_results}

Knowledge Base Context (from ingested documents):
{rag_context}

Your Task:
1. Synthesize information from both web and knowledge base
2. Identify key findings and patterns
3. Note any contradictions or important caveats
4. Provide well-structured, detailed research notes
5. Cite sources where possible

Format: Use clear sections with markdown headers.
Be comprehensive but concise.
"""
    
    logger.info("Synthesizing research findings with Gemini...")
    research = call_gemini(prompt)
    
    log_agent_output(logger, research[:500] + "..." if len(research) > 500 else research)
    
    result = {**state, "research": research}
    log_agent_end(logger, "RESEARCHER", result)
    
    return result


def _get_rag_context(query: str, k: int = 3) -> str:
    """
    Retrieve context from RAG vector store.
    
    Args:
        query (str): Search query
        k (int): Number of documents to retrieve. Defaults to 3.
    
    Returns:
        str: Formatted context from retrieved documents or default message
    """
    try:
        doc_manager = DocumentManager()
        
        # Try to load existing vectorstore
        try:
            doc_manager.load_vectorstore()
        except FileNotFoundError:
            logger.info("No vectorstore found. RAG context unavailable.")
            return "No knowledge base available. Upload documents via the Streamlit interface to enable RAG context."
        
        logger.info(f"Searching vectorstore for {k} relevant documents...")
        docs = doc_manager.search(query, k=k)
        
        if docs:
            logger.info(f"Found {len(docs)} relevant documents from knowledge base")
            context = "\n\n".join([
                f"[Source: {d.metadata.get('source', 'unknown')}]\n{d.page_content}"
                for d in docs
            ])
            return context
        else:
            logger.info("No relevant documents found in knowledge base")
            return "No relevant documents found in knowledge base."
    except Exception as e:
        logger.warning(f"RAG retrieval warning: {str(e)}")
        return "Unable to retrieve knowledge base context. Proceeding with web search results only."
