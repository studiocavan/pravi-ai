"""
MCP Service - Model Context Protocol Integration
Provides access to MCP tools and resources
"""

from typing import List, Dict, Optional
import asyncio
import os
import tempfile
import logging
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)


class MCPService:
    """Service for interacting with MCP servers"""

    def __init__(self):
        self.server_params = None
        self.available_tools = []
        self.enabled = False

        # Try to configure MCP server on initialization
        self._configure_server()

    def _configure_server(self):
        """Configure MCP server connection"""
        try:
            # Get cross-platform temp directory
            # Can be overridden with MCP_FS_PATH environment variable
            fs_path = os.getenv("MCP_FS_PATH", tempfile.gettempdir())

            # Using the filesystem MCP server as an example
            # You can change this to other MCP servers
            self.server_params = StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", fs_path],
                env=None
            )
            self.enabled = True
        except Exception as e:
            logger.warning(f"MCP server configuration failed: {e}")
            self.enabled = False

    async def check_health(self) -> bool:
        """Check if MCP service is available"""
        if not self.enabled or not self.server_params:
            return False

        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    return True
        except Exception:
            return False

    async def list_tools(self) -> List[Dict]:
        """List all available MCP tools"""
        if not self.enabled or not self.server_params:
            return []

        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    tools_response = await session.list_tools()
                    tools = []

                    for tool in tools_response.tools:
                        tools.append({
                            "name": tool.name,
                            "description": tool.description or "No description",
                            "input_schema": getattr(tool, 'inputSchema', {})
                        })

                    self.available_tools = tools
                    return tools

        except Exception as e:
            logger.error(f"Error listing MCP tools: {e}")
            return []

    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict
    ) -> Optional[str]:
        """
        Call a specific MCP tool

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool result as string
        """
        if not self.enabled or not self.server_params:
            return None

        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    result = await session.call_tool(tool_name, arguments=arguments)

                    # Extract text content from result
                    content_parts = []
                    for content in result.content:
                        if hasattr(content, 'text'):
                            content_parts.append(content.text)
                        else:
                            content_parts.append(str(content))

                    return "\n".join(content_parts)

        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            return None

    async def list_resources(self) -> List[Dict]:
        """List all available MCP resources"""
        if not self.enabled or not self.server_params:
            return []

        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    resources_response = await session.list_resources()
                    resources = []

                    for resource in resources_response.resources:
                        resources.append({
                            "name": resource.name,
                            "uri": resource.uri,
                            "description": resource.description or "No description",
                            "mime_type": getattr(resource, 'mimeType', 'unknown')
                        })

                    return resources

        except Exception as e:
            logger.error(f"Error listing MCP resources: {e}")
            return []

    async def read_resource(self, resource_uri: str) -> Optional[str]:
        """Read a specific MCP resource"""
        if not self.enabled or not self.server_params:
            return None

        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    result = await session.read_resource(resource_uri)

                    content_parts = []
                    for content in result.contents:
                        if hasattr(content, 'text'):
                            content_parts.append(content.text)

                    return "\n".join(content_parts)

        except Exception as e:
            logger.error(f"Error reading MCP resource: {e}")
            return None

    async def process_query(self, query: str) -> Optional[Dict]:
        """
        Process a user query and determine if MCP tools can help

        Args:
            query: User's question

        Returns:
            Dict with content and tools used, or None
        """
        if not self.enabled or not self.server_params:
            return None

        # Simple keyword-based tool selection
        # In a production system, you'd use the LLM to decide which tools to use
        query_lower = query.lower()

        try:
            # Example: If query mentions files, try to list available resources
            if any(word in query_lower for word in ["file", "document", "read", "show"]):
                resources = await self.list_resources()

                if resources:
                    resource_info = "\n".join([
                        f"- {r['name']}: {r['uri']}"
                        for r in resources[:5]  # Limit to first 5
                    ])

                    return {
                        "content": f"Available resources:\n{resource_info}",
                        "tools_used": ["list_resources"]
                    }

            # Example: List available tools if query asks about capabilities
            if any(word in query_lower for word in ["tool", "capability", "can you", "able to"]):
                tools = await self.list_tools()

                if tools:
                    tool_info = "\n".join([
                        f"- {t['name']}: {t['description']}"
                        for t in tools[:5]
                    ])

                    return {
                        "content": f"Available tools:\n{tool_info}",
                        "tools_used": ["list_tools"]
                    }

            return None

        except Exception as e:
            logger.error(f"Error processing MCP query: {e}")
            return None


# Example MCP server configurations
MCP_SERVER_CONFIGS = {
    "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        "description": "Access local filesystem"
    },
    "sqlite": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sqlite"],
        "description": "Query SQLite databases"
    },
    "github": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "description": "Interact with GitHub repositories"
    },
    "everything": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-everything"],
        "description": "Example server with multiple capabilities"
    }
}
