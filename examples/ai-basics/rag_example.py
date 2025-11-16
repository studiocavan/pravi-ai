"""
RAG (Retrieval Augmented Generation) Example

This example demonstrates how to implement RAG to enhance LLM responses
with relevant context from a knowledge base.

RAG combines:
1. Document retrieval (using embeddings and vector search)
2. LLM generation (using retrieved context)
"""

import os
from dotenv import load_dotenv
from typing import List

load_dotenv()


def simple_rag_with_chromadb():
    """Simple RAG implementation using ChromaDB"""
    import chromadb
    from chromadb.utils import embedding_functions
    from anthropic import Anthropic

    print("Simple RAG with ChromaDB")
    print("="*50)

    # Initialize ChromaDB
    client = chromadb.Client()

    # Create collection with sentence transformer embeddings
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    collection = client.create_collection(
        name="knowledge_base",
        embedding_function=sentence_transformer_ef
    )

    # Add documents to knowledge base
    documents = [
        "Python was created by Guido van Rossum and released in 1991.",
        "Python is known for its simple and readable syntax.",
        "Django is a popular web framework for Python.",
        "FastAPI is a modern, fast web framework for building APIs with Python.",
        "NumPy is fundamental for scientific computing in Python.",
        "Pandas provides data structures for data analysis in Python.",
        "Machine learning in Python often uses libraries like scikit-learn and TensorFlow.",
        "Python supports multiple programming paradigms including OOP and functional programming."
    ]

    collection.add(
        documents=documents,
        ids=[f"doc_{i}" for i in range(len(documents))]
    )

    print(f"\nAdded {len(documents)} documents to knowledge base\n")

    # RAG function
    def rag_query(question: str, n_results: int = 3) -> str:
        """Perform RAG query"""

        # 1. Retrieve relevant documents
        results = collection.query(
            query_texts=[question],
            n_results=n_results
        )

        retrieved_docs = results['documents'][0]

        print(f"Question: {question}")
        print(f"\nRetrieved {len(retrieved_docs)} relevant documents:")
        for i, doc in enumerate(retrieved_docs, 1):
            print(f"  {i}. {doc}")

        # 2. Generate response with LLM
        context = "\n".join(retrieved_docs)

        anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        message = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"""Use the following context to answer the question. If the context doesn't contain the answer, say so.

Context:
{context}

Question: {question}

Answer:"""
            }]
        )

        return message.content[0].text

    # Test queries
    questions = [
        "When was Python created?",
        "What are some popular Python web frameworks?",
        "What is Python used for in data science?"
    ]

    for question in questions:
        answer = rag_query(question)
        print(f"\nAnswer: {answer}")
        print("\n" + "-"*50 + "\n")

    print("="*50 + "\n")


