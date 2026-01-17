# 🔬 AI Research Agent

A multi-agent research system powered by Gemini API, LangGraph, and FAISS RAG.

## 🚀 Features

### Multi-Agent Architecture
- **Planner Agent**: Breaks down queries into actionable steps
- **Researcher Agent**: Conducts web search + RAG retrieval
- **Critic Agent**: Evaluates findings for accuracy and gaps
- **Summarizer Agent**: Creates final synthesis and summary

### RAG (Retrieval-Augmented Generation)
- Upload PDFs, TXT, Markdown files
- Automatic document chunking and embedding
- FAISS vector store for fast semantic search
- Hybrid search combining web results + your documents

### Modern UI
- Beautiful Streamlit interface
- Real-time status updates
- Tabbed results view
- Download options (TXT, JSON)
- Settings panel with logging toggle

### Comprehensive Logging
- **Agent Communication**: Track flow between agents
- **Agent Thinking**: See reasoning process
- **Detailed Outputs**: Monitor each step
- **Color-coded Logs**: Easy-to-read terminal output

### REST API
- FastAPI backend for programmatic access
- Swagger documentation
- Full error handling
- Production-ready

## 📋 Tech Stack

- **LLM**: Google Gemini 2.0 Flash
- **Orchestration**: LangGraph
- **Vector DB**: FAISS + Sentence Transformers
- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Document Processing**: PyPDF, LangChain

## 🛠️ Setup

### 1. Create `.env` file
```bash
GEMINI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here  # or SERPAPI_API_KEY or GOOGLE_API_KEY
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application

**Terminal 1 - Backend API:**
```bash
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend UI:**
```bash
streamlit run streamlit_app.py
```

The UI opens at `http://localhost:8501`

## 📚 Usage

### Via Streamlit UI
1. Upload PDFs/TXT files (optional)
2. Enter your research query
3. Click "Run Research"
4. View results in tabs
5. Download findings

### Via REST API
```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is quantum computing?",
    "use_rag": true,
    "num_results": 5
  }'
```

## 🔍 Features Explained

### Agent Communication Flow
```
Query
  ↓
[PLANNER] → Creates research plan
  ↓
[RESEARCHER] → Web search + RAG retrieval
  ↓
[CRITIC] → Evaluates findings
  ↓
[SUMMARIZER] → Final synthesis
  ↓
Results
```

### Logging System
View real-time agent communication in the terminal:
```
[HH:MM:SS] [INFO] [__main__] Initializing Research Graph...
[HH:MM:SS] [INFO] [agents.planner] ============================================================
[HH:MM:SS] [INFO] [agents.planner] AGENT START: PLANNER
[HH:MM:SS] [INFO] [agents.planner] THINKING: Analyzing query...
[HH:MM:SS] [INFO] [agents.planner] OUTPUT: Breaking down the topic...
```

### RAG Pipeline
1. **Upload**: PDF/TXT files via Streamlit
2. **Parse**: Extract text from documents
3. **Chunk**: Split into overlapping chunks (500 tokens, 50 overlap)
4. **Embed**: Convert to embeddings using Sentence Transformers
5. **Store**: Save in FAISS vector store
6. **Retrieve**: Find relevant documents on each query

## 📊 Example Output

The system generates:
- **Research Findings**: Comprehensive information from web + docs
- **Critical Review**: Evaluation of accuracy and gaps
- **Final Summary**: Structured markdown with key takeaways

## 🔧 Configuration

### Environment Variables
```bash
# LLM Settings
GEMINI_API_KEY=               # Required
GEMINI_MODEL=gemini-2.0-flash # Optional
GEMINI_TEMPERATURE=0.7        # Optional
GEMINI_MAX_TOKENS=2048        # Optional

# Search APIs (choose one)
TAVILY_API_KEY=               # Recommended
SERPAPI_API_KEY=              # Alternative
GOOGLE_API_KEY=               # Alternative
GOOGLE_CSE_ID=                # For Google search
```

### RAG Settings
Edit in `rag/document_manager.py`:
```python
DocumentManager(
    chunk_size=500,           # Token chunk size
    chunk_overlap=50,         # Token overlap
    model_name="...",         # Embedding model
    vectorstore_path="..."    # Storage location
)
```

## 📈 Next Steps

- **Conversation Memory**: Save research history
- **Database Backend**: Persistent storage
- **More Tools**: Email, PDF export, citations
- **Advanced Agents**: Fact-checking, source verification
- **User Accounts**: Multi-user support with auth
- **Real-time Streaming**: Stream responses as generated

## 🐛 Troubleshooting

**White screen on Streamlit?**
- Check terminal for errors
- Clear browser cache
- Restart Streamlit

**No search results?**
- Set a search API key in `.env`
- Check API quotas

**PDF loading errors?**
- Ensure pypdf is installed: `pip install pypdf`
- Check PDF is not corrupted

**Import errors?**
- Run: `pip install -r requirements.txt`
- Check Python version (3.11+)

## 📄 License

MIT

## 👨‍💻 Author

Built with ❤️ using modern AI stack

---

**Start researching smarter today!** 🚀
