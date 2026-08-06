"""
MCP File Client for the blog generator.

This client connects to the file operations MCP server and provides
a clean interface for filesystem operations.
"""

import asyncio
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

from fastmcp import Client


class MCPFileClient:
    """Client for connecting to the file operations MCP server."""
    
    def __init__(self, server_spec: str, verbose: bool = False):
        """Initialize the MCP file client.
        
        Args:
            server_spec: Server specification (file path, URL, or server instance)
            verbose: Enable verbose logging
        """
        self.server_spec = server_spec
        self.verbose = verbose
        self.client: Optional[Client] = None
        self.connected = False
        
        if self.verbose:
            print(f"🔧 MCP File Client initialized for server: {server_spec}")
    
    async def connect(self):
        """Connect to the MCP server."""
        try:
            if self.verbose:
                print(f"🔧 Connecting to MCP server: {self.server_spec}")
            
            # Create client and connect
            self.client = Client(self.server_spec)
            
            # Test connection by listing tools
            tools = await self.client.list_tools()
            
            if self.verbose:
                print(f"✅ Connected to MCP server with {len(tools)} tools available")
                for tool in tools[:5]:  # Show first 5 tools
                    print(f"  - {tool.name}: {tool.description}")
            
            self.connected = True
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Failed to connect to MCP server: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.client:
            try:
                await self.client.close()
                if self.verbose:
                    print("🔧 Disconnected from MCP server")
            except Exception as e:
                if self.verbose:
                    print(f"⚠️ Error during disconnect: {e}")
            finally:
                self.client = None
                self.connected = False
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Tool execution result
        """
        if not self.connected or not self.client:
            return {
                "success": False,
                "error": "Not connected to MCP server"
            }
        
        try:
            if self.verbose:
                print(f"🔧 Calling MCP tool: {tool_name}")
                print(f"🔧 Arguments: {arguments}")
            
            result = await self.client.call_tool(tool_name, arguments)
            
            if self.verbose:
                print(f"✅ Tool {tool_name} executed successfully")
            
            # Convert result to dictionary format
            if hasattr(result, 'data'):
                return result.data
            elif hasattr(result, 'text'):
                return {"content": result.text}
            else:
                return {"result": str(result)}
                
        except Exception as e:
            if self.verbose:
                print(f"❌ Tool {tool_name} failed: {e}")
            
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}"
            }
    
    # Convenience methods for common filesystem operations
    
    async def write_file(self, file_path: str, content: str, encoding: str = "utf-8", overwrite: bool = False) -> bool:
        """Write content to a file using MCP.
        
        Args:
            file_path: Path to the file
            content: Content to write
            encoding: File encoding
            overwrite: Whether to overwrite existing files
            
        Returns:
            True if successful, False otherwise
        """
        result = await self.call_tool("file_create", {
            "file_path": file_path,
            "content": content,
            "encoding": encoding,
            "overwrite": overwrite
        })
        
        return result.get("success", False)
    
    async def read_file(self, file_path: str, encoding: str = "utf-8") -> Optional[str]:
        """Read content from a file using MCP.
        
        Args:
            file_path: Path to the file
            encoding: File encoding
            
        Returns:
            File content if successful, None otherwise
        """
        result = await self.call_tool("file_read", {
            "file_path": file_path,
            "encoding": encoding
        })
        
        if result.get("success", False):
            return result.get("content")
        return None
    
    async def create_directory(self, folder_path: str, parents: bool = True, exist_ok: bool = True) -> bool:
        """Create a directory using MCP.
        
        Args:
            folder_path: Path of the directory to create
            parents: Create parent directories if they don't exist
            exist_ok: Don't raise error if directory already exists
            
        Returns:
            True if successful, False otherwise
        """
        result = await self.call_tool("folder_create", {
            "folder_path": folder_path,
            "parents": parents,
            "exist_ok": exist_ok
        })
        
        return result.get("success", False)
    
    async def list_directory(self, folder_path: str, include_hidden: bool = False) -> List[str]:
        """List contents of a directory using MCP.
        
        Args:
            folder_path: Path of the directory to list
            include_hidden: Include hidden files
            
        Returns:
            List of file/directory names
        """
        result = await self.call_tool("folder_contents", {
            "folder_path": folder_path,
            "include_hidden": include_hidden
        })
        
        if result.get("success", False):
            contents = result.get("contents", [])
            return [item["name"] for item in contents]
        return []
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if a file exists using MCP.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file exists, False otherwise
        """
        result = await self.call_tool("file_exists", {
            "file_path": file_path
        })
        
        return result.get("exists", False) if result.get("success", False) else False
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file using MCP.
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        result = await self.call_tool("file_delete", {
            "file_path": file_path
        })
        
        return result.get("success", False)
    
    async def move_file(self, source_path: str, destination_path: str, overwrite: bool = False) -> bool:
        """Move a file using MCP.
        
        Args:
            source_path: Current path of the file
            destination_path: New path for the file
            overwrite: Whether to overwrite existing files
            
        Returns:
            True if successful, False otherwise
        """
        result = await self.call_tool("file_move", {
            "source_path": source_path,
            "destination_path": destination_path,
            "overwrite": overwrite
        })
        
        return result.get("success", False)
    
    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a file using MCP.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File information dictionary if successful, None otherwise
        """
        result = await self.call_tool("file_exists", {
            "file_path": file_path
        })
        
        if result.get("success", False) and result.get("exists", False):
            return {
                "path": result.get("file_path"),
                "is_file": result.get("is_file"),
                "is_directory": result.get("is_directory"),
                "size_bytes": result.get("size_bytes"),
                "modified": result.get("modified"),
                "permissions": result.get("permissions")
            }
        return None
    
    async def bulk_operations(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute multiple filesystem operations in bulk using MCP.
        
        Args:
            operations: List of operations to execute
            
        Returns:
            Results of all operations
        """
        result = await self.call_tool("call_tool_bulk", {
            "operations": operations
        })
        
        return result
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


# Convenience function for quick file operations
async def write_file_mcp(server_spec: str, file_path: str, content: str, verbose: bool = False) -> bool:
    """Quick function to write a file using MCP.
    
    Args:
        server_spec: MCP server specification
        file_path: Path to the file
        content: Content to write
        verbose: Enable verbose logging
        
    Returns:
        True if successful, False otherwise
    """
    async with MCPFileClient(server_spec, verbose=verbose) as client:
        return await client.write_file(file_path, content)


async def read_file_mcp(server_spec: str, file_path: str, verbose: bool = False) -> Optional[str]:
    """Quick function to read a file using MCP.
    
    Args:
        server_spec: MCP server specification
        file_path: Path to the file
        verbose: Enable verbose logging
        
    Returns:
        File content if successful, None otherwise
    """
    async with MCPFileClient(server_spec, verbose=verbose) as client:
        return await client.read_file(file_path)


async def create_directory_mcp(server_spec: str, folder_path: str, verbose: bool = False) -> bool:
    """Quick function to create a directory using MCP.
    
    Args:
        server_spec: MCP server specification
        folder_path: Path of the directory to create
        verbose: Enable verbose logging
        
    Returns:
        True if successful, False otherwise
    """
    async with MCPFileClient(server_spec, verbose=verbose) as client:
        return await client.create_directory(folder_path)
