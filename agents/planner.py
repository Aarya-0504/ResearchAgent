"""
Planner Agent Module

Breaks down research queries into actionable steps.
"""

from utils.llm import call_gemini
from utils.logger import get_logger, log_agent_start, log_agent_thinking, log_agent_output, log_agent_end


logger = get_logger(__name__)


def planner_agent(state: dict) -> dict:
    """
    Plan the research approach by breaking down the query.
    
    Thinking Process:
    1. Analyze the query for key topics
    2. Identify research angles and subtopics
    3. Define investigation strategy
    4. Create actionable steps
    
    Args:
        state (dict): Current state with 'query' key
    
    Returns:
        dict: Updated state with 'plan' and 'query'
    """
    query = state.get("query", "")
    
    log_agent_start(logger, "PLANNER", {"query": query})
    
    thinking = f"Analyzing query: '{query}' to break it down into research steps"
    log_agent_thinking(logger, thinking)
    
    prompt = f"""
You are a research planning expert. Break down this research topic into clear, actionable steps.

Topic: {query}

Think step by step:
1. What are the main aspects of this topic?
2. What subtopics need investigation?
3. What questions need answering?
4. What order makes sense for research?

Return ONLY bullet points (no numbering). Be concise and specific.
"""
    
    logger.info(f"Generating research plan with Gemini...")
    steps = call_gemini(prompt)
    
    log_agent_output(logger, steps)
    
    result = {"plan": steps, "query": query}
    log_agent_end(logger, "PLANNER", result)
    
    return result
