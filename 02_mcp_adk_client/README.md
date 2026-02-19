# MCP-ADK Bridge

## Project Overview
This project provides a seamless integration between the **Google Agent Development Kit (ADK)** and the **Model Context Protocol (MCP)**. It enables a Google ADK Agent (e.g., powered by Gemini) to dynamically discover, connect to, and utilize tools hosted on any configured MCP server.

By bridging these two standards, developers can build powerful AI agents that leverage a vast ecosystem of existing MCP tools for tasks like web searching, database access, or hardware control, all within the Google ADK framework.

## Directory Structure
- `mcp_client/`: Contains the core logic for managing MCP sessions and adapting MCP tool schemas into Google ADK-compatible proxy functions.
  - `manager.py`: Handles the lifecycle of MCP server connections via STDIO.
  - `adapter.py`: Translates MCP tool definitions into Python functions that the ADK Agent can invoke.
- `servers/`: Contains custom MCP server implementations.
  - `echo_server/`: A simple echo server used for testing.
- `cmd.py`: The CLI entry point. It initializes the `MCPClientManager`, connects to servers, discovers tools, creates the ADK Agent, and starts an interactive chat loop.
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
Start the interactive agent loop using `uv`:
```bash
uv run cmd.py
```

### Testing with the Echo Server
You can test the setup using the included `echo-server`. When running `cmd.py`, the agent should discover the `echo_tool` and be able to use it. You can also query the resource `resource://echo/status` if the agent is configured to handle resources (the current `adapter.py` focuses on tools).

## Legal & Attribution
This project integrates multiple open-source technologies. Please refer to the following files for licensing and trademark information:
- [ATTRIBUTION.md](ATTRIBUTION.md): Credits for Google ADK and Model Context Protocol.
- [LICENSE](LICENSE): Project license terms.
