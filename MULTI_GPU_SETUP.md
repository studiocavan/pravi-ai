## Multi-GPU Setup Guide

This guide explains how to leverage 2+ GPUs to run different models simultaneously for improved performance and specialized task handling.

## Benefits of Multi-GPU Setup

1. **Parallel Processing**: Handle multiple requests simultaneously
2. **Specialized Models**: Use optimized models for specific tasks (coding, reasoning, etc.)
3. **Load Balancing**: Distribute workload across GPUs
4. **Increased Throughput**: Process more queries per second
5. **Model Comparison**: Test responses from different models side-by-side

## Prerequisites

- 2 or more NVIDIA GPUs
- CUDA drivers installed
- Ollama installed
- Python 3.8+
- At least 8GB VRAM total across GPUs

## Architecture

```
User Request
     │
     ↓
┌────────────────┐
│  Load Balancer │  (Multi-GPU Service)
│   / Router     │
└────┬──────┬────┘
     │      │
     ↓      ↓
┌─────────┐ ┌─────────┐
│  GPU 0  │ │  GPU 1  │
│ Model A │ │ Model B │
│ Port    │ │ Port    │
│ 11434   │ │ 11435   │
└─────────┘ └─────────┘
```

## Step 1: Verify GPU Setup

Check that both GPUs are visible:

```bash
nvidia-smi
```

You should see both GPUs listed. Note their IDs (usually 0 and 1).

## Step 2: Set Up Ollama on Multiple GPUs

Ollama needs to run separate instances for each GPU.

### Terminal 1 - GPU 0 (Default)
```bash
CUDA_VISIBLE_DEVICES=0 ollama serve
```

This runs on default port 11434.

### Terminal 2 - GPU 1
```bash
CUDA_VISIBLE_DEVICES=1 OLLAMA_HOST=0.0.0.0:11435 ollama serve
```

This runs on port 11435.

**Keep both terminals running.**

## Step 3: Download Models

Download models for each GPU based on your use case.

### Configuration 1: Balanced (Recommended)

**GPU 0 - General Purpose:**
```bash
OLLAMA_HOST=localhost:11434 ollama pull mistral:7b
```

**GPU 1 - Code Specialist:**
```bash
OLLAMA_HOST=localhost:11435 ollama pull codellama:7b
```

### Configuration 2: Speed vs Quality

**GPU 0 - Fast Model:**
```bash
OLLAMA_HOST=localhost:11434 ollama pull phi3:mini
```

**GPU 1 - Quality Model:**
```bash
OLLAMA_HOST=localhost:11435 ollama pull llama3.1:8b
```

### Configuration 3: Dual Power (Same Model)

**Both GPUs - Same Model for Load Balancing:**
```bash
OLLAMA_HOST=localhost:11434 ollama pull llama3.1:8b
OLLAMA_HOST=localhost:11435 ollama pull llama3.1:8b
```

## Step 4: Configure Backend

Create a `.env` file in the `backend/` directory:

```env
ENABLE_MULTI_GPU=true
MULTI_GPU_CONFIG=balanced
```

Available configs:
- `balanced` - General + Coding models
- `speed_quality` - Fast + High-quality models
- `specialized` - General + Creative models
- `dual_power` - Same model on both GPUs

Or customize in `backend/multi_gpu_service.py`.

## Step 5: Start the Backend

```bash
cd backend
source venv/bin/activate
python main.py
```

The backend will automatically detect and use multi-GPU configuration.

## Step 6: Verify Setup

Check GPU status via API:

```bash
curl http://localhost:8000/gpu/status
```

You should see both models listed with their GPU assignments.

## Using Multi-GPU Features

### 1. Regular Chat (Auto-Routing)

The system automatically selects the best model:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain machine learning"}'
```

### 2. Specify Model

Choose a specific GPU/model:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Write a Python function",
    "model_name": "codellama:7b"
  }'
```

### 3. Specify Purpose

Route by task type:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Fix this code bug",
    "purpose": "coding"
  }'
```

Available purposes: `general`, `coding`, `reasoning`, `fast`, `creative`

### 4. Compare Models

Get responses from all models:

```bash
curl -X POST http://localhost:8000/gpu/compare \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain recursion"
  }'
```

### 5. Parallel Processing

Process multiple queries simultaneously:

```bash
curl -X POST http://localhost:8000/gpu/parallel \
  -H "Content-Type: application/json" \
  -d '{
    "prompts": [
      "What is AI?",
      "What is ML?",
      "What is DL?"
    ]
  }'
```

## Frontend Integration

The frontend automatically detects multi-GPU mode. When enabled, you'll see:

- Model selector dropdown
- GPU status indicators
- Model used in response metadata

## Performance Optimization

### Optimal Model Pairings

| GPU 0 (4-6GB) | GPU 1 (8-10GB) | Use Case |
|---------------|----------------|----------|
| phi3:mini | llama3.1:8b | Speed + Quality |
| mistral:7b | codellama:7b | General + Coding |
| llama2:7b | mixtral:8x7b | Standard + Advanced |

### Memory Management

Monitor GPU memory:

```bash
watch -n 1 nvidia-smi
```

If a model doesn't fit:
- Use smaller variants (e.g., `llama3.1:7b` instead of `llama3.1:8b`)
- Reduce concurrent requests
- Use quantized models

### Load Balancing Strategies

1. **Purpose-Based**: Route by task type (coding, general, etc.)
2. **Round-Robin**: Distribute evenly across GPUs
3. **Weighted**: More requests to faster/better model
4. **Adaptive**: Monitor GPU utilization and route to less busy GPU

## Troubleshooting

### Problem: Second GPU not detected

**Solution:**
```bash
# Check if both GPUs are visible
nvidia-smi

