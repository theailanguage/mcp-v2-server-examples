import asyncio
import json
import logging
import os
import sys
from typing import List

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.logging import RichHandler

from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.genai import types

# Load environment variables (like GOOGLE_API_KEY) from .env file
load_dotenv()

# Setup logging to stderr
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, console=Console(stderr=True))]
    )

console = Console()

async def main():
    setup_logging()
    
    config_file = "config.json"
    if not os.path.exists(config_file):
        console.print(f"[red]Error: {config_file} not found.[/red]")
        return

    try:
        # Load MCP configurations
        with open(config_file, 'r') as f:
            config = json.load(f)
            servers_config = config.get("mcpServers", {})

        # Create McpToolset instances for each server
        mcp_toolsets = []
        for name, info in servers_config.items():
            console.print(f"[cyan]Connecting to MCP server: {name}...[/cyan]")
            toolset = McpToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command=info["command"],
                        args=info.get("args", []),
                        env=info.get("env")
                    ),
                    timeout=15.0
                )
            )
            mcp_toolsets.append(toolset)

        # Initialize ADK Agent with the toolsets
        console.print("[cyan]Initializing Google ADK Agent...[/cyan]")
        agent = LlmAgent(
            name="mcp_adk_agent",
            model="gemini-2.0-flash",
            instruction="You are a helpful assistant that uses the provided tools from MCP servers to answer user queries.",
            tools=mcp_toolsets
        )
        
        # Initialize Runner to orchestrate the agent
        runner = InMemoryRunner(
            app_name="mcp-adk-bridge",
            agent=agent
        )
        
        # Create a session for the interaction
        session = await runner.session_service.create_session(
            app_name="mcp-adk-bridge",
            user_id="default_user"
        )

        console.print(Panel("[bold green]System Ready![/bold green]\nType your query below. Type 'exit' or 'quit' to stop."))
        
        while True:
            query = Prompt.ask("[bold blue]User[/bold blue]")
            
            if query.lower() in ["exit", "quit"]:
                break
            
            if not query.strip():
                continue
                
            with console.status("[bold green]Agent is thinking..."):
                try:
                    # Construct the user message
                    content = types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=query)]
                    )
                    
                    response_text = ""
                    # Run the agent and collect events
                    async for event in runner.run_async(
                        user_id="default_user",
                        session_id=session.id,
                        new_message=content
                    ):
                        if event.content and event.content.parts:
                            for part in event.content.parts:
                                if part.text:
                                    response_text += part.text
                    
                    # Output the aggregated response
                    if response_text:
                        console.print(Panel(response_text, title="[bold magenta]Agent Response[/bold magenta]", border_style="magenta"))
                    else:
                        console.print("[yellow]No text response received from agent.[/yellow]")
                        
                except Exception as e:
                    console.print(f"[red]Error during agent execution: {e}[/red]")

    except Exception as e:
        console.print(f"[red]Initialization failed: {e}[/red]")
    finally:
        console.print("[yellow]Shutting down...[/yellow]")

if __name__ == "__main__":
    asyncio.run(main())
