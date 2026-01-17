from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

VECTOR_DB_PATH = "faiss_index"

def load_vectorstore():
    return FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
