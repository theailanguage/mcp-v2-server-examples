import asyncio
import json
import logging
import sys
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import mcp.types as types

logger = logging.getLogger("mcp-client-manager")

class MCPClientManager:
    """
    Manages connections to multiple MCP servers via STDIO.
    """
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.sessions: Dict[str, ClientSession] = {}
        self.exit_stack = asyncio.ExitStack()
        self._server_params: Dict[str, StdioServerParameters] = {}

    def load_config(self):
        """Loads the MCP server configurations from config.json."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                servers = config.get("mcpServers", {})
                for name, info in servers.items():
                    self._server_params[name] = StdioServerParameters(
                        command=info["command"],
                        args=info.get("args", []),
                        env=info.get("env")
                    )
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    async def connect_to_all(self):
        """Connects to all configured MCP servers."""
        for name, params in self._server_params.items():
            try:
                # We use a context manager pattern within the class lifecycle
                transport = await self.exit_stack.enter_async_context(stdio_client(params))
                read, write = transport
                session = await self.exit_stack.enter_async_context(ClientSession(read, write))
                
                await session.initialize()
                self.sessions[name] = session
                logger.info(f"Connected to MCP server: {name}")
            except Exception as e:
                logger.error(f"Failed to connect to {name}: {e}")

    async def list_all_tools(self) -> List[types.Tool]:
        """Aggregates tools from all connected servers."""
        all_tools = []
        for name, session in self.sessions.items():
            try:
                result = await session.list_tools()
                # result is usually a ListToolsResult which has a 'tools' attribute
                for tool in result.tools:
                    all_tools.append(tool)
            except Exception as e:
                logger.error(f"Failed to list tools for {name}: {e}")
        return all_tools

    async def call_tool(self, tool_name: str, arguments: dict) -> types.CallToolResult:
        """Calls a tool on the appropriate server."""
        for server_name, session in self.sessions.items():
            tools_result = await session.list_tools()
            if any(t.name == tool_name for t in tools_result.tools):
                return await session.call_tool(tool_name, arguments)
        
        raise ValueError(f"Tool {tool_name} not found on any server")

    async def shutdown(self):
        """Closes all sessions and transports."""
        await self.exit_stack.aclose()
