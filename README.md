# Pravi AI - Local LLM Chat Application

A full-stack AI chat application with local LLM hosting, RAG (Retrieval Augmented Generation), and MCP (Model Context Protocol) integration.

## Features

- 🤖 **Local LLM**: Run models locally using Ollama (4-12GB GPU memory)
- 📚 **RAG System**: Enhanced responses using ChromaDB vector database
- 🔧 **MCP Integration**: Access to tools and resources via Model Context Protocol
- 🎨 **Modern UI**: Clean, responsive web interface
- ⚡ **Fast API**: FastAPI backend with async support
- 🔒 **Privacy**: Everything runs locally - no data sent to external APIs

## Architecture

```
┌─────────────┐
│   Frontend  │  HTML/CSS/JS - User Interface
│  (Browser)  │
└──────┬──────┘
       │ HTTP/REST
┌──────▼──────┐
│   Backend   │  FastAPI - API Server
│  (Python)   │
└──┬────┬────┬┘
   │    │    │
   ▼    ▼    ▼
┌────┐┌────┐┌────┐
│LLM ││RAG ││MCP │  Services
│    ││    ││    │
└────┘└────┘└────┘
```

## Repository Structure

```
pravi-ai/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── llm_service.py       # Local LLM integration (Ollama)
│   ├── rag_service.py       # RAG with ChromaDB
│   ├── mcp_service.py       # MCP integration
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html          # Main UI
│   ├── style.css           # Styling
│   └── app.js              # Frontend logic
├── examples/               # Additional examples
│   ├── llm-interaction/
│   ├── mcp-integration/
│   └── ai-basics/
├── data/                   # Data directory
│   └── documents/          # Document storage
└── README.md              # This file
```

## Quick Start

### Prerequisites

- Python 3.8+
- GPU with 4-12GB VRAM (recommended, but CPU works too)
- Node.js and npm (for MCP servers)

### 1. Install Ollama

First, install Ollama to run local LLMs:

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS:**
```bash
brew install ollama
```

**Windows:**
Download from [ollama.com](https://ollama.com)

### 2. Download a Model

Choose a model based on your GPU memory:

```bash
# For 4-6GB GPU (recommended for most users)
ollama pull mistral:7b

# For 8-10GB GPU (better performance)
ollama pull llama3.1:8b

# For 4GB GPU (most efficient)
ollama pull phi3:mini
```

Start Ollama server:
```bash
ollama serve
```

### 3. Set Up Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python main.py
```

The backend will start on `http://localhost:8000`

### 4. Open Frontend

Simply open `frontend/index.html` in your web browser, or serve it with:

```bash
cd frontend
python -m http.server 3000
```

Then visit `http://localhost:3000`

### 5. (Optional) Set Up MCP Server

To enable MCP tools:

```bash
npm install -g @modelcontextprotocol/server-filesystem
```

## Usage

### Chat Interface

1. Open the web interface
2. Check that all services show as online (green dots)
3. Type your question in the input box
4. Press Enter or click Send

### Features

- **RAG Toggle**: Enable/disable knowledge base retrieval
- **MCP Toggle**: Enable/disable MCP tools
- **View Documents**: Browse the knowledge base
- **Add Documents**: Enhance responses with custom content

## API Endpoints

### Health Check
```
GET /health
```

### Chat
```
POST /chat
{
  "message": "Your question",
  "use_rag": true,
  "use_mcp": false
}
```

### Documents
```
POST /documents        # Add document
GET /documents         # List documents
```

## Recommended Models

| GPU VRAM | Model | Command | Quality |
|----------|-------|---------|---------|
| 4GB | Phi-3 Mini | `ollama pull phi3:mini` | Good |
| 4-6GB | Mistral 7B | `ollama pull mistral:7b` | Excellent |
| 8-10GB | Llama 3.1 8B | `ollama pull llama3.1:8b` | Excellent |
| 10-12GB | Gemma 2 9B | `ollama pull gemma2:9b` | Outstanding |

## Troubleshooting

### LLM shows as offline
- Ensure Ollama is running: `ollama serve`
- Check you've downloaded a model: `ollama list`

### Slow responses
- Use a smaller model (phi3:mini)
- Check GPU is being utilized

### Backend errors
- Verify port 8000 is available
- Check all dependencies are installed

## Additional Examples

The `examples/` directory contains standalone examples for:

- **LLM Interaction**: OpenAI, Anthropic, streaming, function calling
- **MCP Integration**: Client basics, tool usage, resources
- **AI Basics**: Text classification, embeddings, RAG

Run any example:
```bash
python examples/llm-interaction/openai_example.py
```

## Advanced Configuration

### Change Default Model

Edit `backend/llm_service.py`:
```python
self.default_model = "llama3.1:8b"  # Your preferred model
```

### Add More MCP Servers

Edit `backend/mcp_service.py` to configure different servers (filesystem, SQLite, GitHub, etc.)

## Contributing

Contributions welcome! Areas for improvement:
- Streaming responses (WebSocket)
- Chat history persistence
- Advanced RAG techniques
- More MCP integrations

## License

MIT License

## Resources

- [Ollama Documentation](https://ollama.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [ChromaDB Documentation](https://docs.trychroma.com)
- [MCP Specification](https://spec.modelcontextprotocol.io)
