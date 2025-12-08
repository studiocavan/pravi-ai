"""
Multi-GPU Example - Leveraging Multiple GPUs for Different Models

This example demonstrates how to:
1. Set up multiple models on different GPUs
2. Use specialized models for specific tasks
3. Process requests in parallel across GPUs
4. Compare responses from different models
"""

import asyncio
import sys
import os

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from multi_gpu_service import MultiGPUService, ModelPurpose, DUAL_GPU_CONFIGS


async def basic_multi_gpu_example():
    """Basic example: Setting up and using multiple models"""
    print("="*70)
    print("EXAMPLE 1: Basic Multi-GPU Setup")
    print("="*70)

    # Create multi-GPU service
    service = MultiGPUService()

    # Register models on different GPUs
    # GPU 0: Fast model for quick queries
    service.register_model(
        model_name="phi3:mini",
        gpu_id=0,
        purpose=ModelPurpose.FAST,
        vram_usage="~4GB",
        description="Fast model for quick responses"
    )

    # GPU 1: Larger model for complex tasks
    service.register_model(
        model_name="llama3.1:8b",
        gpu_id=1,
        purpose=ModelPurpose.REASONING,
        vram_usage="~8GB",
        description="High-quality model for reasoning"
    )

    # List registered models
    print("\nRegistered Models:")
    for model in service.list_models():
        print(f"  - {model['name']}")
        print(f"    GPU: {model['gpu_id']}")
        print(f"    Purpose: {model['purpose']}")
        print(f"    VRAM: {model['vram_usage']}")
        print()

    # Check health
    print("Checking model health...")
    health = await service.check_health()
    for model_name, is_healthy in health.items():
        status = "✓ Online" if is_healthy else "✗ Offline"
        print(f"  {model_name}: {status}")

    print()


async def purpose_based_routing():
    """Example: Route queries to appropriate models based on purpose"""
    print("="*70)
    print("EXAMPLE 2: Purpose-Based Routing")
    print("="*70)

    service = MultiGPUService()

    # Setup: Balanced configuration
    service.register_model("mistral:7b", 0, ModelPurpose.GENERAL, "~5GB", "General purpose")
    service.register_model("codellama:7b", 1, ModelPurpose.CODING, "~5GB", "Code specialist")

    # Simple query - use fast model
    print("\n1. Simple question (using GENERAL model):")
    question = "What is the capital of France?"
    response, model_used = await service.generate(
        prompt=question,
        purpose=ModelPurpose.GENERAL
    )
    print(f"Q: {question}")
    print(f"A: {response[:200]}...")
    print(f"Model: {model_used}")

    # Coding query - use specialized model
    print("\n2. Coding question (using CODING model):")
    question = "Write a Python function to calculate fibonacci numbers"
    response, model_used = await service.generate(
        prompt=question,
        purpose=ModelPurpose.CODING
    )
    print(f"Q: {question}")
    print(f"A: {response[:200]}...")
    print(f"Model: {model_used}")

    print()


async def parallel_processing():
    """Example: Process multiple queries in parallel across GPUs"""
    print("="*70)
    print("EXAMPLE 3: Parallel Processing")
    print("="*70)

    service = MultiGPUService()

    # Setup dual models
    service.register_model("llama3.1:8b", 0, ModelPurpose.GENERAL, "~8GB")
    service.register_model("llama3.1:8b", 1, ModelPurpose.GENERAL, "~8GB")

    # Multiple queries to process
    queries = [
        "Explain quantum computing in one sentence",
        "What is machine learning?",
        "Define artificial intelligence",
        "What is a neural network?",
    ]

    print(f"\nProcessing {len(queries)} queries in parallel...\n")

    import time
    start = time.time()

    # Process all queries in parallel
    results = await service.parallel_generate(prompts=queries)

    elapsed = time.time() - start

    # Display results
    for i, (query, (response, model)) in enumerate(zip(queries, results), 1):
        print(f"{i}. Q: {query}")
        print(f"   A: {response[:150]}...")
        print(f"   Model: {model}")
        print()

    print(f"Total time: {elapsed:.2f}s")
    print(f"Average time per query: {elapsed/len(queries):.2f}s")
    print()


