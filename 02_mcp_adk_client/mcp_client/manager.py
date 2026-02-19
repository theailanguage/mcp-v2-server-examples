import asyncio
import json
import logging
import sys
import os
from typing import Dict, List, Optional
from contextlib import AsyncExitStack, asynccontextmanager

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
        self.exit_stack = AsyncExitStack()
        self._server_params: Dict[str, StdioServerParameters] = {}

    def load_config(self):
        """Loads the MCP server configurations from config.json."""
        if not os.path.exists(self.config_path):
            logger.error(f"Config file not found: {self.config_path}")
            raise FileNotFoundError(f"Config file {self.config_path} not found.")

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
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse config JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    async def connect_to_all(self):
        """Connects to all configured MCP servers."""
        for name, params in self._server_params.items():
            try:
                logger.info(f"Connecting to MCP server '{name}' using command: {params.command} {' '.join(params.args)}")
                
                # Check if command exists if it's a relative path or just a command
                # This is a basic check; real-world usage might be more complex
                
                transport = await self.exit_stack.enter_async_context(stdio_client(params))
                read, write = transport
                session = await self.exit_stack.enter_async_context(ClientSession(read, write))
                
                await session.initialize()
                self.sessions[name] = session
                logger.info(f"Successfully connected to MCP server: {name}")
            except Exception as e:
                logger.error(f"Failed to connect to '{name}': {e}")
                logger.error(f"Command attempted: {params.command} {' '.join(params.args)}")
                # We don't raise here so that other servers can still be connected

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
            try:
                tools_result = await session.list_tools()
                if any(t.name == tool_name for t in tools_result.tools):
                    return await session.call_tool(tool_name, arguments)
            except Exception as e:
                logger.warning(f"Error checking tools on server {server_name}: {e}")
                continue
        
        raise ValueError(f"Tool {tool_name} not found on any active server session.")

    async def shutdown(self):
        """Closes all sessions and transports."""
        await self.exit_stack.aclose()
        logger.info("MCP connections closed.")
