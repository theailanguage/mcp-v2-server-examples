"""
This is an example Model Context Protocol (MCP) server that provides a simple echo tool and status resource.

The Model Context Protocol (MCP) is an open standard that enables AI models to interact with external tools and data sources.
This server uses the FastMCP framework, which provides a high-level, ergonomic interface for building MCP servers.

Key concepts demonstrated in this file:
1.  **FastMCP Initialization**: Creating a named server instance.
2.  **Tool Registration**: Exposing functions as tools that an AI agent (like a Gemini model) can call.
3.  **Resource Registration**: Providing read-only data (like status information) via a standard URI format.
4.  **Protocol-Safe Logging**: Using stderr for logging to avoid interfering with the JSON-RPC communication on stdout.
"""

import logging
import sys
from mcp.server.fastmcp.server import FastMCP
from .tools import echo
from .resources import connection_status

# --- PROTOCOL SAFETY: LOGGING TO STDERR ---
# In the Model Context Protocol (MCP), the communication between the client (agent) and the server
# happens over standard input (stdin) and standard output (stdout) using JSON-RPC.
# If you use `print()` or write to stdout, it will corrupt the JSON-RPC stream.
# Therefore, all logging MUST be directed to standard error (stderr).
# Students: Always remember that stdout is for data (JSON-RPC), and stderr is for humans (logs).
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("echo-server")

# --- SERVER INITIALIZATION ---
# We initialize the FastMCP with a descriptive name.
# This name helps identify the server in logs and when multiple servers are connected to a client.
mcp = FastMCP("echo-server")

# --- TOOL REGISTRATION ---
# A 'tool' is a function that the AI agent can decide to call when it needs external information or actions.
# The `@mcp.tool()` decorator registers the following function as an MCP tool.
# The docstring and type hints are CRITICAL: the AI model uses them to understand:
# - What the tool does (the docstring)
# - What parameters it needs (the arguments and their types)
# Students: The LLM 'reads' your docstrings to decide if this tool is useful!
@mcp.tool()
def echo_tool(text: str) -> str:
    """
    Echoes the input text back to the caller.
    
    Args:
        text: The text to be echoed.
    """
    # We log tool execution to stderr for visibility during development and debugging.
    logger.info(f"Tool 'echo_tool' called with text: {text}")
    
    # We delegate the actual logic to a function in the 'tools.py' module.
    # This keeps our entry point clean and separates protocol logic from business logic.
    return echo(text)

# --- RESOURCE REGISTRATION ---
# A 'resource' is a piece of data that the AI agent can read, but not modify.
# Resources are identified by URIs (Uniform Resource Identifiers).
# The `@mcp.resource()` decorator registers a function that returns the content of the resource.
# Students: Think of resources like 'files' or 'URLs' that the agent can open to get context.
@mcp.resource("resource://echo/status")
def status_resource() -> str:
    """
    Returns the current connection status of the echo server.
    
    Resources are useful for providing static or dynamic data that doesn't require complex interaction.
    """
    logger.info("Resource 'resource://echo/status' accessed.")
    
    # We delegate the logic to 'resources.py'.
    return connection_status()

# --- SERVER ENTRY POINT ---
# This block ensures the server runs when the script is executed directly.
# The `mcp.run()` method starts the MCP transport (defaulting to stdio).
# 'stdio' transport means the server communicates via standard input and output.
if __name__ == "__main__":
    logger.info("Starting echo-server using stdio transport...")
    mcp.run(transport="stdio")
