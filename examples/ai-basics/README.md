# AI Development Basics

This directory contains foundational examples for AI and machine learning development in Python.

## Examples

### 1. Text Classification (`text_classification.py`)
Multiple approaches to text classification:
- **Traditional ML**: TF-IDF + Naive Bayes with scikit-learn
- **Transformers**: Pre-trained models (DistilBERT) for sentiment analysis
- **LLM-based**: Zero-shot classification with Claude
- **Multi-label**: Classifying text into multiple categories

**Usage:**
```bash
python text_classification.py
```

**Key Concepts:**
- Feature extraction (TF-IDF)
- Supervised learning
- Transfer learning with pre-trained models
- Zero-shot learning with LLMs

### 2. Embeddings (`embeddings_example.py`)
Working with text embeddings for semantic understanding:
- **OpenAI Embeddings**: Using OpenAI's embedding API
- **Sentence Transformers**: Local embedding generation
- **Semantic Search**: Finding relevant documents
- **Clustering**: Grouping similar texts
- **Visualization**: 2D projection with PCA

**Usage:**
```bash
python embeddings_example.py
```

**Key Concepts:**
- Vector representations of text
- Cosine similarity
- Semantic search
- Dimensionality reduction

### 3. RAG - Retrieval Augmented Generation (`rag_example.py`)
Building RAG systems to enhance LLM responses:
- **Simple RAG**: Basic retrieval + generation with ChromaDB
- **Advanced RAG**: Document chunking and metadata
- **Re-ranking**: Improving retrieval accuracy

**Usage:**
```bash
python rag_example.py
```

**Key Concepts:**
- Vector databases (ChromaDB)
- Document retrieval
- Context-aware generation
- Hybrid search strategies

## Setup

### Install Dependencies

```bash
pip install scikit-learn transformers torch sentence-transformers chromadb anthropic openai python-dotenv numpy pandas
```

### Environment Variables

Create a `.env` file:
```env
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

## Learning Path

### Beginners
1. Start with **text_classification.py** (sklearn section)
2. Explore **embeddings_example.py** (semantic similarity)
3. Try **text_classification.py** (transformer section)

### Intermediate
1. **embeddings_example.py** (semantic search and clustering)
2. **rag_example.py** (simple RAG)
3. **text_classification.py** (LLM-based classification)

### Advanced
1. **rag_example.py** (advanced chunking and re-ranking)
2. Combine concepts to build custom applications
3. Optimize for production use

## Common Use Cases

### Text Classification
- Sentiment analysis
- Topic categorization
- Spam detection
- Intent recognition

### Embeddings
- Semantic search
- Duplicate detection
- Recommendation systems
- Content clustering

### RAG
- Question answering systems
- Chatbots with knowledge bases
- Document analysis
- Research assistants

## Key Libraries

### Machine Learning
- **scikit-learn**: Traditional ML algorithms
- **transformers**: State-of-the-art NLP models
- **sentence-transformers**: Efficient sentence embeddings

### Vector Databases
- **ChromaDB**: Lightweight vector database
- **FAISS**: Fast similarity search
- **Pinecone**: Managed vector database

### LLM APIs
- **OpenAI**: GPT models and embeddings
- **Anthropic**: Claude models
- **Together AI**: Various open-source models

## Performance Tips

### Embeddings
- Cache embeddings to avoid re-computation
- Use smaller models for faster inference
- Batch encode documents when possible

### RAG
- Chunk documents appropriately (100-500 words)
- Include metadata for better filtering
- Use hybrid search (keyword + semantic)
- Re-rank results for better accuracy

### Classification
- Use pre-trained models when possible
- Fine-tune on domain-specific data
- Consider zero-shot for quick prototypes

## Troubleshooting

### Out of Memory
- Reduce batch sizes
- Use smaller models
- Process data in chunks

### Poor Accuracy
- Check data quality and labeling
- Try different models
- Adjust hyperparameters
- Add more training data

### Slow Performance
- Use GPU acceleration
- Reduce model size
- Optimize retrieval strategy
- Cache intermediate results

## Next Steps

1. **Fine-tuning**: Adapt pre-trained models to your domain
2. **Production**: Deploy models with FastAPI or similar
3. **Monitoring**: Track model performance in production
4. **Advanced RAG**: Multi-query, query decomposition, agents

## Resources

- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- [Sentence Transformers](https://www.sbert.net/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [RAG Guide](https://www.anthropic.com/index/retrieval-augmented-generation)
