"""
FastAPI Application for Multi-Agent Research System

REST API endpoints for the research agent with MongoDB persistence.
Use this for programmatic access to the research capabilities.

Endpoints:
    POST /research - Execute research query and save to MongoDB
    GET /research/{id} - Get specific research
    GET /research/history - Get all past research
    DELETE /research/{id} - Delete research
    GET /stats - Get database stats
    GET /health - Health check
    GET /docs - API documentation (Swagger)
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from graph import app_graph
from persistence import get_memory_manager
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)
logger.info("FastAPI Research Agent initialized")


app = FastAPI(
    title="Multi-Agent Research API",
    description="AI-powered research system with LangGraph, Gemini, and MongoDB persistence",
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
    research_id: Optional[str] = None
    error: Optional[str] = None


class ResearchHistory(BaseModel):
    """Model for research history item."""
    
    id: str = Field(..., alias="_id")
    query: str
    created_at: str
    final_answer: Optional[str] = None


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "API is running"}


@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """
    Execute a research query and save results to MongoDB.
    
    The system will:
    1. Break down the query into sub-tasks (planner)
    2. Conduct research using web search + RAG (researcher)
    3. Critically evaluate findings (critic)
    4. Synthesize final summary (summarizer)
    5. Save results to MongoDB
    
    Args:
        request: ResearchRequest with query and options
    
    Returns:
        ResearchResponse with research results and ID
    
    Raises:
        HTTPException: If research fails
    """
    try:
        logger.info("="*70)
        logger.info(f"NEW RESEARCH REQUEST: {request.query[:80]}")
        logger.info(f"Options: use_rag={request.use_rag}, num_results={request.num_results}")
        
        # Invoke the graph
        logger.info("Executing research workflow...")
        result = app_graph.invoke({"query": request.query})
        
        logger.info(f"✅ Research workflow completed")
        logger.debug(f"Result keys: {list(result.keys())}")
        
        # Save to MongoDB
        research_id = None
        try:
            logger.info("Saving research to MongoDB...")
            memory_manager = get_memory_manager()
            
            research_id = memory_manager.save_research(
                query=request.query,
                research=result.get("research", ""),
                critique=result.get("critique", ""),
                final_answer=result.get("final_answer", ""),
                metadata={"use_rag": request.use_rag, "num_results": request.num_results}
            )
            logger.info(f"✅ MongoDB save successful. Research ID: {research_id}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save to MongoDB: {str(e)}")
            logger.debug(f"MongoDB error details: {type(e).__name__}")
        
        logger.info("="*70)
        
        return ResearchResponse(
            success=True,
            query=request.query,
            research=result.get("research"),
            critique=result.get("critique"),
            final_answer=result.get("final_answer"),
            research_id=research_id
        )
    
    except Exception as e:
        logger.error(f"❌ RESEARCH FAILED: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.info("="*70)
        raise HTTPException(
            status_code=500,
            detail=f"Research failed: {str(e)}"
        )


@app.get("/research/{research_id}")
async def get_research(research_id: str):
    """Get a specific research by ID."""
    try:
        logger.info(f"Fetching research: {research_id}")
        memory_manager = get_memory_manager()
        research = memory_manager.get_research(research_id)
        
        if not research:
            logger.warning(f"Research not found: {research_id}")
            raise HTTPException(status_code=404, detail="Research not found")
        
        logger.info(f"✅ Research retrieved successfully")
        return research
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving research: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/research-history")
async def research_history(skip: int = 0, limit: int = 50):
    """Get research history (paginated)."""
    try:
        logger.info(f"Fetching research history: skip={skip}, limit={limit}")
        memory_manager = get_memory_manager()
        research_list = memory_manager.get_all_research(limit=limit, skip=skip)
        
        logger.info(f"✅ Retrieved {len(research_list)} research(s) from history")
        
        return {
            "total": len(research_list),
            "skip": skip,
            "limit": limit,
            "research": research_list
        }
    except Exception as e:
        logger.error(f"❌ Error fetching history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/research/{research_id}")
async def delete_research(research_id: str):
    """Delete a research record."""
    try:
        logger.info(f"Deleting research: {research_id}")
        memory_manager = get_memory_manager()
        success = memory_manager.delete_research(research_id)
        
        if not success:
            logger.warning(f"Research not found for deletion: {research_id}")
            raise HTTPException(status_code=404, detail="Research not found")
        
        logger.info(f"✅ Research deleted successfully")
        return {"message": "Research deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting research: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get database statistics."""
    try:
        logger.info("Fetching database statistics...")
        memory_manager = get_memory_manager()
        stats = memory_manager.get_stats()
        logger.info(f"✅ Stats retrieved: {stats}")
        return stats
    except Exception as e:
        logger.error(f"❌ Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Multi-Agent Research API",
        "version": "1.0.0",
        "docs": "/docs",
        "database": "MongoDB",
        "endpoints": {
            "health": "GET /health",
            "research": "POST /research",
            "get_research": "GET /research/{id}",
            "history": "GET /research-history",
            "delete": "DELETE /research/{id}",
            "stats": "GET /stats"
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
