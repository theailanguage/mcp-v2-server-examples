import logging
import sys
from mcp.server.mcpserver import MCPServer
from .tools import echo
from .resources import connection_status

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("echo-server")

# Initialize the MCP Server
server = MCPServer("echo-server")

@server.tool()
def echo_tool(text: str) -> str:
    """
    Echoes the input text back to the caller.
    
    Args:
        text: The text to be echoed.
    """
    logger.info(f"Tool 'echo_tool' called with text: {text}")
    return echo(text)

@server.resource("resource://echo/status")
def status_resource() -> str:
    """
    Returns the current connection status of the echo server.
    """
    logger.info("Resource 'resource://echo/status' accessed.")
    return connection_status()

if __name__ == "__main__":
    logger.info("Starting echo-server...")
    server.run()