# Ensure CUDA_VISIBLE_DEVICES is set correctly
echo $CUDA_VISIBLE_DEVICES
```

### Problem: Port already in use

**Solution:**
```bash
# Check what's using the port
lsof -i :11435

# Kill the process or use different port
OLLAMA_HOST=0.0.0.0:11436 ollama serve
```

### Problem: Model loading fails

**Solution:**
- Ensure model is pulled for correct port:
  ```bash
  OLLAMA_HOST=localhost:11435 ollama list
  OLLAMA_HOST=localhost:11435 ollama pull mistral:7b
  ```

### Problem: Out of memory

**Solution:**
- Use smaller models
- Check memory usage: `nvidia-smi`
- Reduce `num_ctx` (context length) in Ollama config
- Use one model per GPU (not multiple)

### Problem: Slow responses

**Solution:**
- Check GPU utilization with `nvidia-smi`
- Ensure models are on GPU, not CPU
- Reduce concurrent requests
- Use faster models (phi3:mini)

## Advanced Configuration

### Custom Model Assignment

Edit `backend/multi_gpu_service.py`:

```python
service = MultiGPUService()

service.register_model(
    model_name="your-model:tag",
    gpu_id=0,  # GPU ID
    purpose=ModelPurpose.GENERAL,
    vram_usage="~XGB",
    description="Your description"
)
```

### Dynamic GPU Selection

Implement custom routing logic in `multi_gpu_service.py`:

```python
async def smart_generate(self, prompt: str):
    # Analyze prompt
    if "code" in prompt.lower():
        model = self.get_model_by_purpose(ModelPurpose.CODING)
    else:
        model = self.get_model_by_purpose(ModelPurpose.GENERAL)

    return await self.generate(prompt=prompt, model_name=model.name)
```

### GPU Monitoring

Add monitoring to track GPU metrics:

```python
import pynvml

pynvml.nvmlInit()
handle = pynvml.nvmlDeviceGetHandleByIndex(0)
info = pynvml.nvmlDeviceGetMemoryInfo(handle)
print(f"GPU 0 Memory: {info.used / 1024**3:.2f} GB")
```

## Use Case Examples

### 1. Development Team Setup

- **GPU 0**: `codellama:7b` - For code review and generation
- **GPU 1**: `llama3.1:8b` - For documentation and chat

### 2. Content Creation

- **GPU 0**: `mistral:7b` - For quick drafts and editing
- **GPU 1**: `mixtral:8x7b` - For high-quality creative writing

### 3. Research Lab

- **GPU 0**: `phi3:mini` - For quick literature searches
- **GPU 1**: `llama3.1:8b` - For paper analysis and synthesis

### 4. Customer Support

- **GPU 0**: `mistral:7b` - For simple FAQ responses
- **GPU 1**: `llama3.1:8b` - For complex technical issues

## Performance Benchmarks

Typical improvements with dual GPU setup:

| Metric | Single GPU | Dual GPU | Improvement |
|--------|-----------|----------|-------------|
| Throughput | 10 req/min | 18-20 req/min | +80-100% |
| Latency (simple) | 2-3s | 1.5-2s | +33% |
| Latency (complex) | 5-8s | 3-5s | +40% |
| Concurrent requests | 1-2 | 4-6 | +200% |

*Results vary based on models and hardware*

## Cost-Benefit Analysis

**Hardware Cost**: 2x GPUs (~$1000-2000)

**Benefits**:
- 2x throughput capacity
- Zero API costs (vs $20-100/month for cloud LLM APIs)
- Complete privacy
- No rate limits
- Specialized model optimization

**Breaks even in**: 1-2 years vs cloud APIs for moderate usage

## Scaling Beyond 2 GPUs

The system supports 3+ GPUs:

```bash
# GPU 0
CUDA_VISIBLE_DEVICES=0 OLLAMA_HOST=:11434 ollama serve

# GPU 1
CUDA_VISIBLE_DEVICES=1 OLLAMA_HOST=:11435 ollama serve

# GPU 2
CUDA_VISIBLE_DEVICES=2 OLLAMA_HOST=:11436 ollama serve
```

Update `multi_gpu_service.py` GPU port mapping:

```python
self.gpu_ports = {
    0: 11434,
    1: 11435,
    2: 11436,
    # Add more as needed
}
```

## Best Practices

1. **Start Simple**: Begin with 2 GPUs and same model
2. **Monitor Usage**: Track which models are used most
3. **Specialize Gradually**: Move to specialized models based on patterns
4. **Update Regularly**: Pull model updates periodically
5. **Test Configurations**: Try different setups to find optimal balance
6. **Document Setup**: Keep notes on model assignments and purposes

## Resources

- [Ollama Documentation](https://ollama.com)
- [CUDA Multi-GPU Guide](https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#multi-device-system)
- [NVIDIA Multi-GPU Best Practices](https://developer.nvidia.com/blog/cuda-pro-tip-write-flexible-kernels-grid-stride-loops/)

## Support

For issues:
1. Check both Ollama servers are running
2. Verify GPU visibility with `nvidia-smi`
3. Test each model individually
4. Check backend logs for errors
5. Review API documentation at `http://localhost:8000/docs`
