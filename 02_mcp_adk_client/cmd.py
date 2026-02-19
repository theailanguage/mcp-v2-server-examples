import asyncio
import logging
import sys
import os
from typing import List
from dotenv import load_dotenv

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.logging import RichHandler

from mcp_client.manager import MCPClientManager
from mcp_client.adapter import adapt_tools
from google.adk.agents import LlmAgent

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

    manager = MCPClientManager(config_file)
    
    try:
        console.print("[cyan]Initializing MCP Client...[/cyan]")
        manager.load_config()
        await manager.connect_to_all()
        
        mcp_tools = await manager.list_all_tools()
        
        # Display discovered tools
        table = Table(title="Discovered MCP Tools", show_header=True, header_style="bold magenta")
        table.add_column("Server", style="dim")
        table.add_column("Tool Name", style="bold green")
        table.add_column("Description")
        
        # We need to track which tool belongs to which server for display 
        # but manager.list_all_tools returns a flat list. 
        # For simplicity, we just list them.
        for tool in mcp_tools:
            table.add_row("MCP Server", tool.name, tool.description or "N/A")
        
        console.print(table)
        
        if not mcp_tools:
            console.print("[yellow]No tools discovered. The agent will have no tools.[/yellow]")

        # Adapt tools for ADK
        adk_tools = adapt_tools(mcp_tools, manager)
        
        # Initialize ADK Agent
        console.print("[cyan]Initializing Google ADK Agent...[/cyan]")
        agent = LlmAgent(
            model="gemini-2.0-flash",
            name="mcp_adk_agent",
            instruction="You are a helpful assistant that uses the provided tools from MCP servers to answer user queries.",
            tools=adk_tools
        )
        
        console.print(Panel("[bold green]System Ready![/bold green]\nType your query below. Type 'exit' or 'quit' to stop."))
        
        while True:
            query = Prompt.ask("[bold blue]User[/bold blue]")
            
            if query.lower() in ["exit", "quit"]:
                break
                
            with console.status("[bold green]Agent is thinking..."):
                try:
                    # agent.run is typically async or returns a response object
                    # Based on ADK docs, we can use agent.run(query)
                    response = await agent.run(query)
                    
                    # Output response
                    console.print(Panel(response.text, title="[bold magenta]Agent Response[/bold magenta]", border_style="magenta"))
                except Exception as e:
                    console.print(f"[red]Error during agent execution: {e}[/red]")

    except Exception as e:
        console.print(f"[red]Initialization failed: {e}[/red]")
    finally:
        await manager.shutdown()
        console.print("[yellow]MCP connection closed.[/yellow]")

if __name__ == "__main__":
    asyncio.run(main())
