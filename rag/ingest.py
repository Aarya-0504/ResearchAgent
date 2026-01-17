"""
Document Ingestion Module

This module provides legacy support for document ingestion.
For new code, use DocumentManager from document_manager.py instead.
"""

from document_manager import DocumentManager


def ingest_docs(docs: list[str]) -> None:
    """
    Legacy function to ingest raw text documents.
    
    Args:
        docs (list[str]): List of document strings to ingest.
        
    Example:
        >>> ingest_docs(["Document 1 content", "Document 2 content"])
    """
    doc_manager = DocumentManager()
    
    # Try to load existing vectorstore, create new if doesn't exist
    try:
        doc_manager.load_vectorstore()
    except:
        pass
    
    # Convert strings to documents and ingest
    documents = [
        doc_manager.load_text_string(doc, metadata={"source": f"doc_{i}"})[0]
        for i, doc in enumerate(docs)
    ]
    
    doc_manager.ingest_documents(documents)
    doc_manager.save_vectorstore()
