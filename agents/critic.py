"""
Critic Agent Module

Reviews research findings for accuracy, gaps, and improvements.
"""

from utils.llm import call_gemini
from utils.logger import get_logger, log_agent_start, log_agent_thinking, log_agent_output, log_agent_end


logger = get_logger(__name__)


def critic_agent(state: dict) -> dict:
    """
    Critically evaluate research findings.
    
    Thinking Process:
    1. Analyze the research for factual accuracy
    2. Identify gaps in the research
    3. Check for contradictions or biases
    4. Suggest improvements
    5. Rate the overall quality
    
    Args:
        state (dict): Current state with 'research' key
    
    Returns:
        dict: Updated state with 'critique' key
    """
    query = state.get("query", "")
    research = state.get("research", "")
    
    log_agent_start(logger, "CRITIC", {"has_research": bool(research)})
    
    thinking = f"""
Analyzing research on '{query}':
1. Checking factual accuracy
2. Identifying information gaps
3. Assessing source credibility
4. Looking for biases or contradictions
5. Evaluating completeness
"""
    log_agent_thinking(logger, thinking)
    
    prompt = f"""
You are a critical research analyst. Review this research and provide constructive criticism.

Query: {query}

Research:
{research}

Analyze and provide:
1. Accuracy Assessment: Are the claims sound?
2. Gaps: What important information is missing?
3. Source Quality: Are sources credible?
4. Contradictions: Any conflicting information?
5. Improvements: What could be added or clarified?
6. Confidence Level: How confident are you in these findings?

Be fair but thorough. Point out both strengths and weaknesses.
"""
    
    logger.info("Generating critique with Gemini...")
    critique = call_gemini(prompt)
    
    log_agent_output(logger, critique[:500] + "..." if len(critique) > 500 else critique)
    
    result = {**state, "critique": critique}
    log_agent_end(logger, "CRITIC", result)
    
    return result
