"""
MCP Tool Usage Example

This example demonstrates how to invoke tools provided by
MCP servers and integrate them with LLM workflows.
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def list_and_call_tools():
    """List available tools and call one"""

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-everything"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("MCP Tool Usage Example")
            print("="*50)

            # List all available tools
            tools = await session.list_tools()
            print(f"\nAvailable Tools: {len(tools.tools)}")

            for i, tool in enumerate(tools.tools, 1):
                print(f"\n{i}. {tool.name}")
                print(f"   Description: {tool.description}")
                if hasattr(tool, 'inputSchema'):
                    print(f"   Input Schema: {json.dumps(tool.inputSchema, indent=2)}")

            # Call a tool if any are available
            if tools.tools:
                print("\n" + "="*50)
                print(f"\nCalling tool: {tools.tools[0].name}")

                # Prepare arguments based on the tool's schema
                # This is a simplified example - adjust based on actual tool
                tool_args = {}

                try:
                    result = await session.call_tool(
                        tools.tools[0].name,
                        arguments=tool_args
                    )

                    print(f"\nTool Result:")
                    for content in result.content:
                        if hasattr(content, 'text'):
                            print(content.text)
                        else:
                            print(content)

                except Exception as e:
                    print(f"Error calling tool: {e}")


async def integrate_with_llm():
    """
    Demonstrate integrating MCP tools with an LLM workflow
    This shows how tools from MCP servers can enhance LLM capabilities
    """
    from anthropic import Anthropic
    import os
    from dotenv import load_dotenv

    load_dotenv()

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-everything"],
        env=None
    )

    print("\nIntegrating MCP Tools with LLM")
    print("="*50)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Get tools from MCP server
            mcp_tools_response = await session.list_tools()
            mcp_tools = mcp_tools_response.tools

            # Convert MCP tools to Anthropic tool format
            anthropic_tools = []
            for tool in mcp_tools:
                anthropic_tool = {
                    "name": tool.name,
                    "description": tool.description or "No description provided",
                    "input_schema": getattr(tool, 'inputSchema', {
                        "type": "object",
                        "properties": {},
                        "required": []
                    })
                }
                anthropic_tools.append(anthropic_tool)

            print(f"\nConverted {len(anthropic_tools)} MCP tools for LLM use")

            # Use with Anthropic Claude
            try:
                client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

                # Example conversation where the LLM might use MCP tools
                messages = [{
                    "role": "user",
                    "content": "What tools do you have available?"
                }]

                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1024,
                    tools=anthropic_tools,
                    messages=messages
                )

                print(f"\nLLM Response:")
                for content in response.content:
                    if hasattr(content, 'text'):
                        print(content.text)

            except Exception as e:
                print(f"LLM integration error: {e}")
                print("Make sure ANTHROPIC_API_KEY is set in .env")


async def custom_tool_workflow():
    """
    Example of a custom workflow using MCP tools
    Simulates a complex task requiring multiple tool calls
    """

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-everything"],
        env=None
    )

    print("\nCustom Tool Workflow Example")
    print("="*50)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Get available tools
            tools = await session.list_tools()

            print(f"\nWorkflow: Using {len(tools.tools)} available tools")

            # Example workflow:
            # 1. List tools
            # 2. Select appropriate tool based on task
            # 3. Execute tool
            # 4. Process results

            for tool in tools.tools[:3]:  # Process first 3 tools
                print(f"\nProcessing with tool: {tool.name}")

                try:
                    # Call tool with empty args (adjust based on actual requirements)
                    result = await session.call_tool(tool.name, arguments={})

                    print(f"  ✓ Success")

                except Exception as e:
                    print(f"  ✗ Error: {e}")


async def main():
    """Run MCP tool usage examples"""
    try:
        await list_and_call_tools()
        print("\n" + "="*50 + "\n")

        await integrate_with_llm()
        print("\n" + "="*50 + "\n")

        await custom_tool_workflow()

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have an MCP server installed")


if __name__ == "__main__":
    asyncio.run(main())
