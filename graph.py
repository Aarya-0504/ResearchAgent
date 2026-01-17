"""
Research Graph Module

Orchestrates the multi-agent research workflow using LangGraph.
Defines the flow: Planner → Researcher → Critic → Summarizer
"""

from langgraph.graph import StateGraph
from agents.planner import planner_agent
from agents.researcher import research_agent
from agents.critic import critic_agent
from agents.summarizer import summarizer_agent
from utils.logger import get_logger, log_communication

logger = get_logger(__name__)

logger.info("Initializing Research Graph...")

graph = StateGraph(dict)

# Add agents as nodes
graph.add_node("planner", planner_agent)
graph.add_node("researcher", research_agent)
graph.add_node("critic", critic_agent)
graph.add_node("summarizer", summarizer_agent)

# Define the workflow flow
graph.set_entry_point("planner")

# Planner → Researcher
logger.info("Connecting: Planner → Researcher")
graph.add_edge("planner", "researcher")

# Researcher → Critic
logger.info("Connecting: Researcher → Critic")
graph.add_edge("researcher", "critic")

# Critic → Summarizer
logger.info("Connecting: Critic → Summarizer")
graph.add_edge("critic", "summarizer")

# Compile the graph
app_graph = graph.compile()

logger.info("Research Graph compiled successfully!")
logger.info("Workflow: PLANNER → RESEARCHER → CRITIC → SUMMARIZER")
