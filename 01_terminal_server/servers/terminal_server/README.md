# Terminal MCP Server

[⬅ Back to Root](../../README.md)

Welcome to the **Terminal MCP Server**! This project is a basic example of how to build a Model Context Protocol (MCP) server that allows an AI (like Claude) to interact with your computer's terminal using the high-level `MCPServer` implementation.

## 🎓 Learning Objectives
- Understand how to structure an MCP server in Python.
- Learn how to use the `MCPServer` class to register tools automatically.
- Learn how to connect an MCP server to Claude Desktop using the `stdio` transport.
- Use `uv` for modern Python project management.

---

## 🛠 Tools

### `execute_command`
Executes a shell command within the configured workspace and returns its output or error message. This tool is the primary way for the AI to interact with the host system.
- **Arguments**: 
    - `command` (string): The full shell command to execute.

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10 or higher** installed on your machine.
- **[uv](https://docs.astral.sh/uv/)** installed (highly recommended for environment management).
- **Claude Desktop** installed (if you want to use the GUI).

### 2. Installation
We use `uv` to manage dependencies. From the root directory, run:

```bash
uv sync
```

This will create a virtual environment and install all necessary dependencies.

### 3. Workspace Configuration
The server restricts command execution to a specific directory. By default, it uses a `./workspace` folder or the current directory.

#### Option A: Using Environment Variables (Claude Desktop)
Update your `claude_desktop_config.json` to include the `env` key:

```json
{
  "mcpServers": {
    "terminal-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/PATH/TO/YOUR/servers/terminal_server",
        "run",
        "python",
        "main.py"
      ],
      "env": {
        "TERMINAL_WORKSPACE": "/path/to/your/desired/workspace"
      }
    }
  }
}
```

#### Option B: Using a `.env` file
Create a file named `.env` in the `servers/terminal_server/` directory:

```env
TERMINAL_WORKSPACE=./workspace
```

The server will automatically load this variable on startup using `python-dotenv`.

### 4. Running the Server
To run the server manually using `uv`:

```bash
uv run python servers/terminal_server/main.py
```

### 5. Configuration (Connecting to Claude)
To let Claude Desktop know about your new server, you need to add it to your `claude_desktop_config.json` file.

#### File Locations:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

#### What to Add:
Open the file in a text editor and add the entry to the `mcpServers` object as shown in the Workspace Configuration section above.

### 6. Testing Locally
Before connecting to Claude, you can test if the server works using the **MCP Inspector**:

```bash
npx @modelcontextprotocol/inspector uv run python servers/terminal_server/main.py
```

---

## ⚠️ Safety Warning
This server allows the AI to run **any** command on your computer within the workspace. This is powerful but dangerous. 
- **Never** run this server on a public network.
- **Always** monitor what commands the AI is suggesting before you let it run them.
- In a real-world application, you should restrict the commands the server is allowed to run.

---

## 📂 Project Structure
- `main.py`: The entry point that initializes the `MCPServer` and registers tools.
- `tools.py`: Contains the logic for executing terminal commands using Python's `subprocess` module.
- `__init__.py`: Makes the directory a Python package.

---

## 🛠 How it Works
The server uses the **STDIO (Standard Input/Output)** transport. 
1. Claude Desktop starts the Python script as a background process using `uv run`.
2. Claude sends JSON-RPC messages to the script's `stdin`.
3. The `MCPServer` instance handles these messages and calls the `execute_command` tool.
4. The output of the command is sent back to Claude via `stdout`.
5. Logs are sent to `stderr` to avoid corrupting the communication channel.
