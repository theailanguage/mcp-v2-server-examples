import asyncio
import json
import re
from typing import Any, Callable, Dict, List
import mcp.types as types

def create_adk_tool(tool: types.Tool, manager: Any) -> Callable:
    """
    Creates a proxy function compatible with Google ADK from an MCP Tool.
    
    Args:
        tool: The MCP Tool definition.
        manager: The MCPClientManager instance to use for calls.
    """
    original_name = tool.name
    description = tool.description or ""
    
    # Sanitize name for Python identifier compatibility
    # ADK/Pydantic validation often requires valid identifiers for names.
    sanitized_name = re.sub(r'[^a-zA-Z0-9_]', '_', original_name)
    if not sanitized_name[0].isalpha() and sanitized_name[0] != '_':
        sanitized_name = '_' + sanitized_name

    # Include the schema in the docstring to help the LLM understand the parameters
    schema_str = json.dumps(tool.inputSchema, indent=2)
    
    async def mcp_proxy_tool(**kwargs) -> Dict[str, Any]:
        """
        Proxy for MCP tool.
        """
        # ADK might pass tool_context, we remove it before forwarding to MCP
        kwargs.pop('tool_context', None)
        
        try:
            # We use the original_name here because the server expects it
            result = await manager.call_tool(original_name, kwargs)
            response_text = ""
            for block in result.content:
                if block.type == 'text':
                    response_text += getattr(block, 'text', '')
                elif block.type == 'resource':
                    # Handle other block types if necessary
                    response_text += f"\n[Resource: {getattr(block, 'uri', 'unknown')}]"
            return {"result": response_text}
        except Exception as e:
            return {"error": str(e)}

    # Set metadata for ADK
    mcp_proxy_tool.__name__ = sanitized_name
    # We combine description and schema in the docstring.
    # Google ADK uses the docstring for the tool's description in the model's tool definition.
    mcp_proxy_tool.__doc__ = f"{description}\n\nParameters Schema:\n{schema_str}"
    
    return mcp_proxy_tool

def adapt_tools(mcp_tools: List[types.Tool], manager: Any) -> List[Callable]:
    """
    Converts a list of MCP tools into ADK proxy functions.
    """
    return [create_adk_tool(t, manager) for t in mcp_tools]
