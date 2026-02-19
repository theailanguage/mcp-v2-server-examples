# MCP-ADK Bridge

## Project Overview
This project provides a seamless integration between the **Google Agent Development Kit (ADK)** and the **Model Context Protocol (MCP)**. It enables a Google ADK Agent (powered by Gemini) to dynamically discover, connect to, and utilize tools hosted on any configured MCP server using the native `McpToolset`.

## Directory Structure
- `servers/`: Contains custom MCP server implementations.
  - `echo_server/`: A simple echo server used for testing.
- `cmd.py`: The CLI entry point. It initializes the `McpToolset` for each configured server, creates the ADK Agent, and starts an interactive chat loop using `InMemoryRunner`.
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

## Architecture
The system uses the native `google.adk.tools.mcp_tool.McpToolset` to handle MCP communication. This toolset automatically manages the lifecycle of the MCP server subprocesses and exposes their tools to the Gemini model.

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
                          │
                          └── Tools (e.g., echo_tool)
```

## Legal & Attribution
This project integrates multiple open-source technologies. Please refer to [ATTRIBUTION.md](ATTRIBUTION.md) for licensing and trademark information.
