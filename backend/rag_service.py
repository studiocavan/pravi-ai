"""
RAG Service - Retrieval Augmented Generation using ChromaDB
Handles document storage, embedding, and retrieval
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import uuid
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class RAGService:
    """Service for managing RAG knowledge base with ChromaDB"""

    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize RAG service with ChromaDB

        Args:
            persist_directory: Directory to persist the vector database
        """
        # Create persistent ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get or create collection
        # Using default embedding function (all-MiniLM-L6-v2)
        try:
            self.collection = self.client.get_collection(name="documents")
        except:
            self.collection = self.client.create_collection(
                name="documents",
                metadata={"description": "Knowledge base documents"}
            )

        # Load initial documents if collection is empty
        if self.collection.count() == 0:
            self._load_initial_documents()

    def check_health(self) -> bool:
        """Check if RAG service is working"""
        try:
            self.collection.count()
            return True
        except Exception:
            return False

    def add_document(
        self,
        content: str,
        metadata: Optional[Dict] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """
        Add a document to the knowledge base

        Args:
            content: Document text content
            metadata: Optional metadata (source, title, etc.)
            doc_id: Optional custom document ID

        Returns:
            Document ID
        """
        if not doc_id:
            doc_id = str(uuid.uuid4())

        metadata = metadata or {}
        metadata["length"] = len(content)

        self.collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )

        return doc_id

    def add_documents_batch(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add multiple documents at once

        Args:
            documents: List of document texts
            metadatas: Optional list of metadata dicts
            ids: Optional list of custom IDs

        Returns:
            List of document IDs
        """
        if not ids:
            ids = [str(uuid.uuid4()) for _ in documents]

        if not metadatas:
            metadatas = [{}] * len(documents)

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        return ids

    def search(
        self,
        query: str,
        top_k: int = 3,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for relevant documents

        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            List of relevant documents with metadata and scores
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=filter_metadata
            )

            # Format results
            documents = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    documents.append({
                        "id": results["ids"][0][i],
                        "content": doc,
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i] if "distances" in results else None,
                        "source": results["metadatas"][0][i].get("source", "Unknown")
                    })

            return documents

        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID"""
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception:
            return False

    def list_documents(self, limit: int = 100) -> List[Dict]:
        """
        List all documents in the knowledge base

        Args:
            limit: Maximum number of documents to return

        Returns:
            List of documents with metadata
        """
        try:
            results = self.collection.get(limit=limit)

            documents = []
            for i in range(len(results["ids"])):
                documents.append({
                    "id": results["ids"][i],
                    "content": results["documents"][i][:200] + "...",  # Preview
                    "metadata": results["metadatas"][i]
                })

            return documents

        except Exception as e:
            logger.error(f"List error: {e}")
            return []

    def get_stats(self) -> Dict:
        """Get statistics about the knowledge base"""
        return {
            "total_documents": self.collection.count(),
            "collection_name": self.collection.name,
            "metadata": self.collection.metadata
        }

    def clear_all(self):
        """Clear all documents (use with caution!)"""
        try:
            self.client.delete_collection(name="documents")
            self.collection = self.client.create_collection(
                name="documents",
                metadata={"description": "Knowledge base documents"}
            )
            return True
        except Exception:
            return False

    def _load_initial_documents(self):
        """Load some initial example documents"""
        initial_docs = [
            {
                "content": "Python is a high-level, interpreted programming language known for its simplicity and readability. It was created by Guido van Rossum and first released in 1991.",
                "metadata": {"source": "Python Basics", "category": "programming"}
            },
            {
                "content": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing algorithms that can access data and learn from it.",
                "metadata": {"source": "ML Introduction", "category": "ai"}
            },
            {
                "content": "FastAPI is a modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints. It's designed to be easy to use and provides automatic API documentation.",
                "metadata": {"source": "Web Frameworks", "category": "programming"}
            },
            {
                "content": "Retrieval Augmented Generation (RAG) is a technique that combines information retrieval with text generation. It enhances LLM responses by providing relevant context from a knowledge base.",
                "metadata": {"source": "RAG Guide", "category": "ai"}
            },
            {
                "content": "Vector databases store data as high-dimensional vectors, enabling semantic search and similarity matching. They are essential for modern AI applications like RAG systems.",
                "metadata": {"source": "Vector DBs", "category": "database"}
            },
            {
                "content": "The Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to LLMs. It enables secure access to tools, data sources, and services.",
                "metadata": {"source": "MCP Documentation", "category": "ai"}
            },
            {
                "content": "GPU memory (VRAM) is crucial for running large language models. Models like Llama 3.1 8B typically require 8-10GB of VRAM, while smaller models like Phi-3 can run on 4GB.",
                "metadata": {"source": "Hardware Guide", "category": "hardware"}
            },
            {
                "content": "Ollama is a tool for running large language models locally. It makes it easy to download, run, and manage various open-source LLMs on your own hardware.",
                "metadata": {"source": "Ollama Guide", "category": "tools"}
            }
        ]

        documents = [doc["content"] for doc in initial_docs]
        metadatas = [doc["metadata"] for doc in initial_docs]

        self.add_documents_batch(documents=documents, metadatas=metadatas)
        logger.info(f"Loaded {len(documents)} initial documents into knowledge base")
