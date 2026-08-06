"""
Hybrid MCP File Service for the blog generator.

This service demonstrates MCP concepts while providing real file operations.
It can be easily extended to use actual MCP tools when they become available.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import asyncio
from dataclasses import dataclass


@dataclass
class MCPTool:
    """Represents an MCP tool."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    handler: callable


@dataclass
class MCPResult:
    """Represents the result of an MCP tool call."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class HybridMCPService:
    """Hybrid MCP service that provides real file operations with MCP-like interface."""
    
    def __init__(self, verbose: bool = False):
        """Initialize the hybrid MCP service.
        
        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.tools: Dict[str, MCPTool] = {}
        self._register_default_tools()
        
        if self.verbose:
            print(f"🔧 Hybrid MCP Service initialized with {len(self.tools)} tools")
    
    def _register_default_tools(self):
        """Register default MCP-like tools."""
        
        # File writing tool
        self.tools["filesystem_write_file"] = MCPTool(
            name="filesystem_write_file",
            description="Write content to a file",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file"},
                    "content": {"type": "string", "description": "Content to write"},
                    "encoding": {"type": "string", "default": "utf-8", "description": "File encoding"}
                },
                "required": ["file_path", "content"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "file_path": {"type": "string"},
                    "bytes_written": {"type": "integer"},
                    "encoding": {"type": "string"}
                }
            },
            handler=self._handle_write_file
        )
        
        # Directory creation tool
        self.tools["filesystem_create_directory"] = MCPTool(
            name="filesystem_create_directory",
            description="Create a directory",
            input_schema={
                "type": "object",
                "properties": {
                    "directory_path": {"type": "string", "description": "Path to create"}
                },
                "required": ["directory_path"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "directory_path": {"type": "string"},
                    "created": {"type": "boolean"}
                }
            },
            handler=self._handle_create_directory
        )
        
        # Directory listing tool
        self.tools["filesystem_list_directory"] = MCPTool(
            name="filesystem_list_directory",
            description="List contents of a directory",
            input_schema={
                "type": "object",
                "properties": {
                    "directory_path": {"type": "string", "description": "Path to list"}
                },
                "required": ["directory_path"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "directory_path": {"type": "string"},
                    "contents": {"type": "array", "items": {"type": "string"}},
                    "total_items": {"type": "integer"}
                }
            },
            handler=self._handle_list_directory
        )
        
        # File existence check tool
        self.tools["filesystem_file_exists"] = MCPTool(
            name="filesystem_file_exists",
            description="Check if a file exists",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to check"}
                },
                "required": ["file_path"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "file_path": {"type": "string"},
                    "exists": {"type": "boolean"},
                    "is_file": {"type": "boolean"},
                    "is_directory": {"type": "boolean"}
                }
            },
            handler=self._handle_file_exists
        )
        
        # File info tool
        self.tools["filesystem_get_file_info"] = MCPTool(
            name="filesystem_get_file_info",
            description="Get information about a file",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to get info for"}
                },
                "required": ["file_path"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "file_path": {"type": "string"},
                    "size": {"type": "integer"},
                    "modified": {"type": "string"},
                    "created": {"type": "string"},
                    "is_file": {"type": "boolean"},
                    "is_directory": {"type": "boolean"},
                    "permissions": {"type": "string"}
                }
            },
            handler=self._handle_get_file_info
        )
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> MCPResult:
        """Call an MCP tool by name.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            MCPResult with the tool execution result
        """
        if tool_name not in self.tools:
            return MCPResult(
                success=False,
                error=f"Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}"
            )
        
        tool = self.tools[tool_name]
        
        try:
            if self.verbose:
                print(f"🔧 Calling MCP tool: {tool_name}")
                print(f"🔧 Arguments: {arguments}")
            
            # Execute the tool handler
            result = await tool.handler(arguments)
            
            if self.verbose:
                print(f"✅ Tool {tool_name} executed successfully")
            
            return result
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Tool {tool_name} failed: {e}")
            
            return MCPResult(
                success=False,
                error=f"Tool execution failed: {str(e)}"
            )
    
    def list_tools(self) -> List[str]:
        """List available tool names."""
        return list(self.tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Optional[MCPTool]:
        """Get information about a specific tool."""
        return self.tools.get(tool_name)
    
    # Tool handlers
    async def _handle_write_file(self, args: Dict[str, Any]) -> MCPResult:
        """Handle file writing."""
        try:
            file_path = args["file_path"]
            content = args["content"]
            encoding = args.get("encoding", "utf-8")
            
            # Ensure directory exists
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the file
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            # Get file info
            file_info = file_path_obj.stat()
            
            return MCPResult(
                success=True,
                data={
                    "file_path": file_path,
                    "bytes_written": len(content.encode(encoding)),
                    "encoding": encoding
                },
                metadata={
                    "file_size": file_info.st_size,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return MCPResult(
                success=False,
                error=f"File writing failed: {str(e)}"
            )
    
    async def _handle_create_directory(self, args: Dict[str, Any]) -> MCPResult:
        """Handle directory creation."""
        try:
            directory_path = args["directory_path"]
            dir_path_obj = Path(directory_path)
            
            # Check if already exists
            already_exists = dir_path_obj.exists()
            
            # Create directory
            dir_path_obj.mkdir(parents=True, exist_ok=True)
            
            return MCPResult(
                success=True,
                data={
                    "directory_path": directory_path,
                    "created": not already_exists
                }
            )
            
        except Exception as e:
            return MCPResult(
                success=False,
                error=f"Directory creation failed: {str(e)}"
            )
    
    async def _handle_list_directory(self, args: Dict[str, Any]) -> MCPResult:
        """Handle directory listing."""
        try:
            directory_path = args["directory_path"]
            dir_path_obj = Path(directory_path)
            
            if not dir_path_obj.exists():
                return MCPResult(
                    success=False,
                    error=f"Directory does not exist: {directory_path}"
                )
            
            contents = [item.name for item in dir_path_obj.iterdir()]
            
            return MCPResult(
                success=True,
                data={
                    "directory_path": directory_path,
                    "contents": contents,
                    "total_items": len(contents)
                }
            )
            
        except Exception as e:
            return MCPResult(
                success=False,
                error=f"Directory listing failed: {str(e)}"
            )
    
    async def _handle_file_exists(self, args: Dict[str, Any]) -> MCPResult:
        """Handle file existence check."""
        try:
            file_path = args["file_path"]
            path_obj = Path(file_path)
            
            exists = path_obj.exists()
            
            return MCPResult(
                success=True,
                data={
                    "file_path": file_path,
                    "exists": exists,
                    "is_file": path_obj.is_file() if exists else False,
                    "is_directory": path_obj.is_dir() if exists else False
                }
            )
            
        except Exception as e:
            return MCPResult(
                success=False,
                error=f"File existence check failed: {str(e)}"
            )
    
    async def _handle_get_file_info(self, args: Dict[str, Any]) -> MCPResult:
        """Handle file info retrieval."""
        try:
            file_path = args["file_path"]
            path_obj = Path(file_path)
            
            if not path_obj.exists():
                return MCPResult(
                    success=False,
                    error=f"File does not exist: {file_path}"
                )
            
            stat_info = path_obj.stat()
            
            return MCPResult(
                success=True,
                data={
                    "file_path": file_path,
                    "size": stat_info.st_size,
                    "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                    "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                    "is_file": path_obj.is_file(),
                    "is_directory": path_obj.is_dir(),
                    "permissions": oct(stat_info.st_mode)[-3:]
                }
            )
            
        except Exception as e:
            return MCPResult(
                success=False,
                error=f"File info retrieval failed: {str(e)}"
            )
    
    # Convenience methods that use the MCP tools
    async def write_file(self, file_path: str, content: str, encoding: str = "utf-8") -> bool:
        """Write content to a file using MCP tools."""
        result = await self.call_tool("filesystem_write_file", {
            "file_path": file_path,
            "content": content,
            "encoding": encoding
        })
        return result.success
    
    async def create_directory(self, dir_path: str) -> bool:
        """Create a directory using MCP tools."""
        result = await self.call_tool("filesystem_create_directory", {
            "directory_path": dir_path
        })
        return result.success
    
    async def list_directory(self, dir_path: str) -> List[str]:
        """List directory contents using MCP tools."""
        result = await self.call_tool("filesystem_list_directory", {
            "directory_path": dir_path
        })
        if result.success and result.data:
            return result.data.get("contents", [])
        return []
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists using MCP tools."""
        result = await self.call_tool("filesystem_file_exists", {
            "file_path": file_path
        })
        if result.success and result.data:
            return result.data.get("exists", False)
        return False
    
    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file info using MCP tools."""
        result = await self.call_tool("filesystem_get_file_info", {
            "file_path": file_path
        })
        if result.success and result.data:
            return result.data
        return None
    
    async def cleanup(self):
        """Clean up resources (no-op for this implementation)."""
        if self.verbose:
            print("🔧 Hybrid MCP service cleanup completed")


# Convenience function for quick file writing
async def write_file_hybrid_mcp(file_path: str, content: str, verbose: bool = False) -> bool:
    """Quick function to write a file using hybrid MCP service.
    
    Args:
        file_path: Path to the file
        content: Content to write
        verbose: Enable verbose logging
        
    Returns:
        True if successful, False otherwise
    """
    service = HybridMCPService(verbose=verbose)
    try:
        return await service.write_file(file_path, content)
    finally:
        await service.cleanup()
