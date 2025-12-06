"""
LLM Service - Local model hosting using Ollama
Supports models that use 4-12GB GPU memory
"""

import httpx
from typing import Optional, List, Dict
import asyncio


class LLMService:
    """Service for interacting with local LLM via Ollama"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.default_model = "llama3.1:8b"  # ~8GB GPU memory
        # Other good options:
        # - mistral:7b (~4GB)
        # - phi3:mini (~4GB)
        # - llama2:7b (~4GB)
        # - gemma2:9b (~9GB)

    async def check_health(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> List[Dict]:
        """List all available models in Ollama"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    return data.get("models", [])
                return []
        except Exception as e:
            print(f"Error listing models: {e}")
            return []

    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate a response using the local LLM

        Args:
            prompt: User's question/prompt
            context: Additional context (from RAG or MCP)
            model: Model name (defaults to self.default_model)
            temperature: Sampling temperature (0.0 - 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response
        """
        model = model or self.default_model

        # Build the full prompt with context
        full_prompt = self._build_prompt(prompt, context)

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": full_prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens,
                        }
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "")
                else:
                    return f"Error: Unable to generate response (status {response.status_code})"

        except httpx.TimeoutException:
            return "Error: Request timed out. The model might be loading."
        except Exception as e:
            return f"Error generating response: {str(e)}"

    async def generate_stream(
        self,
        prompt: str,
        context: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        Generate a streaming response (for future use with WebSocket)

        Yields:
            Chunks of generated text
        """
        model = model or self.default_model
        full_prompt = self._build_prompt(prompt, context)

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": full_prompt,
                    "stream": True,
                    "options": {"temperature": temperature}
                }
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]

    def _build_prompt(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Build the final prompt with context

        Args:
            prompt: User's question
            context: Retrieved context from RAG/MCP

        Returns:
            Formatted prompt
        """
        if context:
            return f"""You are a helpful AI assistant. Use the following context to answer the user's question accurately.

Context:
{context}

User Question: {prompt}

Answer (be concise and helpful):"""
        else:
            return f"""You are a helpful AI assistant. Answer the user's question concisely and accurately.

User Question: {prompt}

Answer:"""

    async def pull_model(self, model_name: str):
        """
        Pull/download a model from Ollama registry

        Args:
            model_name: Name of the model to download (e.g., "llama3.1:8b")
        """
        try:
            async with httpx.AsyncClient(timeout=600.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/pull",
                    json={"name": model_name, "stream": False}
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Error pulling model: {e}")
            return False


# Recommended models for 4-12GB GPU memory:
RECOMMENDED_MODELS = {
    "llama3.1:8b": {
        "size": "8GB",
        "description": "Meta's Llama 3.1 8B - Great general purpose model",
        "vram": "~8GB"
    },
    "mistral:7b": {
        "size": "7GB",
        "description": "Mistral 7B - Excellent reasoning and coding",
        "vram": "~4-5GB"
    },
    "phi3:mini": {
        "size": "4GB",
        "description": "Microsoft Phi-3 Mini - Fast and efficient",
        "vram": "~4GB"
    },
    "gemma2:9b": {
        "size": "9GB",
        "description": "Google Gemma 2 9B - Strong performance",
        "vram": "~9GB"
    },
    "llama2:7b": {
        "size": "7GB",
        "description": "Meta's Llama 2 7B - Reliable classic",
        "vram": "~4-5GB"
    }
}
