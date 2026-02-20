"""
Main Application Entry Point: The MCP-ADK Bridge.

This script demonstrates how to integrate the Google Agent Development Kit (ADK) 
with the Model Context Protocol (MCP). It creates an autonomous agent that can 
discover and use tools from external MCP servers to help users.

Key ADK concepts for students:
1.  **LlmAgent**: Represents the AI model (Gemini) with its instructions and tools.
2.  **McpToolset**: An ADK component that automatically handles the complexity 
    of connecting to and communicating with MCP servers.
3.  **InMemoryRunner**: A high-level orchestrator that manages the conversation 
    loop, session history, and tool execution.
4.  **SessionService**: Manages the persistent state of a conversation.
"""

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
from rich.table import Table

from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.genai import types

# --- INITIALIZATION ---
# Load environment variables (like GOOGLE_API_KEY) from .env file
load_dotenv()

# Setup logging to stderr using Rich for beautiful formatting
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
        # 1. LOAD CONFIGURATION
        # We read the list of MCP servers we want to connect to.
        with open(config_file, 'r') as f:
            config = json.load(f)
            servers_config = config.get("mcpServers", {})

        # 2. CONNECT TO MCP SERVERS
        # We create a list of 'McpToolset' objects. In ADK, a 'Toolset' is a 
        # collection of tools that an agent can use.
        mcp_toolsets = []
        for name, info in servers_config.items():
            console.print(f"[cyan]Connecting to MCP server: {name}...[/cyan]")
            try:
                # The McpToolset handles the 'stdio' connection automatically.
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
                
                # DISCOVERY: We fetch tools to verify the connection and show the user.
                # In a real app, the LLM will discover these tools dynamically.
                tools = await toolset.get_tools()
                
                if tools:
                    # Displaying the discovered tools in a pretty table.
                    table = Table(title=f"Tools loaded from {name}", show_header=True, header_style="bold magenta")
                    table.add_column("Tool Name", style="cyan")
                    table.add_column("Description")
                    
                    for tool in tools:
                        # Accessing tool metadata. 
                        # Tools in ADK follow standard Python function signatures.
                        # Fix: In ADK, tool information is stored in the 'definition' attribute.
                        desc = tool.definition.description.split('\n')[0] if tool.definition.description else "No description"
                        table.add_row(tool.definition.name, desc)
                    
                    console.print(table)
                    console.print(f"[green]Successfully connected and loaded {len(tools)} tools from '{name}'.[/green]\n")
                else:
                    console.print(f"[yellow]Connected to '{name}', but no tools were found.[/yellow]\n")
                
                mcp_toolsets.append(toolset)
            except Exception as e:
                # If a server fails, we log it and continue.
                console.print(f"[bold yellow]Warning:[/bold yellow] Ignoring server '{name}' because we were not able to connect to it.")
                console.print(f"[red]Reason: {e}[/red]\n")

        if not mcp_toolsets:
            console.print("[bold yellow]Warning: No MCP servers were successfully connected. The agent will run without external tools.[/bold yellow]\n")

        # 3. INITIALIZE THE ADK AGENT
        # The LlmAgent is the 'brain'. We tell it who it is, what model to use,
        # and give it the toolsets we just created.
        console.print("[cyan]Initializing Google ADK Agent...[/cyan]")
        agent = LlmAgent(
            name="mcp_adk_agent",
            model="gemini-2.0-flash",
            instruction="You are a helpful assistant that uses the provided tools from MCP servers to answer user queries.",
            tools=mcp_toolsets
        )
        
        # 4. INITIALIZE THE RUNNER
        # The InMemoryRunner is responsible for the 'loop'. It takes the user input,
        # sends it to the agent, sees if the agent wants to call a tool, 
        # executes the tool, and sends the result back to the agent.
        runner = InMemoryRunner(
            app_name="mcp-adk-bridge",
            agent=agent
        )
        
        # 5. START A CONVERSATION SESSION
        # Sessions allow the agent to remember context from previous messages.
        session = await runner.session_service.create_session(
            app_name="mcp-adk-bridge",
            user_id="default_user"
        )

        console.print(Panel("[bold green]System Ready![/bold green]\nType your query below. Type 'exit' or 'quit' to stop."))
        
        # 6. INTERACTIVE CHAT LOOP
        while True:
            query = Prompt.ask("[bold blue]User[/bold blue]")
            
            if query.lower() in ["exit", "quit"]:
                break
            
            if not query.strip():
                continue
                
            with console.status("[bold green]Agent is thinking..."):
                try:
                    # Construct the user message using ADK's type system.
                    content = types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=query)]
                    )
                    
                    response_text = ""
                    # The runner.run_async method is an async generator.
                    # It yields 'events' (text chunks, tool calls, etc.)
                    async for event in runner.run_async(
                        user_id="default_user",
                        session_id=session.id,
                        new_message=content
                    ):
                        # We collect the text parts to display to the user.
                        if event.content and event.content.parts:
                            for part in event.content.parts:
                                if part.text:
                                    response_text += part.text
                    
                    # 7. DISPLAY AGENT RESPONSE
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
    # Entry point for the asyncio application.
    asyncio.run(main())
