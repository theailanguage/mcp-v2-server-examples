import os
from dotenv import load_dotenv
# Import the MCPServer class from the MCP SDK.
from mcp.server.mcpserver import MCPServer

# Load environment variables from a .env file if it exists.
# This is useful for local development and for setting the TERMINAL_WORKSPACE.
load_dotenv()

# Import the tool logic we defined in the other file.
try:
    from .tools import execute_command
except ImportError:
    # This fallback allows the script to be run directly: python main.py
    from tools import execute_command

def main():
    """
    Main entry point for the Terminal MCP Server.
    """
    
    # 1. Initialize the MCP Server.
    server = MCPServer("TerminalServer")

    # 2. Register our tool.
    server.add_tool(execute_command)

    # 3. Start the server.
    # Stdio stands for "Standard Input/Output".
    print("Terminal MCP Server starting...", flush=True)
    server.run(transport='stdio')

# The following block ensures that main() only runs if this file is executed directly.
if __name__ == "__main__":
    main()
