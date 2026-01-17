# 🗄️ MongoDB Memory Persistence Setup

## What Was Added

**Memory Persistence System** - All research queries and results are now automatically saved to MongoDB!

### Files Created:
- `persistence/memory_manager.py` - MongoDB operations (save, retrieve, search, delete)
- `persistence/__init__.py` - Module exports
- `MONGODB_SETUP.py` - Setup instructions and examples
- Updated `main.py` - Now saves all research to MongoDB
- Updated `requirements.txt` - Added `pymongo>=4.6.0`

---

## Quick Setup (Choose One)

### **Option 1: Docker Compose (Easiest)** ⭐ RECOMMENDED

```bash
# Create docker-compose.yml in project root with:
version: '3.8'
services:
  mongodb:
    image: mongo:latest
    container_name: research-agent-mongo
    ports:
      - "27017:27017"

# Start MongoDB
docker-compose up -d

# Add to .env
MONGO_URI=mongodb://localhost:27017
```

### **Option 2: Local MongoDB**

```bash
# Download from: https://www.mongodb.com/try/download/community
# Install and run mongod

# Add to .env
MONGO_URI=mongodb://localhost:27017
```

### **Option 3: MongoDB Atlas (Cloud - Free)**

```bash
# Go to: https://www.mongodb.com/cloud/atlas
# Create free account and cluster
# Copy connection string to .env
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/research_agent
```

---

## Install Dependencies

```bash
pip install pymongo
# OR
pip install -r requirements.txt
```

---

## Features

✅ **Auto-Save**: Every research query automatically saved to MongoDB  
✅ **History**: View all past research queries  
✅ **Search**: Find research by query text  
✅ **Retrieve**: Get specific research by ID  
✅ **Delete**: Remove old research records  
✅ **Statistics**: Database stats (total count, weekly count, etc.)  
✅ **Metadata**: Store custom tags, sources, etc.  

---

## API Endpoints (New)

### Save & Execute Research
```bash
POST /research
{
    "query": "What is quantum computing?",
    "use_rag": true
}

Response includes: research_id (MongoDB document ID)
```

### View All Research
```bash
GET /research-history?skip=0&limit=10

Returns list of all past research with pagination
```

### Get Specific Research
```bash
GET /research/{research_id}

Returns full research document with all fields
```

### Delete Research
```bash
DELETE /research/{research_id}

Removes research record from MongoDB
```

### Database Stats
```bash
GET /stats

Returns: total_research, this_week, database, collection
```

---

## Usage Examples

### Via Python
```python
from persistence import get_memory_manager

memory = get_memory_manager()

# Save research
research_id = memory.save_research(
    query="What is AI?",
    research="...",
    critique="...",
    final_answer="...",
    metadata={"tags": ["AI", "ML"]}
)

# Get research
result = memory.get_research(research_id)

# Get all research
all_research = memory.get_all_research(limit=50)

# Search
results = memory.search_research("quantum computing", limit=5)

# Get stats
stats = memory.get_stats()
```

### Via REST API
```bash
# Save research
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What is AI?"}'

# View history
curl http://localhost:8000/research-history?limit=10

# Get stats
curl http://localhost:8000/stats
```

---

## Database Schema

Each research document contains:
```json
{
    "_id": "ObjectId",
    "query": "Research question",
    "research": "Research findings",
    "critique": "Critical review",
    "final_answer": "Final summary",
    "created_at": "ISO timestamp",
    "updated_at": "ISO timestamp",
    "metadata": {
        "use_rag": true,
        "num_results": 5,
        "tags": ["physics"],
        "source": "web_search"
    }
}
```

---

## Running Everything

**Terminal 1 - MongoDB**
```bash
docker-compose up -d
# or: mongod
```

**Terminal 2 - Backend API**
```bash
uvicorn main:app --reload --port 8000
```

**Terminal 3 - Frontend UI**
```bash
streamlit run streamlit_app.py
```

---

## Check Saved Data

### Via mongosh CLI
```bash
mongosh
> use research_agent
> db.queries.find().pretty()
> db.queries.countDocuments()
```

### Via Python
```python
from persistence import get_memory_manager
memory = get_memory_manager()
stats = memory.get_stats()
print(f"Total research: {stats['total_research']}")
```

### Via API
```bash
curl http://localhost:8000/stats
```

---

## Troubleshooting

**"Failed to connect to MongoDB"**
- Make sure MongoDB is running (mongod or docker-compose up)
- Check MONGO_URI in .env
- Verify port 27017 is open

**"Authentication failed"**
- For Docker: check password in connection string
- For Atlas: verify correct connection string format
- For local: no auth needed by default

**"Database not found"**
- MongoDB creates DB on first write - this is normal
- Will be created automatically when first research is saved

---

## Next Steps

- Streamlit UI will show research history in sidebar
- Download research results feature
- Compare old vs new research
- Export history to CSV/PDF
- Advanced search and filtering
- Research tagging system

---

**All set!** Your research system now has persistent memory. 🎉
