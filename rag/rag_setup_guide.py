"""
RAG Setup and Usage Guide

This module demonstrates how to use the DocumentManager class for RAG ingestion.
"""

from rag.document_manager import DocumentManager
from pathlib import Path


def example_basic_usage():
    """
    Example 1: Basic usage with PDF files
    """
    print("=" * 60)
    print("EXAMPLE 1: Loading PDF Files")
    print("=" * 60)
    
    # Initialize document manager
    doc_manager = DocumentManager(
        chunk_size=500,
        chunk_overlap=50,
        vectorstore_path="faiss_index"
    )
    
    # Load a single PDF
    documents = doc_manager.load_pdf("path/to/document.pdf")
    
    # Ingest into vector store
    doc_manager.ingest_documents(documents)
    
    # Save for future use
    doc_manager.save_vectorstore()
    print()


def example_multiple_files():
    """
    Example 2: Loading multiple file types
    """
    print("=" * 60)
    print("EXAMPLE 2: Loading Multiple Files")
    print("=" * 60)
    
    doc_manager = DocumentManager()
    
    # List of files to ingest
    files = [
        "research_paper.pdf",
        "notes.txt",
        "documentation.md"
    ]
    
    # Add all documents
    doc_manager.add_documents(files)
    print()


def example_raw_text():
    """
    Example 3: Adding raw text directly
    """
    print("=" * 60)
    print("EXAMPLE 3: Adding Raw Text")
    print("=" * 60)
    
    doc_manager = DocumentManager()
    
    # Load existing vectorstore first
    doc_manager.load_vectorstore()
    
    # Add raw text
    text = """
    Quantum computing represents a paradigm shift in computational power.
    Unlike classical computers, quantum computers use qubits which can exist
    in superposition states, allowing for exponential computational advantages.
    """
    
    docs = doc_manager.load_text_string(
        text,
        metadata={"source": "quantum_notes.txt", "category": "physics"}
    )
    
    doc_manager.ingest_documents(docs)
    doc_manager.save_vectorstore()
    print()


def example_search():
    """
    Example 4: Searching the vector store
    """
    print("=" * 60)
    print("EXAMPLE 4: Searching Documents")
    print("=" * 60)
    
    doc_manager = DocumentManager()
    doc_manager.load_vectorstore()
    
    # Search for relevant documents
    query = "quantum computing applications"
    results = doc_manager.search(query, k=5)
    
    print(f"\nFound {len(results)} relevant documents:")
    for i, doc in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Source: {doc.metadata.get('source', 'unknown')}")
        print(f"Content: {doc.page_content[:200]}...")
    print()


def example_incremental_ingestion():
    """
    Example 5: Incrementally add documents over time
    """
    print("=" * 60)
    print("EXAMPLE 5: Incremental Document Ingestion")
    print("=" * 60)
    
    doc_manager = DocumentManager(vectorstore_path="incremental_index")
    
    # Load existing or create new
    try:
        doc_manager.load_vectorstore()
        print("Loaded existing vectorstore")
    except:
        print("Creating new vectorstore")
    
    # Add new documents
    new_files = ["new_research.pdf", "updates.txt"]
    doc_manager.add_documents(new_files)
    
    print()


def example_custom_chunking():
    """
    Example 6: Custom chunk sizes for different use cases
    """
    print("=" * 60)
    print("EXAMPLE 6: Custom Chunking Parameters")
    print("=" * 60)
    
    # Small chunks for detail-oriented tasks
    small_chunk_manager = DocumentManager(
        chunk_size=200,
        chunk_overlap=20,
        vectorstore_path="small_chunks_index"
    )
    
    # Large chunks for big-picture understanding
    large_chunk_manager = DocumentManager(
        chunk_size=1000,
        chunk_overlap=100,
        vectorstore_path="large_chunks_index"
    )
    
    print("✓ Managers configured with custom chunking parameters")
    print()


if __name__ == "__main__":
    """
    Run examples (uncomment the ones you want to use)
    """
    
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " RAG SETUP AND USAGE EXAMPLES ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    # Uncomment to run examples:
    # example_basic_usage()
    # example_multiple_files()
    # example_raw_text()
    # example_search()
    # example_incremental_ingestion()
    # example_custom_chunking()
    
    print("\n✓ Ready to use! Import DocumentManager in your code:\n")
    print("    from rag.document_manager import DocumentManager")
    print("\n    doc_manager = DocumentManager()")
    print("    doc_manager.add_documents(['file1.pdf', 'file2.txt'])")
    print("    results = doc_manager.search('your query')")
    print("\n")
