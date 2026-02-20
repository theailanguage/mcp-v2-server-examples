# MCP-ADK Bridge

## Project Overview
This project provides a seamless integration between the **Google Agent Development Kit (ADK)** and the **Model Context Protocol (MCP)**. It enables a Google ADK Agent (powered by Gemini) to dynamically discover, connect to, and utilize tools hosted on any configured MCP server using the native `McpToolset`.

Additionally, it provides a low-level programmatic interface for direct interaction with MCP servers without an AI agent, which is useful for debugging and understanding the protocol.

> **Note:** This project uses **MCP version 1** (and not version 2) because the **Google Agent Development Kit (ADK)** currently supports MCP version 1.

## Directory Structure
- `servers/`: Contains custom MCP server implementations.
  - `echo_server/`: A simple echo server used for testing.
- `mcp_client/`: Contains a low-level, manual MCP client manager for educational purposes.
  - `manager.py`: Implementation of `MCPClientManager` using `mcp.ClientSession`.
- `cmd.py`: The CLI entry point for the **Agentic** mode. It initializes the `McpToolset`, creates the ADK Agent, and starts an interactive chat loop.
- `cmd_mcp_client_manager.py`: The CLI entry point for the **Programmatic** mode. It uses the `MCPClientManager` to call tools directly via code.
- `config.json`: Configuration file where you define your MCP servers (command, arguments, and environment variables).
- `requirements.txt`: Lists the Python dependencies required for the project.
- `.env`: Environment variable storage for sensitive keys (like `GOOGLE_API_KEY`).

## Prerequisites
- **Python 3.10+**
- **[uv](https://github.com/astral-sh/uv)**: A fast Python package installer and resolver (recommended).

## Setup Instructions

### 1. Initialize the Project
```bash
uv init
uv venv
```

### 2. Activate the Virtual Environment
- **macOS/Linux:**
  ```bash
  source .venv/bin/activate
  ```
- **Windows:**
  ```bash
  .venv\Scripts\activate
  ```

### 3. Install Dependencies
```bash
uv add -r requirements.txt
```

### 4. Configure Environment Variables
Create or update the `.env` file in the project root and add your Google API Key:
```env
GOOGLE_API_KEY=your_api_key_here
```

### 5. Configure MCP Servers
Update `config.json` to include the MCP servers you want to use. Example:
```json
{
  "mcpServers": {
    "weather-server": {
      "command": "python",
      "args": ["-m", "weather_server"]
    },
    "echo-server": {
      "command": "python",
      "args": ["-m", "servers.echo_server.main"]
    }
  }
}
```

## Running the Code

### Agentic Mode (LLM-Powered)
Start the interactive agent loop using `uv`:
```bash
uv run cmd.py
```

### Programmatic Mode (Manual Execution)
To test MCP tools directly without the LLM, run the client manager interface:
```bash
uv run cmd_mcp_client_manager.py
```

## Architecture
The system supports two distinct modes of operation:

### 1. Agentic Mode (ADK)
Uses the native `google.adk.tools.mcp_tool.McpToolset` to handle MCP communication. The agent decides which tools to call based on the user's query.

```
cmd.py
  │
  └── InMemoryRunner
        │
        └── LlmAgent (Gemini 2.0 Flash)
              │
              └── McpToolset (Stdio)
                    │
                    └── MCP Server (Subprocess)
```

### 2. Programmatic Mode (Manual)
Uses a custom `MCPClientManager` to establish direct JSON-RPC sessions via STDIO. This mode is used for explicit tool calls where the logic is defined in the script rather than by an LLM.

```
cmd_mcp_client_manager.py
  │
  └── MCPClientManager
        │
        └── ClientSession (JSON-RPC)
              │
              └── MCP Server (Subprocess)
```

## Legal & Attribution
This project integrates multiple open-source technologies. Please refer to [ATTRIBUTION.md](ATTRIBUTION.md) for licensing and trademark information.
