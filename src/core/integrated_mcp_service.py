"""
Integrated MCP File Service for the blog generator.

This service provides the best of both worlds:
1. Internal MCP server for immediate use
2. External MCP client for production deployments
"""

import asyncio
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

from .mcp_file_server import FileOperationsMCPServer
from .mcp_file_client import MCPFileClient


class IntegratedMCPService:
    """Integrated MCP service that can run internally or connect externally."""
    
    def __init__(self, verbose: bool = False, external_server: Optional[str] = None):
        """Initialize the integrated MCP service.
        
        Args:
            verbose: Enable verbose logging
            external_server: External MCP server specification (if None, uses internal server)
        """
        self.verbose = verbose
        self.external_server = external_server
        self.internal_server: Optional[FileOperationsMCPServer] = None
        self.external_client: Optional[MCPFileClient] = None
        self.mode = "external" if external_server else "internal"
        
        if self.verbose:
            print(f"🔧 Integrated MCP Service initialized in {self.mode} mode")
            if external_server:
                print(f"🔧 External server: {external_server}")
    
    async def initialize(self):
        """Initialize the MCP service."""
        try:
            if self.mode == "external":
                # Connect to external MCP server
                if self.verbose:
                    print("🔧 Connecting to external MCP server...")
                
                self.external_client = MCPFileClient(self.external_server, verbose=self.verbose)
                success = await self.external_client.connect()
                
                if success:
                    if self.verbose:
                        print("✅ Connected to external MCP server")
                    return True
                else:
                    if self.verbose:
                        print("⚠️ Failed to connect to external server, falling back to internal server")
                    self.mode = "internal"
            
            if self.mode == "internal":
                # Create internal MCP server
                if self.verbose:
                    print("🔧 Creating internal MCP server...")
                
                self.internal_server = FileOperationsMCPServer(verbose=self.verbose)
                
                if self.verbose:
                    print("✅ Internal MCP server created")
                return True
                
        except Exception as e:
            if self.verbose:
                print(f"❌ MCP service initialization failed: {e}")
            return False
    
    async def write_file(self, file_path: str, content: str, encoding: str = "utf-8") -> bool:
        """Write content to a file using MCP.
        
        Args:
            file_path: Path to the file
            content: Content to write
            encoding: File encoding
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.mode == "external" and self.external_client:
                # Use external MCP server
                return await self.external_client.write_file(file_path, content, encoding)
            
            elif self.mode == "internal" and self.internal_server:
                # Use internal MCP server
                tool = await self.internal_server.mcp.get_tool("file_create")
                result = await tool.run({
                    "file_path": file_path,
                    "content": content,
                    "encoding": encoding,
                    "overwrite": True
                })
                # Handle FastMCP ToolResult object
                if hasattr(result, 'structured_content'):
                    return result.structured_content.get("success", False)
                elif hasattr(result, 'content') and result.content:
                    # Parse content from TextContent objects
                    import json
                    try:
                        text_content = result.content[0].text
                        data = json.loads(text_content)
                        return data.get("success", False)
                    except:
                        return False
                else:
                    return bool(result)
            
            else:
                if self.verbose:
                    print("❌ No MCP service available")
                return False
                
        except Exception as e:
            if self.verbose:
                print(f"❌ File writing failed: {e}")
            return False
    
    async def create_directory(self, dir_path: str) -> bool:
        """Create a directory using MCP.
        
        Args:
            dir_path: Path of the directory to create
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.mode == "external" and self.external_client:
                # Use external MCP server
                return await self.external_client.create_directory(dir_path)
            
            elif self.mode == "internal" and self.internal_server:
                # Use internal MCP server
                tool = await self.internal_server.mcp.get_tool("folder_create")
                result = await tool.run({
                    "folder_path": dir_path,
                    "parents": True,
                    "exist_ok": True
                })
                # Handle FastMCP ToolResult object
                if hasattr(result, 'structured_content'):
                    return result.structured_content.get("success", False)
                elif hasattr(result, 'content') and result.content:
                    # Parse content from TextContent objects
                    import json
                    try:
                        text_content = result.content[0].text
                        data = json.loads(text_content)
                        return data.get("success", False)
                    except:
                        return False
                else:
                    return bool(result)
            
            else:
                if self.verbose:
                    print("❌ No MCP service available")
                return False
                
        except Exception as e:
            if self.verbose:
                print(f"❌ Directory creation failed: {e}")
            return False
    
    async def list_directory(self, dir_path: str) -> List[str]:
        """List contents of a directory using MCP.
        
        Args:
            dir_path: Path of the directory to list
            
        Returns:
            List of file/directory names
        """
        try:
            if self.mode == "external" and self.external_client:
                # Use external MCP server
                return await self.external_client.list_directory(dir_path)
            
            elif self.mode == "internal" and self.internal_server:
                # Use internal MCP server
                tool = await self.internal_server.mcp.get_tool("folder_contents")
                result = await tool.run({
                    "folder_path": dir_path,
                    "include_hidden": False
                })
                # Handle FastMCP ToolResult object
                if hasattr(result, 'structured_content'):
                    data = result.structured_content
                elif hasattr(result, 'content') and result.content:
                    # Parse content from TextContent objects
                    import json
                    try:
                        text_content = result.content[0].text
                        data = json.loads(text_content)
                    except:
                        return []
                else:
                    data = result
                
                if data.get("success", False):
                    contents = data.get("contents", [])
                    return [item["name"] for item in contents]
                return []
            
            else:
                if self.verbose:
                    print("❌ No MCP service available")
                return []
                
        except Exception as e:
            if self.verbose:
                print(f"❌ Directory listing failed: {e}")
            return []
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if a file exists using MCP.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            if self.mode == "external" and self.external_client:
                # Use external MCP server
                return await self.external_client.file_exists(file_path)
            
            elif self.mode == "internal" and self.internal_server:
                # Use internal MCP server
                tool = await self.internal_server.mcp.get_tool("file_exists")
                result = await tool.run({
                    "file_path": file_path
                })
                # Handle FastMCP ToolResult object
                if hasattr(result, 'structured_content'):
                    data = result.structured_content
                elif hasattr(result, 'content') and result.content:
                    # Parse content from TextContent objects
                    import json
                    try:
                        text_content = result.content[0].text
                        data = json.loads(text_content)
                    except:
                        return False
                else:
                    data = result
                
                return data.get("exists", False) if data.get("success", False) else False
            
            else:
                if self.verbose:
                    print("❌ No MCP service available")
                return False
                
        except Exception as e:
            if self.verbose:
                print(f"❌ File existence check failed: {e}")
            return False
    
    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a file using MCP.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File information dictionary if successful, None otherwise
        """
        try:
            if self.mode == "external" and self.external_client:
                # Use external MCP server
                return await self.external_client.get_file_info(file_path)
            
            elif self.mode == "internal" and self.internal_server:
                # Use internal MCP server
                tool = await self.internal_server.mcp.get_tool("file_exists")
                result = await tool.run({
                    "file_path": file_path
                })
                # Handle FastMCP ToolResult object
                if hasattr(result, 'structured_content'):
                    data = result.structured_content
                elif hasattr(result, 'content') and result.content:
                    # Parse content from TextContent objects
                    import json
                    try:
                        text_content = result.content[0].text
                        data = json.loads(text_content)
                    except:
                        return None
                else:
                    data = result
                
                if data.get("success", False) and data.get("exists", False):
                    return {
                        "path": data.get("file_path"),
                        "is_file": data.get("is_file"),
                        "is_directory": data.get("is_directory"),
                        "size_bytes": data.get("size_bytes"),
                        "modified": data.get("modified"),
                        "permissions": data.get("permissions")
                    }
                return None
            
            else:
                if self.verbose:
                    print("❌ No MCP service available")
                return None
                
        except Exception as e:
            if self.verbose:
                print(f"❌ File info retrieval failed: {e}")
            return None
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific MCP tool.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Tool execution result
        """
        try:
            if self.mode == "external" and self.external_client:
                # Use external MCP server
                return await self.external_client.call_tool(tool_name, arguments)
            
            elif self.mode == "internal" and self.internal_server:
                # Use internal MCP server
                tool = await self.internal_server.mcp.get_tool(tool_name)
                if tool:
                    result = await tool.run(arguments)
                    # Handle FastMCP ToolResult object
                    if hasattr(result, 'structured_content'):
                        return result.structured_content
                    elif hasattr(result, 'content') and result.content:
                        # Parse content from TextContent objects
                        import json
                        try:
                            text_content = result.content[0].text
                            return json.loads(text_content)
                        except:
                            return {"content": str(result.content)}
                    else:
                        return {"result": str(result)}
                else:
                    return {
                        "success": False,
                        "error": f"Tool '{tool_name}' not found"
                    }
            
            else:
                return {
                    "success": False,
                    "error": "No MCP service available"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}"
            }
    
    def get_available_tools(self) -> List[str]:
        """Get list of available MCP tools.
        
        Returns:
            List of available tool names
        """
        try:
            if self.mode == "external" and self.external_client and self.external_client.connected:
                # For external client, we'd need to cache the tools list
                # For now, return common filesystem tools
                return [
                    "file_create", "file_read", "file_append", "file_delete", "file_move",
                    "folder_create", "folder_contents", "folder_delete", "file_exists"
                ]
            
            elif self.mode == "internal" and self.internal_server:
                # Use internal MCP server
                try:
                    # For now, return the tools we know exist
                    return [
                        "file_create", "file_read", "file_append", "file_delete", "file_move",
                        "folder_create", "folder_contents", "folder_delete", "file_exists",
                        "call_tool_bulk"
                    ]
                except Exception:
                    return []
            
            else:
                return []
                
        except Exception as e:
            if self.verbose:
                print(f"❌ Failed to get available tools: {e}")
            return []
    
    async def cleanup(self):
        """Clean up MCP service resources."""
        try:
            if self.external_client:
                await self.external_client.disconnect()
                if self.verbose:
                    print("🔧 External MCP client disconnected")
            
            # Internal server doesn't need cleanup
            if self.verbose:
                print("🔧 MCP service cleanup completed")
                
        except Exception as e:
            if self.verbose:
                print(f"⚠️ MCP service cleanup failed: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the MCP service.
        
        Returns:
            Dictionary containing service status information
        """
        return {
            "mode": self.mode,
            "external_server": self.external_server,
            "external_client_connected": self.external_client.connected if self.external_client else False,
            "internal_server_available": self.internal_server is not None,
            "available_tools": self.get_available_tools(),
            "verbose": self.verbose
        }


# Convenience functions for quick operations

async def write_file_integrated_mcp(
    file_path: str, 
    content: str, 
    external_server: Optional[str] = None,
    verbose: bool = False
) -> bool:
    """Quick function to write a file using integrated MCP service.
    
    Args:
        file_path: Path to the file
        content: Content to write
        external_server: External MCP server specification (optional)
        verbose: Enable verbose logging
        
    Returns:
        True if successful, False otherwise
    """
    service = IntegratedMCPService(verbose=verbose, external_server=external_server)
    await service.initialize()
    try:
        return await service.write_file(file_path, content)
    finally:
        await service.cleanup()


async def create_directory_integrated_mcp(
    folder_path: str,
    external_server: Optional[str] = None,
    verbose: bool = False
) -> bool:
    """Quick function to create a directory using integrated MCP service.
    
    Args:
        folder_path: Path of the directory to create
        external_server: External MCP server specification (optional)
        verbose: Enable verbose logging
        
    Returns:
        True if successful, False otherwise
    """
    service = IntegratedMCPService(verbose=verbose, external_server=external_server)
    await service.initialize()
    try:
        return await service.create_directory(folder_path)
    finally:
        await service.cleanup()


# Function to start an external MCP server process
def start_external_mcp_server(
    server_script: str = "src/core/mcp_file_server.py",
    host: str = "localhost",
    port: int = 8000,
    verbose: bool = False
) -> subprocess.Popen:
    """Start an external MCP server process.
    
    Args:
        server_script: Path to the server script
        host: Host to bind to
        port: Port to bind to
        verbose: Enable verbose logging
        
    Returns:
        Subprocess process object
    """
    cmd = [
        "python", server_script,
        "--http",
        "--host", host,
        "--port", str(port)
    ]
    
    if verbose:
        cmd.append("--verbose")
    
    if verbose:
        print(f"🚀 Starting external MCP server: {' '.join(cmd)}")
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give the server a moment to start
    import time
    time.sleep(2)
    
    if verbose:
        print(f"🔧 External MCP server started with PID: {process.pid}")
    
    return process


# Function to stop an external MCP server process
def stop_external_mcp_server(process: subprocess.Popen, verbose: bool = False):
    """Stop an external MCP server process.
    
    Args:
        process: Subprocess process object
        verbose: Enable verbose logging
    """
    if verbose:
        print(f"🛑 Stopping external MCP server with PID: {process.pid}")
    
    process.terminate()
    
    try:
        process.wait(timeout=5)
        if verbose:
            print("✅ External MCP server stopped gracefully")
    except subprocess.TimeoutExpired:
        if verbose:
            print("⚠️ External MCP server didn't stop gracefully, forcing...")
        process.kill()
        process.wait()
        if verbose:
            print("✅ External MCP server force stopped")
