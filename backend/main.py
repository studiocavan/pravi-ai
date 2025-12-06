"""
Backend API for AI Chat Application
Features: Local LLM (Ollama), RAG (ChromaDB), MCP Integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from rag_service import RAGService
from llm_service import LLMService
from mcp_service import MCPService

# Initialize FastAPI app
app = FastAPI(title="Pravi AI Backend", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
rag_service = RAGService()
llm_service = LLMService()
mcp_service = MCPService()


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    use_rag: bool = True
    use_mcp: bool = False


class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = None
    mcp_tools_used: Optional[List[str]] = None


class DocumentRequest(BaseModel):
    content: str
    metadata: Optional[dict] = None


class HealthResponse(BaseModel):
    status: str
    llm_available: bool
    rag_available: bool
    mcp_available: bool


@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "message": "Pravi AI Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check health of all services"""
    llm_status = await llm_service.check_health()
    rag_status = rag_service.check_health()
    mcp_status = await mcp_service.check_health()

    return HealthResponse(
        status="healthy" if all([llm_status, rag_status]) else "degraded",
        llm_available=llm_status,
        rag_available=rag_status,
        mcp_available=mcp_status
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint
    - Retrieves relevant context from RAG if enabled
    - Optionally uses MCP tools
    - Generates response using local LLM
    """
    try:
        sources = []
        mcp_tools_used = []
        context = ""

        # Get relevant context from RAG
        if request.use_rag:
            rag_results = rag_service.search(request.message, top_k=3)
            if rag_results:
                context = "\n".join([r["content"] for r in rag_results])
                sources = [r.get("source", "Unknown") for r in rag_results]

        # Check if MCP tools can help
        if request.use_mcp:
            mcp_context = await mcp_service.process_query(request.message)
            if mcp_context:
                context += f"\n\nMCP Tools Information:\n{mcp_context['content']}"
                mcp_tools_used = mcp_context.get('tools_used', [])

        # Generate response using LLM
        response = await llm_service.generate(
            prompt=request.message,
            context=context
        )

        return ChatResponse(
            response=response,
            sources=sources if sources else None,
            mcp_tools_used=mcp_tools_used if mcp_tools_used else None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents")
async def add_document(request: DocumentRequest):
    """Add a document to the RAG knowledge base"""
    try:
        doc_id = rag_service.add_document(
            content=request.content,
            metadata=request.metadata or {}
        )
        return {"message": "Document added successfully", "id": doc_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
async def list_documents():
    """List all documents in the knowledge base"""
    try:
        documents = rag_service.list_documents()
        return {"documents": documents}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mcp/tools")
async def list_mcp_tools():
    """List available MCP tools"""
    try:
        tools = await mcp_service.list_tools()
        return {"tools": tools}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models")
async def list_models():
    """List available local models"""
    try:
        models = await llm_service.list_models()
        return {"models": models}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
