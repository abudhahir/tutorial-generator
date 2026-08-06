"""
MCP (Model Context Protocol) Configuration for the blog generator.

This file defines the MCP server configuration and available tools.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MCPServerConfig:
    """Configuration for MCP server connection."""
    
    # Server type (stdio, tcp, etc.)
    server_type: str = "stdio"
    
    # Server executable path
    server_path: str = ""
    
    # Server arguments
    server_args: List[str] = None
    
    # Connection parameters
    host: str = "localhost"
    port: int = 8001
    
    # Authentication
    api_key: str = ""
    
    # Timeout settings
    connection_timeout: int = 30
    request_timeout: int = 60
    
    def __post_init__(self):
        if self.server_args is None:
            self.server_args = []


@dataclass
class MCPToolConfig:
    """Configuration for MCP tools."""
    
    # Tool name
    name: str
    
    # Tool description
    description: str
    
    # Tool type (file, database, etc.)
    tool_type: str
    
    # Whether tool is enabled
    enabled: bool = True
    
    # Tool-specific configuration
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}


# Default MCP server configuration
DEFAULT_MCP_CONFIG = MCPServerConfig(
    server_type="stdio",
    server_path="",  # Will be auto-detected
    server_args=["--verbose"],
    connection_timeout=30,
    request_timeout=60
)

# Available MCP tools
AVAILABLE_MCP_TOOLS = [
    MCPToolConfig(
        name="filesystem",
        description="File system operations (read, write, list, etc.)",
        tool_type="filesystem",
        enabled=True,
        config={
            "root_path": "./blogs",
            "allowed_extensions": [".md", ".py", ".js", ".html", ".css", ".json", ".txt"],
            "max_file_size": 10 * 1024 * 1024,  # 10MB
        }
    ),
    MCPToolConfig(
        name="database",
        description="Database operations (query, insert, update, etc.)",
        tool_type="database",
        enabled=False,
        config={
            "connection_string": "",
            "max_query_time": 30,
        }
    ),
    MCPToolConfig(
        name="http",
        description="HTTP client operations (GET, POST, etc.)",
        tool_type="http",
        enabled=False,
        config={
            "timeout": 30,
            "max_redirects": 5,
            "user_agent": "I'm Poster Blog Generator/1.0",
        }
    )
]

# MCP tool registry
class MCPToolRegistry:
    """Registry for managing MCP tools."""
    
    def __init__(self):
        self.tools: Dict[str, MCPToolConfig] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default MCP tools."""
        for tool in AVAILABLE_MCP_TOOLS:
            self.register_tool(tool)
    
    def register_tool(self, tool: MCPToolConfig):
        """Register an MCP tool."""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> MCPToolConfig:
        """Get an MCP tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[MCPToolConfig]:
        """List all registered MCP tools."""
        return list(self.tools.values())
    
    def get_enabled_tools(self) -> List[MCPToolConfig]:
        """Get all enabled MCP tools."""
        return [tool for tool in self.tools.values() if tool.enabled]
    
    def enable_tool(self, name: str):
        """Enable an MCP tool."""
        if name in self.tools:
            self.tools[name].enabled = True
    
    def disable_tool(self, name: str):
        """Disable an MCP tool."""
        if name in self.tools:
            self.tools[name].enabled = False


# Global MCP tool registry instance
mcp_tool_registry = MCPToolRegistry()


def get_mcp_config() -> MCPServerConfig:
    """Get the MCP server configuration."""
    return DEFAULT_MCP_CONFIG


def get_mcp_tools() -> List[MCPToolConfig]:
    """Get available MCP tools."""
    return mcp_tool_registry.get_enabled_tools()


def get_mcp_tool(name: str) -> MCPToolConfig:
    """Get a specific MCP tool."""
    return mcp_tool_registry.get_tool(name)