async def model_comparison():
    """Example: Compare responses from different models"""
    print("="*70)
    print("EXAMPLE 4: Model Comparison")
    print("="*70)

    service = MultiGPUService()

    # Setup different models for comparison
    service.register_model("phi3:mini", 0, ModelPurpose.FAST, "~4GB", "Small fast model")
    service.register_model("llama3.1:8b", 1, ModelPurpose.GENERAL, "~8GB", "Larger model")

    question = "Explain the concept of recursion in programming"

    print(f"\nComparing responses for: '{question}'\n")

    # Get responses from all models
    responses = await service.compare_models(prompt=question)

    # Display comparison
    for model_name, (response, _) in responses.items():
        print(f"{'='*70}")
        print(f"Model: {model_name}")
        print(f"{'='*70}")
        print(response[:300])
        print("...\n")


async def load_balanced_workflow():
    """Example: Real-world workflow with load balancing"""
    print("="*70)
    print("EXAMPLE 5: Load-Balanced Workflow")
    print("="*70)

    service = MultiGPUService()

    # Setup: Speed vs Quality
    service.register_model("phi3:mini", 0, ModelPurpose.FAST, "~4GB")
    service.register_model("mixtral:8x7b", 1, ModelPurpose.REASONING, "~11GB")

    print("\nSimulating a workflow with different query types:\n")

    # Quick queries use fast model
    quick_queries = [
        "What's 15 * 23?",
        "Define API",
        "What is REST?",
    ]

    print("Quick queries (using fast model):")
    for query in quick_queries:
        response, model = await service.generate(
            prompt=query,
            purpose=ModelPurpose.FAST
        )
        print(f"  Q: {query}")
        print(f"  A: {response[:80]}...")
        print()

    # Complex queries use powerful model
    complex_queries = [
        "Explain the difference between supervised and unsupervised learning",
        "How does a transformer architecture work?",
    ]

    print("\nComplex queries (using reasoning model):")
    for query in complex_queries:
        response, model = await service.generate(
            prompt=query,
            purpose=ModelPurpose.REASONING
        )
        print(f"  Q: {query}")
        print(f"  A: {response[:150]}...")
        print()


async def predefined_configurations():
    """Example: Using predefined multi-GPU configurations"""
    print("="*70)
    print("EXAMPLE 6: Predefined Configurations")
    print("="*70)

    print("\nAvailable configurations:")
    for config_name, config in DUAL_GPU_CONFIGS.items():
        print(f"\n{config_name.upper()}:")
        for model_config in config:
            print(f"  GPU {model_config['gpu']}: {model_config['model']}")
            print(f"    Purpose: {model_config['purpose'].value}")
            print(f"    Description: {model_config['description']}")

    # Use a predefined configuration
    print("\n" + "="*70)
    print("Loading 'balanced' configuration...")
    print("="*70)

    from multi_gpu_service import create_multi_gpu_service

    service = create_multi_gpu_service(config_name="balanced")

    print("\nLoaded models:")
    for model in service.list_models():
        print(f"  - {model['name']} on GPU {model['gpu_id']}")


async def main():
    """Run all examples"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "MULTI-GPU EXAMPLES FOR PRAVI AI" + " "*22 + "║")
    print("╚" + "="*68 + "╝")
    print()
    print("These examples demonstrate multi-GPU model management")
    print("NOTE: Make sure Ollama is running on multiple ports for different GPUs")
    print()

    try:
        # Run examples
        await basic_multi_gpu_example()
        await asyncio.sleep(1)

        print("\n" + "NOTE: The following examples require models to be running.")
        print("Press Ctrl+C to skip to configuration examples\n")

        try:
            # await purpose_based_routing()
            # await parallel_processing()
            # await model_comparison()
            # await load_balanced_workflow()
            await predefined_configurations()

        except Exception as e:
            print(f"\nNote: Skipping live examples - {e}")
            print("Make sure Ollama servers are running on ports 11434 and 11435")

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")

    print("\n" + "="*70)
    print("Examples completed!")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
