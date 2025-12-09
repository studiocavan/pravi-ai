"""
Backend API for AI Chat Application
Features: Local LLM (Ollama), RAG (ChromaDB), MCP Integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import logging

from rag_service import RAGService
from llm_service import LLMService
from mcp_service import MCPService
from multi_gpu_service import MultiGPUService, ModelPurpose
import os

# Configure logging
handlers = [logging.StreamHandler()]
# Try to add file handler if logs directory exists
if os.path.exists('logs') or os.path.exists('../logs'):
    log_path = 'logs/backend.log' if os.path.exists('logs') else '../logs/backend.log'
    try:
        handlers.append(logging.FileHandler(log_path, mode='a'))
    except Exception:
        pass  # Fallback to console-only logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)

logger = logging.getLogger(__name__)

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

# Multi-GPU service (optional, enabled via environment variable)
multi_gpu_enabled = os.getenv("ENABLE_MULTI_GPU", "false").lower() == "true"
multi_gpu_service = None

if multi_gpu_enabled:
    from multi_gpu_service import create_multi_gpu_service
    multi_gpu_service = create_multi_gpu_service(
        config_name=os.getenv("MULTI_GPU_CONFIG", "balanced")
    )


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    use_rag: bool = True
    use_mcp: bool = False
    model_name: Optional[str] = None  # For multi-GPU model selection
    purpose: Optional[str] = None  # For selecting by purpose


class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = None
    mcp_tools_used: Optional[List[str]] = None
    model_used: Optional[str] = None  # Which model generated the response


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
    - Generates response using local LLM or multi-GPU model
    """
    try:
        sources = []
        mcp_tools_used = []
        context = ""
        model_used = None

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

        # Generate response using multi-GPU if enabled, otherwise use single LLM
        if multi_gpu_enabled and multi_gpu_service:
            # Convert purpose string to enum if provided
            purpose_enum = None
            if request.purpose:
                try:
                    purpose_enum = ModelPurpose(request.purpose)
                except ValueError:
                    pass

            response, model_used = await multi_gpu_service.generate(
                prompt=request.message,
                context=context,
                model_name=request.model_name,
                purpose=purpose_enum
            )
        else:
            response = await llm_service.generate(
                prompt=request.message,
                context=context,
                model=request.model_name
            )
            model_used = request.model_name or llm_service.default_model

        return ChatResponse(
            response=response,
            sources=sources if sources else None,
            mcp_tools_used=mcp_tools_used if mcp_tools_used else None,
            model_used=model_used
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
        if multi_gpu_enabled and multi_gpu_service:
            gpu_models = multi_gpu_service.list_models()
            return {
                "multi_gpu_enabled": True,
                "models": gpu_models
            }
        else:
            models = await llm_service.list_models()
            return {
                "multi_gpu_enabled": False,
                "models": models
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Multi-GPU specific endpoints
@app.get("/gpu/status")
async def gpu_status():
    """Get status of all GPUs and their models"""
    if not multi_gpu_enabled or not multi_gpu_service:
        return {
            "enabled": False,
            "message": "Multi-GPU mode not enabled"
        }

    try:
        health = await multi_gpu_service.check_health()
        models = multi_gpu_service.list_models()

        return {
            "enabled": True,
            "models": models,
            "health": health
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CompareRequest(BaseModel):
    prompt: str
    context: Optional[str] = None


@app.post("/gpu/compare")
async def compare_models(request: CompareRequest):
    """Compare responses from all GPU models"""
    if not multi_gpu_enabled or not multi_gpu_service:
        raise HTTPException(
            status_code=400,
            detail="Multi-GPU mode not enabled"
        )

    try:
        results = await multi_gpu_service.compare_models(
            prompt=request.prompt,
            context=request.context
        )

        return {
            "prompt": request.prompt,
            "responses": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ParallelRequest(BaseModel):
    prompts: List[str]
    contexts: Optional[List[str]] = None


@app.post("/gpu/parallel")
async def parallel_generate(request: ParallelRequest):
    """Generate responses in parallel across GPUs"""
    if not multi_gpu_enabled or not multi_gpu_service:
        raise HTTPException(
            status_code=400,
            detail="Multi-GPU mode not enabled"
        )

    try:
        results = await multi_gpu_service.parallel_generate(
            prompts=request.prompts,
            contexts=request.contexts
        )

        return {
            "results": [
                {
                    "response": response,
                    "model": model_name
                }
                for response, model_name in results
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
