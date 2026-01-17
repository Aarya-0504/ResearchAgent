"""
MongoDB Setup Guide for Research Agent Memory Persistence

This module provides instructions for setting up MongoDB with the Research Agent.
"""

# ============================================================================
# QUICK START: MongoDB Setup
# ============================================================================

"""
Option 1: Local MongoDB (Windows)
==================================

1. Download MongoDB Community Edition:
   https://www.mongodb.com/try/download/community

2. Run the installer and follow prompts

3. MongoDB will run as a service (mongod.exe)

4. Verify installation:
   mongosh
   > db.version()


Option 2: Docker (Recommended)
==============================

1. Install Docker Desktop:
   https://www.docker.com/products/docker-desktop

2. Run MongoDB in Docker:
   docker run -d --name research-agent-mongo \\
     -p 27017:27017 \\
     -e MONGO_INITDB_ROOT_USERNAME=admin \\
     -e MONGO_INITDB_ROOT_PASSWORD=password \\
     mongo:latest

3. Verify:
   docker ps


Option 3: MongoDB Atlas (Cloud - Free Tier)
===========================================

1. Go to: https://www.mongodb.com/cloud/atlas

2. Create free account

3. Create a cluster (M0 Free)

4. Get connection string:
   mongodb+srv://username:password@cluster.mongodb.net/research_agent

5. Use that as MONGO_URI in .env


Option 4: Docker Compose (Easiest)
==================================

1. Create docker-compose.yml in project root:

   version: '3.8'
   services:
     mongodb:
       image: mongo:latest
       container_name: research-agent-mongo
       environment:
         MONGO_INITDB_ROOT_USERNAME: admin
         MONGO_INITDB_ROOT_PASSWORD: password
       ports:
         - "27017:27017"
       volumes:
         - mongo_data:/data/db
   
   volumes:
     mongo_data:

2. Start with:
   docker-compose up -d

3. Stop with:
   docker-compose down
"""

# ============================================================================
# .env Configuration
# ============================================================================

"""
Add to your .env file:

# MongoDB Connection
MONGO_URI=mongodb://localhost:27017

# For Docker Compose:
MONGO_URI=mongodb://admin:password@localhost:27017

# For MongoDB Atlas:
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/research_agent

# Optional: Database and collection names
MONGO_DB=research_agent
MONGO_COLLECTION=queries
"""

# ============================================================================
# Installation
# ============================================================================

"""
1. Install pymongo:
   pip install pymongo

2. Or use requirements.txt:
   pip install -r requirements.txt
"""

# ============================================================================
# Usage Examples
# ============================================================================

def example_usage():
    """Example code for using memory persistence."""
    
    from persistence import get_memory_manager
    
    # Get memory manager instance
    memory = get_memory_manager()
    
    # Save research
    research_id = memory.save_research(
        query="What is quantum computing?",
        research="Detailed research findings...",
        critique="Critical evaluation...",
        final_answer="Final summary...",
        metadata={"source": "web_search"}
    )
    print(f"Saved with ID: {research_id}")
    
    # Retrieve research
    result = memory.get_research(research_id)
    print(result)
    
    # Get all research
    all_research = memory.get_all_research(limit=10)
    print(f"Found {len(all_research)} research documents")
    
    # Get recent research (last 7 days)
    recent = memory.get_recent_research(days=7)
    print(f"Recent research: {len(recent)} documents")
    
    # Search research
    results = memory.search_research("quantum computing", limit=5)
    print(f"Search results: {len(results)} documents")
    
    # Get statistics
    stats = memory.get_stats()
    print(f"Total research: {stats['total_research']}")
    print(f"This week: {stats['this_week']}")
    
    # Update research
    memory.update_research(research_id, {"tags": ["physics", "quantum"]})
    
    # Delete research
    memory.delete_research(research_id)


# ============================================================================
# REST API Usage with MongoDB
# ============================================================================

"""
POST /research
{
    "query": "What is AI?",
    "use_rag": true,
    "num_results": 5
}

Response:
{
    "success": true,
    "query": "What is AI?",
    "research": "...",
    "critique": "...",
    "final_answer": "...",
    "research_id": "507f1f77bcf86cd799439011"
}


GET /research-history?skip=0&limit=10
- Returns list of all past research

GET /research/{research_id}
- Returns specific research document

DELETE /research/{research_id}
- Deletes research document

GET /stats
- Returns database statistics
"""

# ============================================================================
# Database Schema
# ============================================================================

"""
MongoDB Documents Structure:

{
    "_id": ObjectId("..."),
    "query": "What is quantum computing?",
    "research": "Detailed research findings...",
    "critique": "Critical evaluation...",
    "final_answer": "Final summary with key takeaways...",
    "created_at": ISODate("2026-01-17T10:30:00Z"),
    "updated_at": ISODate("2026-01-17T10:30:00Z"),
    "metadata": {
        "use_rag": true,
        "num_results": 5,
        "tags": ["physics", "quantum"],
        "source": "web_search"
    }
}

Indexes:
- query (for text search)
- created_at (for sorting)
"""

# ============================================================================
# Troubleshooting
# ============================================================================

"""
MongoDB Connection Issues:

1. "Failed to connect to MongoDB"
   - Make sure MongoDB is running
   - Check MONGO_URI in .env
   - Verify port 27017 is accessible

2. Authentication failed
   - Check username and password
   - For Docker: use admin:password
   - For Atlas: use correct connection string

3. "Database 'research_agent' not found"
   - MongoDB creates DB on first write
   - This is normal, will be created automatically

4. Docker container won't start
   - Check port 27017 isn't already in use
   - Try: docker logs research-agent-mongo
   - Restart Docker Desktop
"""

# ============================================================================
# Running the System
# ============================================================================

"""
1. Start MongoDB:
   
   Local:
   mongod
   
   Docker:
   docker-compose up -d

2. Set .env:
   MONGO_URI=mongodb://localhost:27017
   GEMINI_API_KEY=your_key
   TAVILY_API_KEY=your_key

3. Install dependencies:
   pip install -r requirements.txt

4. Run backend:
   uvicorn main:app --reload --port 8000

5. Run frontend:
   streamlit run streamlit_app.py

6. Check MongoDB:
   mongosh
   > use research_agent
   > db.queries.find()
"""

print(__doc__)
