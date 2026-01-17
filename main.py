"""
FastAPI Application for Multi-Agent Research System

REST API endpoints for the research agent.
Use this for programmatic access to the research capabilities.

Endpoints:
    POST /research - Execute research query
    GET /health - Health check
    GET /docs - API documentation (Swagger)
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from graph import app_graph
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Multi-Agent Research API",
    description="AI-powered research system with LangGraph and Gemini",
    version="1.0.0"
)


class ResearchRequest(BaseModel):
    """Request model for research queries."""
    
    query: str = Field(..., description="The research query", min_length=1, max_length=1000)
    use_rag: bool = Field(True, description="Whether to use RAG context")
    num_results: int = Field(5, ge=1, le=10, description="Number of web search results")


class ResearchResponse(BaseModel):
    """Response model for research results."""
    
    success: bool
    query: str
    research: Optional[str] = None
    critique: Optional[str] = None
    final_answer: Optional[str] = None
    error: Optional[str] = None


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "API is running"}


@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """
    Execute a research query.
    
    The system will:
    1. Break down the query into sub-tasks (planner)
    2. Conduct research using web search + RAG (researcher)
    3. Critically evaluate findings (critic)
    4. Synthesize final summary (summarizer)
    
    Args:
        request: ResearchRequest with query and options
    
    Returns:
        ResearchResponse with research results
    
    Raises:
        HTTPException: If research fails
    """
    try:
        logger.info(f"Received research request: {request.query}")
        
        # Invoke the graph
        result = app_graph.invoke({
            "query": request.query
        })
        
        logger.info(f"Research completed for: {request.query}")
        
        return ResearchResponse(
            success=True,
            query=request.query,
            research=result.get("research"),
            critique=result.get("critique"),
            final_answer=result.get("final_answer")
        )
    
    except Exception as e:
        logger.error(f"Research error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Research failed: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Multi-Agent Research API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "GET /health",
            "research": "POST /research"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
