"""
Multi-GPU Service - Manage multiple models across different GPUs
Enables parallel processing and specialized model assignments
"""

import httpx
from typing import Optional, List, Dict, Tuple
import asyncio
from dataclasses import dataclass
from enum import Enum


class ModelPurpose(Enum):
    """Model specialization purposes"""
    GENERAL = "general"
    CODING = "coding"
    REASONING = "reasoning"
    FAST = "fast"
    CREATIVE = "creative"


@dataclass
class GPUModel:
    """Configuration for a model on a specific GPU"""
    name: str
    gpu_id: int
    purpose: ModelPurpose
    base_url: str
    vram_usage: str
    description: str


class MultiGPUService:
    """
    Service for managing multiple models across different GPUs

    This allows:
    - Running different models on different GPUs simultaneously
    - Load balancing across GPUs
    - Specialized models for specific tasks
    - Parallel request processing
    """

    def __init__(self, base_url: str = "http://localhost"):
        self.base_url = base_url
        self.models: Dict[str, GPUModel] = {}
        self.gpu_ports = {
            0: 11434,  # Default Ollama port for GPU 0
            1: 11435,  # Port for GPU 1
        }

    def register_model(
        self,
        model_name: str,
        gpu_id: int,
        purpose: ModelPurpose = ModelPurpose.GENERAL,
        vram_usage: str = "Unknown",
        description: str = ""
    ):
        """
        Register a model running on a specific GPU

        Args:
            model_name: Ollama model name (e.g., "mistral:7b")
            gpu_id: GPU device ID (0, 1, etc.)
            purpose: What this model is optimized for
            vram_usage: Memory usage info
            description: Model description
        """
        port = self.gpu_ports.get(gpu_id, 11434)
        model_url = f"{self.base_url}:{port}"

        gpu_model = GPUModel(
            name=model_name,
            gpu_id=gpu_id,
            purpose=purpose,
            base_url=model_url,
            vram_usage=vram_usage,
            description=description
        )

        self.models[model_name] = gpu_model
        print(f"Registered {model_name} on GPU {gpu_id} at {model_url}")

    def get_model_by_purpose(self, purpose: ModelPurpose) -> Optional[GPUModel]:
        """Get a model by its purpose"""
        for model in self.models.values():
            if model.purpose == purpose:
                return model
        return None

    def get_model(self, model_name: str) -> Optional[GPUModel]:
        """Get a specific model by name"""
        return self.models.get(model_name)

    def list_models(self) -> List[Dict]:
        """List all registered models with their GPU assignments"""
        return [
            {
                "name": model.name,
                "gpu_id": model.gpu_id,
                "purpose": model.purpose.value,
                "vram_usage": model.vram_usage,
                "description": model.description,
                "url": model.base_url
            }
            for model in self.models.values()
        ]

    async def check_health(self) -> Dict[str, bool]:
        """Check health of all registered models"""
        health_status = {}

        for model_name, model in self.models.items():
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{model.base_url}/api/tags")
                    health_status[model_name] = response.status_code == 200
            except Exception:
                health_status[model_name] = False

        return health_status

    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        model_name: Optional[str] = None,
        purpose: Optional[ModelPurpose] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Tuple[str, str]:
        """
        Generate response using a specific model or purpose

        Args:
            prompt: User's question
            context: Additional context
            model_name: Specific model to use
            purpose: Select model by purpose if model_name not specified
            temperature: Sampling temperature
            max_tokens: Max tokens to generate

        Returns:
            Tuple of (response text, model name used)
        """
        # Select model
        if model_name:
            gpu_model = self.get_model(model_name)
        elif purpose:
            gpu_model = self.get_model_by_purpose(purpose)
        else:
            # Default to first available model
            gpu_model = list(self.models.values())[0] if self.models else None

        if not gpu_model:
            return "Error: No model available", "none"

        # Build prompt
        full_prompt = self._build_prompt(prompt, context)

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{gpu_model.base_url}/api/generate",
                    json={
                        "model": gpu_model.name,
                        "prompt": full_prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens,
                            "num_gpu": 1,  # Use only the assigned GPU
                        }
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", ""), gpu_model.name
                else:
                    return f"Error: Status {response.status_code}", gpu_model.name

        except Exception as e:
            return f"Error: {str(e)}", gpu_model.name

    async def parallel_generate(
        self,
        prompts: List[str],
        contexts: Optional[List[str]] = None
    ) -> List[Tuple[str, str]]:
        """
        Generate responses in parallel using all available GPUs

        Args:
            prompts: List of prompts to process
            contexts: Optional list of contexts (same length as prompts)

        Returns:
            List of (response, model_name) tuples
        """
        if contexts is None:
            contexts = [None] * len(prompts)

        # Distribute prompts across available models
        models = list(self.models.values())
        if not models:
            return [("Error: No models available", "none")] * len(prompts)

        tasks = []
        for i, (prompt, context) in enumerate(zip(prompts, contexts)):
            # Round-robin model selection
            model = models[i % len(models)]
            task = self.generate(
                prompt=prompt,
                context=context,
                model_name=model.name
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        return results

    async def compare_models(
        self,
        prompt: str,
        context: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate responses from all models for comparison

        Args:
            prompt: The prompt to send to all models
            context: Optional context

        Returns:
            Dict mapping model names to their responses
        """
        tasks = {}
        for model_name in self.models.keys():
            tasks[model_name] = self.generate(
                prompt=prompt,
                context=context,
                model_name=model_name
            )

        results = await asyncio.gather(*tasks.values())

        return {
            model_name: response
            for model_name, (response, _) in zip(tasks.keys(), results)
        }

    def _build_prompt(self, prompt: str, context: Optional[str] = None) -> str:
        """Build the final prompt with context"""
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


# Predefined multi-GPU configurations
DUAL_GPU_CONFIGS = {
    "balanced": [
        {
            "model": "mistral:7b",
            "gpu": 0,
            "purpose": ModelPurpose.GENERAL,
            "vram": "~5GB",
            "description": "General purpose model for chat"
        },
        {
            "model": "codellama:7b",
            "gpu": 1,
            "purpose": ModelPurpose.CODING,
            "vram": "~5GB",
            "description": "Specialized for code generation"
        }
    ],
    "speed_quality": [
        {
            "model": "phi3:mini",
            "gpu": 0,
            "purpose": ModelPurpose.FAST,
            "vram": "~4GB",
            "description": "Fast responses for quick queries"
        },
        {
            "model": "llama3.1:8b",
            "gpu": 1,
            "purpose": ModelPurpose.REASONING,
            "vram": "~8GB",
            "description": "High quality for complex reasoning"
        }
    ],
    "specialized": [
        {
            "model": "llama3.1:8b",
            "gpu": 0,
            "purpose": ModelPurpose.GENERAL,
            "vram": "~8GB",
            "description": "General chat and Q&A"
        },
        {
            "model": "mixtral:8x7b",
            "gpu": 1,
            "purpose": ModelPurpose.CREATIVE,
            "vram": "~11GB",
            "description": "Creative writing and complex tasks"
        }
    ],
    "dual_power": [
        {
            "model": "llama3.1:8b",
            "gpu": 0,
            "purpose": ModelPurpose.GENERAL,
            "vram": "~8GB",
            "description": "Primary model for most tasks"
        },
        {
            "model": "llama3.1:8b",
            "gpu": 1,
            "purpose": ModelPurpose.GENERAL,
            "vram": "~8GB",
            "description": "Secondary model for parallel processing"
        }
    ]
}


def create_multi_gpu_service(config_name: str = "balanced") -> MultiGPUService:
    """
    Create a pre-configured multi-GPU service

    Args:
        config_name: Name of predefined config (balanced, speed_quality, specialized, dual_power)

    Returns:
        Configured MultiGPUService instance
    """
    service = MultiGPUService()

    config = DUAL_GPU_CONFIGS.get(config_name, DUAL_GPU_CONFIGS["balanced"])

    for model_config in config:
        service.register_model(
            model_name=model_config["model"],
            gpu_id=model_config["gpu"],
            purpose=model_config["purpose"],
            vram_usage=model_config["vram"],
            description=model_config["description"]
        )

    return service
