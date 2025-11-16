"""
Basic MCP Client Example

This example demonstrates how to connect to and interact with
a Model Context Protocol (MCP) server using Python.
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def connect_to_server():
    """Connect to an MCP server and list available resources"""

    # Define server parameters
    # This example assumes a local MCP server
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-everything"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            print("Connected to MCP Server!")
            print("="*50)

            # List available resources
            resources = await session.list_resources()
            print(f"\nAvailable Resources ({len(resources.resources)}):")
            for resource in resources.resources:
                print(f"  - {resource.name}: {resource.uri}")
                if resource.description:
                    print(f"    Description: {resource.description}")

            print("\n" + "="*50)

            # List available tools
            tools = await session.list_tools()
            print(f"\nAvailable Tools ({len(tools.tools)}):")
            for tool in tools.tools:
                print(f"  - {tool.name}")
                if tool.description:
                    print(f"    Description: {tool.description}")

            print("\n" + "="*50)

            # List available prompts
            prompts = await session.list_prompts()
            print(f"\nAvailable Prompts ({len(prompts.prompts)}):")
            for prompt in prompts.prompts:
                print(f"  - {prompt.name}")
                if prompt.description:
                    print(f"    Description: {prompt.description}")


async def read_resource():
    """Read a specific resource from the MCP server"""

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-everything"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List resources first
            resources = await session.list_resources()

            if resources.resources:
                # Read the first available resource
                resource_uri = resources.resources[0].uri

                print(f"\nReading resource: {resource_uri}")
                print("="*50)

                result = await session.read_resource(resource_uri)

                print(f"Resource contents:")
                for content in result.contents:
                    print(content.text if hasattr(content, 'text') else content)


async def main():
    """Run MCP client examples"""
    try:
        print("MCP Basic Client Examples\n")

        await connect_to_server()
        print("\n" + "="*50 + "\n")

        await read_resource()

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have an MCP server running")
        print("Install example server: npm install -g @modelcontextprotocol/server-everything")


if __name__ == "__main__":
    asyncio.run(main())
