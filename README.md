# Pravi AI - Python AI & LLM Development Examples

A comprehensive collection of examples for AI development, LLM interaction, and MCP (Model Context Protocol) server integration using Python.

## Overview

This repository provides practical examples and starter code for:
- **AI Development**: Machine learning basics, model training, and inference
- **LLM Integration**: Working with popular LLM APIs (OpenAI, Anthropic Claude, etc.)
- **MCP Servers**: Interacting with Model Context Protocol servers

## Repository Structure

```
pravi-ai/
├── examples/
│   ├── llm-interaction/      # LLM API examples
│   ├── mcp-integration/      # MCP server examples
│   └── ai-basics/            # General AI/ML examples
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pravi-ai
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration

Most examples require API keys. Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

## Examples

### LLM Interaction

Examples for working with various LLM providers:

- **OpenAI GPT**: `examples/llm-interaction/openai_example.py`
- **Anthropic Claude**: `examples/llm-interaction/anthropic_example.py`
- **Streaming Responses**: `examples/llm-interaction/streaming_example.py`
- **Function Calling**: `examples/llm-interaction/function_calling_example.py`

### MCP Server Integration

Examples for connecting to and using MCP servers:

- **Basic MCP Client**: `examples/mcp-integration/basic_client.py`
- **Tool Invocation**: `examples/mcp-integration/tool_usage.py`
- **Resource Management**: `examples/mcp-integration/resource_example.py`

### AI Basics

Fundamental AI/ML concepts and implementations:

- **Text Classification**: `examples/ai-basics/text_classification.py`
- **Embeddings**: `examples/ai-basics/embeddings_example.py`
- **RAG (Retrieval Augmented Generation)**: `examples/ai-basics/rag_example.py`

## Usage

Each example is self-contained and can be run independently:

```bash
python examples/llm-interaction/openai_example.py
```

## Requirements

- Python 3.8+
- API keys for the services you want to use (OpenAI, Anthropic, etc.)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic API Documentation](https://docs.anthropic.com)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io)
