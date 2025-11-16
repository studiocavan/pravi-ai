"""
Text Embeddings Example

This example demonstrates how to generate and use text embeddings for:
- Semantic similarity
- Clustering
- Vector search
- Recommendation systems
"""

import os
import numpy as np
from dotenv import load_dotenv

load_dotenv()


def openai_embeddings():
    """Generate embeddings using OpenAI"""
    from openai import OpenAI

    print("OpenAI Embeddings")
    print("="*50)

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    texts = [
        "The cat sat on the mat",
        "A feline rested on the rug",
        "Dogs are loyal pets",
        "Python is a programming language",
        "Machine learning is fascinating"
    ]

    print("\nGenerating embeddings for texts...\n")

    embeddings = []
    for text in texts:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        embeddings.append(response.data[0].embedding)

    # Calculate cosine similarity
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    print("Similarity Matrix:")
    print("-" * 50)

    for i, text1 in enumerate(texts):
        for j, text2 in enumerate(texts):
            if i < j:
                similarity = cosine_similarity(embeddings[i], embeddings[j])
                print(f"\n'{text1}'")
                print(f"  vs '{text2}'")
                print(f"  Similarity: {similarity:.4f}")

    print("\n" + "="*50 + "\n")


def sentence_transformers_embeddings():
    """Generate embeddings using sentence-transformers"""
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity

    print("Sentence-Transformers Embeddings")
    print("="*50)

    # Load model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    texts = [
        "I love pizza",
        "Pizza is my favorite food",
        "I enjoy Italian cuisine",
        "Quantum physics is complex",
        "Machine learning models"
    ]

    print(f"\nModel: {model}")
    print(f"Embedding dimension: {model.get_sentence_embedding_dimension()}\n")

    # Generate embeddings
    embeddings = model.encode(texts)

    print("Embeddings generated:")
    for text, emb in zip(texts, embeddings):
        print(f"  '{text}': shape {emb.shape}")

    # Find most similar pairs
    print("\nMost similar text pairs:")
    print("-" * 50)

    similarities = cosine_similarity(embeddings)

    # Get top 3 similar pairs
    pairs = []
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            pairs.append((i, j, similarities[i][j]))

    pairs.sort(key=lambda x: x[2], reverse=True)

    for i, j, sim in pairs[:3]:
        print(f"\n'{texts[i]}'")
        print(f"  vs '{texts[j]}'")
        print(f"  Similarity: {sim:.4f}")

    print("\n" + "="*50 + "\n")


def semantic_search():
    """Semantic search using embeddings"""
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity

    print("Semantic Search Example")
    print("="*50)

    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Document corpus
    documents = [
        "Python is a high-level programming language",
        "Machine learning is a subset of artificial intelligence",
        "Neural networks are inspired by biological neurons",
        "Deep learning uses multiple layers of neural networks",
        "Natural language processing deals with text and speech",
        "Computer vision enables machines to interpret images",
        "Reinforcement learning learns through trial and error",
        "Supervised learning uses labeled training data"
    ]

    # Generate document embeddings
    doc_embeddings = model.encode(documents)

    # Search queries
    queries = [
        "What is deep learning?",
        "How do computers understand language?",
        "Programming with Python"
    ]

    print("\nSearching documents...\n")

    for query in queries:
        print(f"Query: '{query}'")
        print("Top 3 results:")

        # Generate query embedding
        query_embedding = model.encode([query])

        # Calculate similarities
        similarities = cosine_similarity(query_embedding, doc_embeddings)[0]

        # Get top 3 results
        top_indices = np.argsort(similarities)[::-1][:3]

        for rank, idx in enumerate(top_indices, 1):
            print(f"  {rank}. {documents[idx]}")
            print(f"     Similarity: {similarities[idx]:.4f}")

        print()

    print("="*50 + "\n")


def clustering_with_embeddings():
    """Cluster documents using embeddings"""
    from sentence_transformers import SentenceTransformer
    from sklearn.cluster import KMeans
    import numpy as np

    print("Clustering with Embeddings")
    print("="*50)

    model = SentenceTransformer('all-MiniLM-L6-v2')

    documents = [
        # Sports
        "Football is a popular sport worldwide",
        "Basketball players are very athletic",
        "Tennis requires skill and endurance",
        # Technology
        "Artificial intelligence is transforming industries",
        "Cloud computing provides scalable resources",
        "Cybersecurity protects digital assets",
        # Food
        "Italian pasta is delicious",
        "Sushi is a Japanese delicacy",
        "French cuisine is world-renowned"
    ]

    # Generate embeddings
    embeddings = model.encode(documents)

    # Cluster into 3 groups
    n_clusters = 3
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(embeddings)

    print(f"\nClustered {len(documents)} documents into {n_clusters} groups:\n")

    for cluster_id in range(n_clusters):
        cluster_docs = [doc for doc, c in zip(documents, clusters) if c == cluster_id]
        print(f"Cluster {cluster_id + 1}:")
        for doc in cluster_docs:
            print(f"  - {doc}")
        print()

    print("="*50 + "\n")


def embedding_visualization():
    """Visualize embeddings in 2D using dimensionality reduction"""
    from sentence_transformers import SentenceTransformer
    from sklearn.decomposition import PCA

    print("Embedding Visualization (2D PCA)")
    print("="*50)

    model = SentenceTransformer('all-MiniLM-L6-v2')

    texts = [
        "dog", "cat", "puppy", "kitten",  # Animals
        "car", "truck", "vehicle", "automobile",  # Vehicles
        "happy", "joyful", "cheerful", "glad",  # Emotions
    ]

    # Generate embeddings
    embeddings = model.encode(texts)

    # Reduce to 2D
    pca = PCA(n_components=2)
    embeddings_2d = pca.fit_transform(embeddings)

    print("\n2D coordinates:")
    for text, coords in zip(texts, embeddings_2d):
        print(f"  {text:12s}: ({coords[0]:7.3f}, {coords[1]:7.3f})")

    print(f"\nExplained variance: {sum(pca.explained_variance_ratio_):.2%}")
    print("\n" + "="*50 + "\n")


def main():
    """Run all embedding examples"""
    try:
        # OpenAI embeddings (requires API key)
        try:
            openai_embeddings()
        except Exception as e:
            print(f"OpenAI embeddings skipped: {e}")
            print("Set OPENAI_API_KEY in .env to run this example\n")

        # Sentence transformers (local)
        sentence_transformers_embeddings()
        semantic_search()
        clustering_with_embeddings()
        embedding_visualization()

    except Exception as e:
        print(f"Error: {e}")
        print("\nInstall dependencies with:")
        print("pip install sentence-transformers scikit-learn numpy")


if __name__ == "__main__":
    main()
