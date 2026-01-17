"""
Document Management Module

This module provides document ingestion and management capabilities for RAG systems.
Supports multiple document types including PDFs, text files, and raw strings.

Classes:
    DocumentManager: Handles document loading, preprocessing, and ingestion into vector stores.
"""

from typing import List, Optional
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document


class DocumentManager:
    """
    Manages document ingestion and vector store operations for RAG systems.
    
    This class handles loading documents from various sources (PDFs, text files),
    chunking them appropriately, and storing them in a FAISS vector database.
    
    Attributes:
        chunk_size (int): Size of text chunks for splitting documents.
        chunk_overlap (int): Overlap between consecutive chunks.
        model_name (str): HuggingFace model name for embeddings.
        vectorstore_path (str): Path to store/load FAISS index.
        vectorstore (FAISS): The FAISS vector store instance.
        embeddings (HuggingFaceEmbeddings): Embeddings model instance.
    """
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        vectorstore_path: str = "faiss_index"
    ):
        """
        Initialize the DocumentManager.
        
        Args:
            chunk_size (int): Size of text chunks. Defaults to 500.
            chunk_overlap (int): Overlap between chunks. Defaults to 50.
            model_name (str): HuggingFace embedding model. 
                Defaults to "sentence-transformers/all-MiniLM-L6-v2".
            vectorstore_path (str): Path for FAISS storage. Defaults to "faiss_index".
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.model_name = model_name
        self.vectorstore_path = vectorstore_path
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name=self.model_name)
        self.vectorstore: Optional[FAISS] = None
    
    def load_pdf(self, pdf_path: str) -> List[Document]:
        """
        Load documents from a PDF file.
        
        Args:
            pdf_path (str): Path to the PDF file.
            
        Returns:
            List[Document]: List of loaded document objects.
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist.
            ValueError: If PDF cannot be parsed.
        """
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            print(f"Loaded {len(documents)} pages from {pdf_path}")
            return documents
        except FileNotFoundError:
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        except Exception as e:
            raise ValueError(f"Error loading PDF {pdf_path}: {str(e)}")
    
    def load_text_file(self, text_path: str) -> List[Document]:
        """
        Load documents from a plain text file.
        
        Args:
            text_path (str): Path to the text file.
            
        Returns:
            List[Document]: List of document objects with file content.
            
        Raises:
            FileNotFoundError: If text file doesn't exist.
        """
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                content = f.read()
            doc = Document(page_content=content, metadata={"source": text_path})
            print(f"Loaded text file: {text_path}")
            return [doc]
        except FileNotFoundError:
            raise FileNotFoundError(f"Text file not found: {text_path}")
        except Exception as e:
            raise ValueError(f"Error loading text file {text_path}: {str(e)}")
    
    def load_text_string(self, text: str, metadata: Optional[dict] = None) -> List[Document]:
        """
        Create a document from a raw text string.
        
        Args:
            text (str): Raw text content.
            metadata (dict, optional): Additional metadata for the document.
            
        Returns:
            List[Document]: List containing a single document.
        """
        if not metadata:
            metadata = {"source": "raw_text"}
        doc = Document(page_content=text, metadata=metadata)
        print("Created document from raw text")
        return [doc]
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks using CharacterTextSplitter.
        
        Args:
            documents (List[Document]): Documents to split.
            
        Returns:
            List[Document]: Chunked documents.
        """
        splitter = CharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separator="\n"
        )
        chunks = splitter.split_documents(documents)
        print(f"Split documents into {len(chunks)} chunks")
        return chunks
    
    def ingest_documents(self, documents: List[Document]) -> FAISS:
        """
        Ingest documents into the vector store.
        
        Args:
            documents (List[Document]): Documents to ingest.
            
        Returns:
            FAISS: The updated vector store.
        """
        if not documents:
            raise ValueError("No documents provided for ingestion")
        
        # Split documents into chunks
        chunks = self.split_documents(documents)
        
        # Create or update vector store
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
            print(f"Created new FAISS vectorstore with {len(chunks)} chunks")
        else:
            self.vectorstore.add_documents(chunks)
            print(f"Added {len(chunks)} chunks to existing vectorstore")
        
        return self.vectorstore
    
    def save_vectorstore(self) -> None:
        """
        Save the current vector store to disk.
        
        Raises:
            RuntimeError: If vectorstore hasn't been created yet.
        """
        if self.vectorstore is None:
            raise RuntimeError("No vectorstore to save. Ingest documents first.")
        
        self.vectorstore.save_local(self.vectorstore_path)
        print(f"Saved vectorstore to {self.vectorstore_path}")
    
    def load_vectorstore(self) -> FAISS:
        """
        Load vector store from disk.
        
        Returns:
            FAISS: The loaded vector store.
            
        Raises:
            FileNotFoundError: If vectorstore doesn't exist on disk.
        """
        try:
            self.vectorstore = FAISS.load_local(
                self.vectorstore_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            print(f"Loaded vectorstore from {self.vectorstore_path}")
            return self.vectorstore
        except Exception as e:
            raise FileNotFoundError(f"Cannot load vectorstore: {str(e)}")
    
    def search(self, query: str, k: int = 3) -> List[Document]:
        """
        Search the vector store for relevant documents.
        
        Args:
            query (str): Search query.
            k (int): Number of results to return. Defaults to 3.
            
        Returns:
            List[Document]: Most relevant documents.
            
        Raises:
            RuntimeError: If vectorstore hasn't been loaded/created.
        """
        if self.vectorstore is None:
            raise RuntimeError("Vectorstore not initialized. Load or ingest documents first.")
        
        results = self.vectorstore.similarity_search(query, k=k)
        print(f"Found {len(results)} relevant documents")
        return results
    
    def add_documents(self, file_paths: List[str]) -> None:
        """
        Add multiple documents from file paths (PDFs or text files).
        
        Args:
            file_paths (List[str]): List of file paths to load.
        """
        all_documents = []
        
        for file_path in file_paths:
            path = Path(file_path)
            
            try:
                if path.suffix.lower() == '.pdf':
                    docs = self.load_pdf(str(path))
                elif path.suffix.lower() in ['.txt', '.md']:
                    docs = self.load_text_file(str(path))
                else:
                    print(f"Skipping unsupported file type: {path.suffix}")
                    continue
                
                all_documents.extend(docs)
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")
        
        if all_documents:
            self.ingest_documents(all_documents)
            self.save_vectorstore()
        else:
            print("No documents were successfully loaded")
