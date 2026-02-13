# MCP Terminal Workspace

This workspace contains a set of Model Context Protocol (MCP) servers and tools designed to empower AI agents with system-level capabilities, specifically terminal access. This project demonstrates how to build a robust MCP server using the high-level `MCPServer` implementation.

## 🏗 Project Structure

This repository follows a hierarchical structure for organizing MCP servers.

- `servers/`: Contains individual MCP server implementations.
  - `terminal_server/`: A server providing a tool to execute shell commands.
- `requirements.txt`: Global dependencies for the project.
- `ATTRIBUTION.md`: Open-source credits and trademark disclaimers.
- `LICENSE`: Project licensing information.

## 🛠 Architecture Topology

The workspace is designed to be extensible. Each directory under `servers/` represents a standalone MCP server that can be integrated with clients like Claude Desktop or Google ADK-based agents.

```text
Root
├── servers/
│   └── terminal_server/ (Logic for shell execution)
├── requirements.txt
├── ATTRIBUTION.md
└── LICENSE
```

---

# 🖥 Terminal MCP Server

The Terminal MCP Server allows an AI (like Claude) to interact with your computer's terminal using the high-level `MCPServer` implementation.

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

### 2. Global Setup (using `uv`)
To set up the project environment using `uv`, follow these steps from the root directory:

```bash
# Initialize the project if not already done
uv init

# Create a virtual environment
uv venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies from requirements.txt
uv pip install -r requirements.txt
```

*Note: You can also use `uv sync` if a `pyproject.toml` is present.*

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
        "/PATH/TO/YOUR/PROJECT/servers/terminal_server",
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

### 4. Running the Server Manually
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
Open the file in a text editor and add the entry to the `mcpServers` object as shown in the **Workspace Configuration** section above.

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

## ⚖️ License and Attributions

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.
Refer to [ATTRIBUTION.md](ATTRIBUTION.md) for information regarding third-party frameworks like the Google ADK and the Model Context Protocol.
