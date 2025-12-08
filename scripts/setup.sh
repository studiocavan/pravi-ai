#!/bin/bash

# Pravi AI - Automated Setup Script
# This script automates the installation and setup of Pravi AI

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║                    PRAVI AI SETUP                          ║"
    echo "║            Automated Installation Script                   ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ Error: $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ Warning: $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_error "$1 is not installed"
        return 1
    fi
}

# Main installation
print_header

echo ""
print_info "Checking system requirements..."
echo ""

# Check Python
if check_command python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_info "Python version: $PYTHON_VERSION"
else
    print_error "Python 3.8+ is required"
    echo "Install Python: https://www.python.org/downloads/"
    exit 1
fi

# Check pip
check_command pip3 || {
    print_error "pip3 is required"
    exit 1
}

# Check git (optional)
check_command git || print_warning "git not found (optional)"

# Check Node.js (for MCP)
if check_command node; then
    NODE_VERSION=$(node --version)
    print_info "Node.js version: $NODE_VERSION"
else
    print_warning "Node.js not found (needed for MCP servers)"
fi

# Check npm
check_command npm || print_warning "npm not found (needed for MCP servers)"

# Check Ollama
if check_command ollama; then
    print_success "Ollama is installed"
else
    print_warning "Ollama not found - required for local LLM"
    echo ""
    read -p "Would you like to install Ollama now? [y/N]: " install_ollama

    if [[ $install_ollama =~ ^[Yy]$ ]]; then
        print_info "Installing Ollama..."

        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            curl -fsSL https://ollama.com/install.sh | sh
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install ollama
        else
            print_error "Please install Ollama manually from https://ollama.com"
            exit 1
        fi

        print_success "Ollama installed"
    else
        print_warning "Skipping Ollama installation"
    fi
fi

echo ""
print_info "Setting up Python virtual environment..."
echo ""

cd "$PROJECT_ROOT"

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install backend dependencies
print_info "Installing backend dependencies..."
cd backend
pip install -r requirements.txt
print_success "Backend dependencies installed"

cd ..

# Ask about model installation
echo ""
print_info "Ollama Model Setup"
echo ""

if command -v ollama &> /dev/null; then
    echo "Available model options:"
    echo "  1) Phi-3 Mini (4GB VRAM) - Fastest"
    echo "  2) Mistral 7B (5GB VRAM) - Balanced (Recommended)"
    echo "  3) Llama 3.1 8B (8GB VRAM) - High Quality"
    echo "  4) Skip model installation"
    echo ""
    read -p "Select model to download [1-4]: " model_choice

    case $model_choice in
        1)
            MODEL="phi3:mini"
            ;;
        2)
            MODEL="mistral:7b"
            ;;
        3)
            MODEL="llama3.1:8b"
            ;;
        4)
            print_info "Skipping model installation"
            MODEL=""
            ;;
        *)
            print_warning "Invalid choice, using Mistral 7B"
            MODEL="mistral:7b"
            ;;
    esac

    if [ -n "$MODEL" ]; then
        print_info "Downloading $MODEL..."
        ollama pull "$MODEL"
        print_success "Model downloaded"
    fi
else
    print_warning "Ollama not available, skipping model installation"
fi

# Ask about MCP server
echo ""
print_info "MCP Server Setup (Optional)"
echo ""

if command -v npm &> /dev/null; then
    read -p "Install MCP filesystem server? [y/N]: " install_mcp

    if [[ $install_mcp =~ ^[Yy]$ ]]; then
        print_info "Installing MCP filesystem server..."
        npm install -g @modelcontextprotocol/server-filesystem
        print_success "MCP server installed"
    fi
else
    print_warning "npm not available, skipping MCP installation"
fi

# Create .env file
echo ""
print_info "Creating configuration files..."
echo ""

if [ ! -f "backend/.env" ]; then
    cat > backend/.env << EOF
# Pravi AI Configuration

# Multi-GPU Configuration (set to true if you have 2+ GPUs)
ENABLE_MULTI_GPU=false
MULTI_GPU_CONFIG=balanced

# API Keys (optional, for cloud LLM APIs)
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
EOF
    print_success "Created backend/.env"
else
    print_info "backend/.env already exists"
fi

# Create data directories
mkdir -p data/documents
print_success "Created data directories"

# Setup complete
echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║              SETUP COMPLETED SUCCESSFULLY!                 ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

print_info "Next steps:"
echo ""
echo "1. Start Ollama (in a new terminal):"
echo -e "   ${BLUE}ollama serve${NC}"
echo ""

echo "2. Start the backend (this terminal):"
echo -e "   ${BLUE}cd $PROJECT_ROOT/backend${NC}"
echo -e "   ${BLUE}source ../venv/bin/activate${NC}"
echo -e "   ${BLUE}python main.py${NC}"
echo ""

echo "3. Open the frontend:"
echo -e "   ${BLUE}Open frontend/index.html in your browser${NC}"
echo "   Or run: ${BLUE}cd frontend && python -m http.server 3000${NC}"
echo ""

print_info "Optional: Multi-GPU Setup"
echo "  If you have 2+ GPUs, see: ${BLUE}MULTI_GPU_SETUP.md${NC}"
echo ""

print_info "Documentation:"
echo "  - Quick Start: ${BLUE}README.md${NC}"
echo "  - Detailed Setup: ${BLUE}SETUP_GUIDE.md${NC}"
echo "  - Multi-GPU: ${BLUE}MULTI_GPU_SETUP.md${NC}"
echo ""

# Ask if user wants to start now
echo ""
read -p "Would you like to start the backend now? [y/N]: " start_now

if [[ $start_now =~ ^[Yy]$ ]]; then
    print_info "Starting Ollama..."

    # Check if Ollama is already running
    if pgrep -x "ollama" > /dev/null; then
        print_info "Ollama is already running"
    else
        # Start Ollama in background
        nohup ollama serve > logs/ollama.log 2>&1 &
        sleep 2
        print_success "Ollama started"
    fi

    print_info "Starting backend server..."
    cd backend
    source ../venv/bin/activate
    python main.py
else
    print_info "Setup complete! Follow the steps above to start the application."
fi