def advanced_rag_with_chunking():
    """Advanced RAG with document chunking and metadata"""
    import chromadb
    from chromadb.utils import embedding_functions
    from anthropic import Anthropic

    print("Advanced RAG with Document Chunking")
    print("="*50)

    # Initialize ChromaDB
    client = chromadb.Client()

    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    collection = client.create_collection(
        name="advanced_kb",
        embedding_function=sentence_transformer_ef
    )

    # Longer documents that will be chunked
    long_documents = [
        {
            "title": "Python History",
            "content": """Python is a high-level programming language created by Guido van Rossum.
            It was first released in 1991. Python's design philosophy emphasizes code readability
            with significant use of whitespace. Python is dynamically typed and garbage-collected."""
        },
        {
            "title": "Web Development",
            "content": """Python offers several frameworks for web development. Django is a
            high-level framework that encourages rapid development. Flask is a micro-framework
            that is lightweight and flexible. FastAPI is a modern framework optimized for
            building APIs with automatic documentation."""
        },
        {
            "title": "Data Science",
            "content": """Python is widely used in data science. NumPy provides support for
            large arrays and matrices. Pandas offers data structures for data manipulation.
            Matplotlib is used for visualization. Scikit-learn provides machine learning algorithms."""
        }
    ]

    # Chunk documents
    def chunk_text(text: str, chunk_size: int = 100) -> List[str]:
        """Split text into chunks by words"""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks

    # Add chunked documents with metadata
    chunk_id = 0
    for doc in long_documents:
        chunks = chunk_text(doc['content'])
        for i, chunk in enumerate(chunks):
            collection.add(
                documents=[chunk],
                metadatas=[{
                    "title": doc['title'],
                    "chunk": i,
                    "total_chunks": len(chunks)
                }],
                ids=[f"chunk_{chunk_id}"]
            )
            chunk_id += 1

    print(f"\nAdded {chunk_id} chunks from {len(long_documents)} documents\n")

    # Enhanced RAG query
    def enhanced_rag_query(question: str) -> str:
        # Retrieve with metadata
        results = collection.query(
            query_texts=[question],
            n_results=3
        )

        print(f"Question: {question}\n")
        print("Retrieved chunks:")

        context_parts = []
        for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
            print(f"  - From '{metadata['title']}' (chunk {metadata['chunk']+1}/{metadata['total_chunks']})")
            print(f"    {doc[:100]}...")
            context_parts.append(f"[{metadata['title']}]: {doc}")

        context = "\n\n".join(context_parts)

        # Generate answer
        anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        message = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"""Answer the question using the provided context. Cite the source when possible.

Context:
{context}

Question: {question}

Answer:"""
            }]
        )

        return message.content[0].text

    # Test queries
    questions = [
        "Who created Python and when?",
        "What frameworks can I use for web development?",
        "What libraries are used for data science?"
    ]

    for question in questions:
        answer = enhanced_rag_query(question)
        print(f"\nAnswer: {answer}")
        print("\n" + "-"*50 + "\n")

    print("="*50 + "\n")


def rag_with_reranking():
    """RAG with result re-ranking for better accuracy"""
    from sentence_transformers import SentenceTransformer, util
    from anthropic import Anthropic
    import torch

    print("RAG with Re-ranking")
    print("="*50)

    # Load models
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    # Knowledge base
    documents = [
        "The Eiffel Tower is located in Paris, France.",
        "Python is a programming language.",
        "Paris is the capital of France.",
        "The Eiffel Tower was completed in 1889.",
        "Guido van Rossum created Python.",
        "France is a country in Europe.",
        "The Eiffel Tower is 330 meters tall.",
        "Python is popular for data science."
    ]

    # Encode documents
    doc_embeddings = embedding_model.encode(documents, convert_to_tensor=True)

    def rag_with_rerank(question: str, top_k: int = 3) -> str:
        # Initial retrieval (get more than needed)
        query_embedding = embedding_model.encode(question, convert_to_tensor=True)

        # Calculate similarities
        similarities = util.cos_sim(query_embedding, doc_embeddings)[0]

        # Get top 6 candidates
        top_candidates = torch.topk(similarities, k=min(6, len(documents)))

        # Re-rank candidates (in practice, use a cross-encoder here)
        reranked_indices = top_candidates.indices[:top_k]

        retrieved_docs = [documents[idx] for idx in reranked_indices]

        print(f"Question: {question}")
        print(f"\nTop {top_k} re-ranked documents:")
        for i, doc in enumerate(retrieved_docs, 1):
            print(f"  {i}. {doc}")

        # Generate answer
        context = "\n".join(retrieved_docs)

        anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        message = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": f"""Context: {context}

Question: {question}

Provide a concise answer based on the context."""
            }]
        )

        return message.content[0].text

    # Test
    questions = [
        "How tall is the Eiffel Tower?",
        "Where is the Eiffel Tower located?",
    ]

    for question in questions:
        answer = rag_with_rerank(question)
        print(f"\nAnswer: {answer}")
        print("\n" + "-"*50 + "\n")

    print("="*50 + "\n")


def main():
    """Run RAG examples"""
    try:
        simple_rag_with_chromadb()
        advanced_rag_with_chunking()
        rag_with_reranking()

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure to:")
        print("1. Install: pip install chromadb sentence-transformers anthropic")
        print("2. Set ANTHROPIC_API_KEY in .env file")


if __name__ == "__main__":
    main()
