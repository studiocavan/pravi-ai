"""
MCP Resource Management Example

This example demonstrates how to work with resources provided by
MCP servers, including listing, reading, and subscribing to resources.
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def list_resources():
    """List all resources provided by the MCP server"""

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-everything"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("MCP Resource Management Example")
            print("="*50)

            # List all resources
            resources_response = await session.list_resources()
            resources = resources_response.resources

            print(f"\nFound {len(resources)} resources:\n")

            for i, resource in enumerate(resources, 1):
                print(f"{i}. Resource: {resource.name}")
                print(f"   URI: {resource.uri}")
                if resource.description:
                    print(f"   Description: {resource.description}")
                if hasattr(resource, 'mimeType'):
                    print(f"   MIME Type: {resource.mimeType}")
                print()


async def read_multiple_resources():
    """Read multiple resources from the MCP server"""

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-everything"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("\nReading Multiple Resources")
            print("="*50)

            # Get all resources
            resources_response = await session.list_resources()
            resources = resources_response.resources

            # Read first 3 resources
            for resource in resources[:3]:
                print(f"\nReading: {resource.uri}")
                print("-" * 50)

                try:
                    result = await session.read_resource(resource.uri)

                    for content in result.contents:
                        if hasattr(content, 'text'):
                            # Display first 200 characters of text content
                            text = content.text
                            preview = text[:200] + "..." if len(text) > 200 else text
                            print(preview)
                        elif hasattr(content, 'blob'):
                            print(f"[Binary content: {len(content.blob)} bytes]")
                        else:
                            print(content)

                except Exception as e:
                    print(f"Error reading resource: {e}")


async def subscribe_to_resources():
    """
    Subscribe to resource updates (if supported by the server)
    This allows monitoring changes to resources
    """

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-everything"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("\nResource Subscription Example")
            print("="*50)

            # Get resources
            resources_response = await session.list_resources()
            resources = resources_response.resources

            if resources:
                resource_uri = resources[0].uri
                print(f"\nSubscribing to: {resource_uri}")

                try:
                    # Subscribe to the resource
                    await session.subscribe_resource(resource_uri)
                    print("✓ Successfully subscribed")

                    # In a real application, you would set up a listener
                    # for resource updates here

                    # Unsubscribe when done
                    await session.unsubscribe_resource(resource_uri)
                    print("✓ Unsubscribed")

                except Exception as e:
                    print(f"Subscription error: {e}")
                    print("Note: Not all servers support subscriptions")


async def search_resources():
    """
    Search or filter resources based on criteria
    """

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-everything"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("\nResource Search Example")
            print("="*50)

            # Get all resources
            resources_response = await session.list_resources()
            resources = resources_response.resources

            # Example: Filter by URI pattern
            search_term = "file"
            matching_resources = [
                r for r in resources
                if search_term in r.uri.lower()
            ]

            print(f"\nResources matching '{search_term}':")
            for resource in matching_resources:
                print(f"  - {resource.name} ({resource.uri})")

            # Example: Group by MIME type
            print("\nResources by type:")
            by_type = {}
            for resource in resources:
                mime_type = getattr(resource, 'mimeType', 'unknown')
                if mime_type not in by_type:
                    by_type[mime_type] = []
                by_type[mime_type].append(resource.name)

            for mime_type, names in by_type.items():
                print(f"  {mime_type}: {len(names)} resource(s)")


async def resource_metadata():
    """
    Extract and display detailed metadata about resources
    """

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-everything"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("\nResource Metadata Example")
            print("="*50)

            resources_response = await session.list_resources()
            resources = resources_response.resources

            for resource in resources[:5]:  # First 5 resources
                print(f"\nResource: {resource.name}")
                print(f"  URI: {resource.uri}")

                # Display all available attributes
                for attr in dir(resource):
                    if not attr.startswith('_'):
                        value = getattr(resource, attr)
                        if not callable(value):
                            print(f"  {attr}: {value}")


async def main():
    """Run MCP resource examples"""
    try:
        await list_resources()
        print("\n" + "="*50 + "\n")

        await read_multiple_resources()
        print("\n" + "="*50 + "\n")

        await subscribe_to_resources()
        print("\n" + "="*50 + "\n")

        await search_resources()
        print("\n" + "="*50 + "\n")

        await resource_metadata()

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have an MCP server installed")
        print("Install: npm install -g @modelcontextprotocol/server-everything")


if __name__ == "__main__":
    asyncio.run(main())
