# Import the MCPServer class from the MCP SDK.
# This class handles the complexity of the Model Context Protocol for us.
from mcp.server.mcpserver import MCPServer

# Import the tool logic we defined in the other file.
# We use a relative import here because main.py and tools.py are in the same directory.
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
    # We give it a name so that the client (like Claude Desktop) can identify it.
    server = MCPServer("TerminalServer")

    # 2. Register our tool.
    # The 'add_tool' method takes the function we wrote. 
    # The MCP SDK will automatically inspect the function's docstring and 
    # type hints to create the 'schema' that the AI needs to understand how 
    # to use the tool.
    # - The function name becomes the tool name.
    # - The docstring becomes the tool description.
    # - The type hints (command: str) become the input parameters.
    server.add_tool(execute_command)

    # 3. Start the server.
    # We use the 'stdio' transport, which is the standard way MCP servers 
    # communicate with desktop applications like Claude.
    # Stdio stands for "Standard Input/Output". The client sends JSON-RPC 
    # messages to the server's stdin and reads responses from its stdout.
    print("Terminal MCP Server starting...", flush=True)
    server.run(transport='stdio')

# The following block ensures that main() only runs if this file is executed directly.
if __name__ == "__main__":
    main()
