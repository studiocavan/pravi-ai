# LLM Interaction Examples

This directory contains examples for interacting with various Large Language Model (LLM) APIs using Python.

## Examples

### 1. OpenAI Example (`openai_example.py`)
Demonstrates basic interactions with OpenAI's GPT models:
- Simple text completions
- Chat with conversation history
- Generating text embeddings

**Usage:**
```bash
python openai_example.py
```

### 2. Anthropic Claude Example (`anthropic_example.py`)
Shows how to use Anthropic's Claude models:
- Basic message completions
- System prompts for role definition
- Multi-turn conversations
- Structured output requests

**Usage:**
```bash
python anthropic_example.py
```

### 3. Streaming Example (`streaming_example.py`)
Demonstrates streaming responses for real-time output:
- OpenAI streaming
- Anthropic streaming
- Event-based streaming control
- Async streaming patterns

**Usage:**
```bash
python streaming_example.py
```

### 4. Function Calling Example (`function_calling_example.py`)
Advanced example showing how LLMs can call external functions:
- OpenAI function calling
- Anthropic tool use
- Multi-tool orchestration
- Function result integration

**Usage:**
```bash
python function_calling_example.py
```

## Setup

1. Install dependencies:
```bash
pip install openai anthropic python-dotenv
```

2. Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

## Key Concepts

### Temperature
Controls randomness in responses (0.0 = deterministic, 1.0 = creative)

### Max Tokens
Limits the length of generated responses

### System Prompts
Define the AI's role and behavior

### Streaming
Delivers responses incrementally for better UX

### Function Calling / Tool Use
Allows LLMs to interact with external tools and APIs
