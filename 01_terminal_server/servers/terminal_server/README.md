# Terminal MCP Server

[⬅ Back to Root](../../README.md)

Welcome to the **Terminal MCP Server**! This project is a basic example of how to build a Model Context Protocol (MCP) server that allows an AI (like Claude) to interact with your computer's terminal.

## 🎓 Learning Objectives
- Understand how to structure an MCP server in Python.
- Learn how to use the `mcp` library to register tools.
- Learn how to connect an MCP server to Claude Desktop using the `stdio` transport.

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10 or higher** installed on your machine.
- **Claude Desktop** installed (if you want to use the GUI).

### 2. Installation
Ensure you have installed the requirements from the [root directory](../../requirements.txt):

```bash
pip install -r ../../requirements.txt
```

### 3. Configuration (Connecting to Claude)
To let Claude Desktop know about your new server, you need to add it to your `claude_desktop_config.json` file.

#### File Locations:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json` (if applicable)

#### What to Add:
Open the file in a text editor and add the following entry to the `mcpServers` object. **Make sure to replace the path with the actual absolute path to your file.**

```json
{
  "mcpServers": {
    "terminal-server": {
      "command": "python",
      "args": [
        "/PATH/TO/YOUR/servers/terminal_server/main.py"
      ]
    }
  }
}
```

*Note: On Windows, use `python.exe` and double backslashes in the path (e.g., `C:\\Users\\...`).*

### 4. Testing Locally
Before connecting to Claude, you can test if the server works using the **MCP Inspector**. Run this command in your terminal:

```bash
npx @modelcontextprotocol/inspector python /PATH/TO/YOUR/servers/terminal_server/main.py
```

This will open a web interface where you can manually trigger the `execute_command` tool.

---

## ⚠️ Safety Warning
This server allows the AI to run **any** command on your computer. This is powerful but dangerous. 
- **Never** run this server on a public network.
- **Always** monitor what commands the AI is suggesting before you let it run them.
- In a real-world application, you should restrict the commands the server is allowed to run.

---

## 📂 Project Structure
- `main.py`: The entry point that initializes the MCPServer and registers tools.
- `tools.py`: Contains the logic for executing terminal commands using Python's `subprocess` module.
- `__init__.py`: Makes the directory a Python package.

---

## 🛠 How it Works
The server uses the **STDIO (Standard Input/Output)** transport. 
1. Claude Desktop starts the Python script as a background process.
2. Claude sends JSON-RPC messages to the script's `stdin`.
3. The `mcp` library parses these messages and calls the `execute_command` function.
4. The output of the command is sent back to Claude via `stdout`.
