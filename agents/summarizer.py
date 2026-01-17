"""
Summarizer Agent Module

Creates final synthesis and summary of research findings.
"""

from utils.llm import call_gemini
from utils.logger import get_logger, log_agent_start, log_agent_thinking, log_agent_output, log_agent_end


logger = get_logger(__name__)


def summarizer_agent(state: dict) -> dict:
    """
    Create a final summary combining research and critique.
    
    Thinking Process:
    1. Review all research findings
    2. Consider the critique feedback
    3. Identify most important insights
    4. Create clear, actionable summary
    5. Format for readability
    
    Args:
        state (dict): Current state with 'research' and 'critique' keys
    
    Returns:
        dict: Updated state with 'final_answer' key
    """
    query = state.get("query", "")
    research = state.get("research", "")
    critique = state.get("critique", "")
    
    log_agent_start(logger, "SUMMARIZER", {"query": query})
    
    thinking = f"""
Creating final summary:
1. Synthesizing research findings
2. Incorporating critique feedback
3. Identifying key takeaways
4. Organizing for clarity
5. Creating actionable insights
"""
    log_agent_thinking(logger, thinking)
    
    prompt = f"""
Create a final, well-structured research summary for this query: {query}

Use:
Research Findings:
{research}

Critical Review:
{critique}

Your Task:
1. Extract the most important findings
2. Incorporate critique feedback to improve quality
3. Create a clear executive summary
4. List key takeaways (3-5 bullets)
5. Suggest next steps or further research if needed
6. Include confidence assessment

Format as markdown with:
- # Executive Summary
- ## Key Findings
- ## Takeaways
- ## Confidence Assessment
- ## Next Steps (if applicable)

Make it insightful, clear, and actionable.
"""
    
    logger.info("Generating final summary with Gemini...")
    summary = call_gemini(prompt)
    
    log_agent_output(logger, summary[:500] + "..." if len(summary) > 500 else summary)
    
    result = {**state, "final_answer": summary}
    log_agent_end(logger, "SUMMARIZER", result)
    
    return result
