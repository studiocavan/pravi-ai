# MCP Integration Examples

This directory contains examples for working with the Model Context Protocol (MCP) in Python. MCP is a protocol that enables LLMs to securely access tools, data, and services.

## What is MCP?

The Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to LLMs. It allows:
- **Tools**: Functions that LLMs can invoke
- **Resources**: Data that LLMs can read
- **Prompts**: Templated interactions

## Examples

### 1. Basic Client (`basic_client.py`)
Introduction to connecting with MCP servers:
- Establishing server connections
- Listing available resources
- Listing available tools
- Listing available prompts

**Usage:**
```bash
python basic_client.py
```

### 2. Tool Usage (`tool_usage.py`)
Working with MCP tools:
- Discovering available tools
- Invoking tools from MCP servers
- Integrating MCP tools with LLMs
- Building custom tool workflows

**Usage:**
```bash
python tool_usage.py
```

### 3. Resource Management (`resource_example.py`)
Managing MCP resources:
- Listing all resources
- Reading resource contents
- Subscribing to resource updates
- Searching and filtering resources
- Extracting resource metadata

**Usage:**
```bash
python resource_example.py
```

## Setup

### 1. Install Python Dependencies

```bash
pip install mcp anthropic python-dotenv
```

### 2. Install an MCP Server

For testing, you can use the example MCP server:

```bash
npm install -g @modelcontextprotocol/server-everything
```

Or install other MCP servers:
- `@modelcontextprotocol/server-filesystem` - File system access
- `@modelcontextprotocol/server-github` - GitHub integration
- `@modelcontextprotocol/server-sqlite` - SQLite database access

### 3. Configure Environment

Create a `.env` file if using LLM integration:

```env
ANTHROPIC_API_KEY=your_anthropic_key_here
```

## MCP Server Configuration

MCP servers can be run in different modes:

### Stdio Mode (Used in examples)
```python
server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-everything"],
    env=None
)
```

### Custom Server
You can create your own MCP server in Python or Node.js to expose custom tools and resources.

## Key Concepts

### Client Session
Manages the connection to an MCP server:
```python
async with ClientSession(read, write) as session:
    await session.initialize()
    # Use session methods
```

### Resources
Data sources that can be read:
- File contents
- Database records
- API responses
- Any structured data

### Tools
Functions that can be invoked:
- Data processing
- External API calls
- Calculations
- System operations

### Prompts
Pre-defined templates for interactions

## Common Patterns

### 1. List and Use
```python
# List available tools
tools = await session.list_tools()

# Use a specific tool
result = await session.call_tool(tool_name, arguments)
```

### 2. Resource Reading
```python
# List resources
resources = await session.list_resources()

# Read a resource
content = await session.read_resource(resource_uri)
```

### 3. LLM Integration
```python
# Get MCP tools
mcp_tools = await session.list_tools()

# Convert to LLM-compatible format
llm_tools = convert_to_llm_format(mcp_tools)

# Use with LLM
response = llm.create(tools=llm_tools, messages=messages)
```

## Troubleshooting

### Server Not Found
Ensure the MCP server is installed:
```bash
npm list -g @modelcontextprotocol/server-everything
```

### Connection Issues
Check that the server command and arguments are correct in `StdioServerParameters`.

### Permission Errors
Some MCP servers may require specific permissions or environment variables.

## Resources

- [MCP Specification](https://spec.modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Available MCP Servers](https://github.com/modelcontextprotocol/servers)
