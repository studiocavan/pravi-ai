#!/bin/bash

# Multi-GPU Startup Script for Pravi AI
# This script helps start Ollama on multiple GPUs

set -e

echo "=========================================="
echo "Pravi AI Multi-GPU Setup Script"
echo "=========================================="
echo ""

# Check for CUDA
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ Error: nvidia-smi not found. CUDA drivers may not be installed."
    exit 1
fi

# Check number of GPUs
GPU_COUNT=$(nvidia-smi --list-gpus | wc -l)
echo "✓ Found $GPU_COUNT GPU(s)"

if [ "$GPU_COUNT" -lt 2 ]; then
    echo "⚠️  Warning: Less than 2 GPUs detected. Multi-GPU features require 2+ GPUs."
    echo "   Continuing anyway for testing..."
fi

nvidia-smi --query-gpu=index,name,memory.total --format=csv
echo ""

# Check for Ollama
if ! command -v ollama &> /dev/null; then
    echo "❌ Error: Ollama not found. Please install Ollama first."
    echo "   Visit: https://ollama.com"
    exit 1
fi

echo "✓ Ollama found"
echo ""

# Configuration
GPU0_PORT=11434
GPU1_PORT=11435

echo "Configuration:"
echo "  GPU 0: Port $GPU0_PORT"
echo "  GPU 1: Port $GPU1_PORT"
echo ""

# Get config from user
echo "Select model configuration:"
echo "  1) Balanced (mistral:7b + codellama:7b)"
echo "  2) Speed vs Quality (phi3:mini + llama3.1:8b)"
echo "  3) Dual Power (llama3.1:8b + llama3.1:8b)"
echo "  4) Custom"
read -p "Enter choice [1-4]: " config_choice

case $config_choice in
    1)
        GPU0_MODEL="mistral:7b"
        GPU1_MODEL="codellama:7b"
        CONFIG_NAME="balanced"
        ;;
    2)
        GPU0_MODEL="phi3:mini"
        GPU1_MODEL="llama3.1:8b"
        CONFIG_NAME="speed_quality"
        ;;
    3)
        GPU0_MODEL="llama3.1:8b"
        GPU1_MODEL="llama3.1:8b"
        CONFIG_NAME="dual_power"
        ;;
    4)
        read -p "Enter model for GPU 0: " GPU0_MODEL
        read -p "Enter model for GPU 1: " GPU1_MODEL
        CONFIG_NAME="custom"
        ;;
    *)
        echo "Invalid choice. Using balanced configuration."
        GPU0_MODEL="mistral:7b"
        GPU1_MODEL="codellama:7b"
        CONFIG_NAME="balanced"
        ;;
esac

echo ""
echo "Selected Configuration: $CONFIG_NAME"
echo "  GPU 0: $GPU0_MODEL"
echo "  GPU 1: $GPU1_MODEL"
echo ""

# Check if models are available
echo "Checking models..."

check_model() {
    local host=$1
    local model=$2

    if OLLAMA_HOST=$host ollama list | grep -q "^${model}"; then
        echo "  ✓ $model found on $host"
        return 0
    else
        echo "  ✗ $model not found on $host"
        return 1
    fi
}

NEED_PULL=false

if ! check_model "localhost:$GPU0_PORT" "$GPU0_MODEL"; then
    NEED_PULL=true
fi

if ! check_model "localhost:$GPU1_PORT" "$GPU1_MODEL"; then
    NEED_PULL=true
fi

if [ "$NEED_PULL" = true ]; then
    echo ""
    read -p "Some models are missing. Download them now? [y/N]: " download_choice

    if [[ $download_choice =~ ^[Yy]$ ]]; then
        echo "Downloading models..."

        echo "  Pulling $GPU0_MODEL for GPU 0..."
        OLLAMA_HOST=localhost:$GPU0_PORT ollama pull "$GPU0_MODEL"

        echo "  Pulling $GPU1_MODEL for GPU 1..."
        OLLAMA_HOST=localhost:$GPU1_PORT ollama pull "$GPU1_MODEL"

        echo "✓ Models downloaded"
    else
        echo "⚠️  Warning: Models not downloaded. Make sure to download them manually."
    fi
fi

echo ""
echo "=========================================="
echo "Starting Ollama servers..."
echo "=========================================="
echo ""

# Create log directory
mkdir -p logs

echo "Starting GPU 0 (Port $GPU0_PORT)..."
CUDA_VISIBLE_DEVICES=0 OLLAMA_HOST=0.0.0.0:$GPU0_PORT nohup ollama serve > logs/ollama_gpu0.log 2>&1 &
GPU0_PID=$!
echo "  PID: $GPU0_PID"
sleep 2

echo "Starting GPU 1 (Port $GPU1_PORT)..."
CUDA_VISIBLE_DEVICES=1 OLLAMA_HOST=0.0.0.0:$GPU1_PORT nohup ollama serve > logs/ollama_gpu1.log 2>&1 &
GPU1_PID=$!
echo "  PID: $GPU1_PID"
sleep 2

echo ""
echo "Verifying servers..."

check_server() {
    local port=$1
    if curl -s "http://localhost:$port/api/tags" > /dev/null 2>&1; then
        echo "  ✓ Server on port $port is running"
        return 0
    else
        echo "  ✗ Server on port $port is NOT running"
        return 1
    fi
}

check_server $GPU0_PORT
check_server $GPU1_PORT

echo ""
echo "=========================================="
echo "Multi-GPU Setup Complete!"
echo "=========================================="
echo ""
echo "Ollama servers running:"
echo "  GPU 0: localhost:$GPU0_PORT (PID: $GPU0_PID) - $GPU0_MODEL"
echo "  GPU 1: localhost:$GPU1_PORT (PID: $GPU1_PID) - $GPU1_MODEL"
echo ""
echo "Logs:"
echo "  GPU 0: logs/ollama_gpu0.log"
echo "  GPU 1: logs/ollama_gpu1.log"
echo ""
echo "Next steps:"
echo "1. Create backend/.env file with:"
echo "   ENABLE_MULTI_GPU=true"
echo "   MULTI_GPU_CONFIG=$CONFIG_NAME"
echo ""
echo "2. Start the backend:"
echo "   cd backend && python main.py"
echo ""
echo "3. Open frontend and enjoy multi-GPU performance!"
echo ""
echo "To stop servers:"
echo "  kill $GPU0_PID $GPU1_PID"
echo ""
echo "To monitor GPU usage:"
echo "  watch -n 1 nvidia-smi"
echo ""
