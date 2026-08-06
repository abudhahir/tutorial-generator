"""
File Operations MCP Server for the blog generator.

This server provides comprehensive filesystem operations through the MCP protocol,
allowing the blog generator to use real MCP tools for file management.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import asyncio

from fastmcp import FastMCP


class FileOperationsMCPServer:
    """MCP server providing comprehensive filesystem operations."""
    
    def __init__(self, name: str = "FileOperations", verbose: bool = False):
        """Initialize the file operations MCP server.
        
        Args:
            name: Name of the MCP server
            verbose: Enable verbose logging
        """
        self.name = name
        self.verbose = verbose
        
        # Create the FastMCP server instance
        self.mcp = FastMCP(
            name=name,
            instructions="""
            This MCP server provides comprehensive filesystem operations for file and directory management.
            Use these tools to read, write, create, delete, and manage files and directories.
            All operations are safe and include proper error handling.
            """,
            on_duplicate_tools="error"
        )
        
        # Register all filesystem tools
        self._register_tools()
        
        if self.verbose:
            print(f"🔧 File Operations MCP Server '{name}' initialized with filesystem tools")
    
    def _register_tools(self):
        """Register all filesystem operation tools."""
        
        # File reading operations
        @self.mcp.tool
        def file_read(file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
            """Read the contents of a file.
            
            Args:
                file_path: Path to the file to read
                encoding: File encoding (default: utf-8)
                
            Returns:
                Dictionary containing file content and metadata
            """
            try:
                file_path_obj = Path(file_path)
                
                if not file_path_obj.exists():
                    return {
                        "success": False,
                        "error": f"File does not exist: {file_path}",
                        "file_path": file_path
                    }
                
                if not file_path_obj.is_file():
                    return {
                        "success": False,
                        "error": f"Path is not a file: {file_path}",
                        "file_path": file_path
                    }
                
                # Read file content
                with open(file_path_obj, 'r', encoding=encoding) as f:
                    content = f.read()
                
                # Get file stats
                stat = file_path_obj.stat()
                
                return {
                    "success": True,
                    "file_path": str(file_path_obj),
                    "content": content,
                    "encoding": encoding,
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "permissions": oct(stat.st_mode)[-3:]
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to read file: {str(e)}",
                    "file_path": file_path
                }
        
        # File writing operations
        @self.mcp.tool
        def file_create(file_path: str, content: str, encoding: str = "utf-8", overwrite: bool = False) -> Dict[str, Any]:
            """Create a new file with content.
            
            Args:
                file_path: Path where the file should be created
                content: Content to write to the file
                encoding: File encoding (default: utf-8)
                overwrite: Whether to overwrite existing files (default: False)
                
            Returns:
                Dictionary containing operation result and metadata
            """
            try:
                file_path_obj = Path(file_path)
                
                # Check if file exists and overwrite is not allowed
                if file_path_obj.exists() and not overwrite:
                    return {
                        "success": False,
                        "error": f"File already exists: {file_path}. Use overwrite=True to overwrite.",
                        "file_path": file_path
                    }
                
                # Ensure parent directory exists
                file_path_obj.parent.mkdir(parents=True, exist_ok=True)
                
                # Write file content
                with open(file_path_obj, 'w', encoding=encoding) as f:
                    f.write(content)
                
                # Get file stats
                stat = file_path_obj.stat()
                
                return {
                    "success": True,
                    "file_path": str(file_path_obj),
                    "bytes_written": len(content.encode(encoding)),
                    "encoding": encoding,
                    "overwritten": file_path_obj.exists() and overwrite,
                    "size_bytes": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to create file: {str(e)}",
                    "file_path": file_path
                }
        
        # File appending operations
        @self.mcp.tool
        def file_append(file_path: str, content: str, encoding: str = "utf-8") -> Dict[str, Any]:
            """Append content to an existing file.
            
            Args:
                file_path: Path to the file to append to
                content: Content to append
                encoding: File encoding (default: utf-8)
                
            Returns:
                Dictionary containing operation result and metadata
            """
            try:
                file_path_obj = Path(file_path)
                
                if not file_path_obj.exists():
                    return {
                        "success": False,
                        "error": f"File does not exist: {file_path}",
                        "file_path": file_path
                    }
                
                # Append content
                with open(file_path_obj, 'a', encoding=encoding) as f:
                    f.write(content)
                
                # Get updated file stats
                stat = file_path_obj.stat()
                
                return {
                    "success": True,
                    "file_path": str(file_path_obj),
                    "bytes_appended": len(content.encode(encoding)),
                    "encoding": encoding,
                    "new_size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to append to file: {str(e)}",
                    "file_path": file_path
                }
        
        # File deletion operations
        @self.mcp.tool
        def file_delete(file_path: str) -> Dict[str, Any]:
            """Delete a file.
            
            Args:
                file_path: Path to the file to delete
                
            Returns:
                Dictionary containing operation result
            """
            try:
                file_path_obj = Path(file_path)
                
                if not file_path_obj.exists():
                    return {
                        "success": False,
                        "error": f"File does not exist: {file_path}",
                        "file_path": file_path
                    }
                
                if not file_path_obj.is_file():
                    return {
                        "success": False,
                        "error": f"Path is not a file: {file_path}",
                        "file_path": file_path
                    }
                
                # Get file info before deletion
                stat = file_path_obj.stat()
                file_size = stat.st_size
                
                # Delete the file
                file_path_obj.unlink()
                
                return {
                    "success": True,
                    "file_path": file_path,
                    "deleted": True,
                    "size_bytes": file_size
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to delete file: {str(e)}",
                    "file_path": file_path
                }
        
        # File move operations
        @self.mcp.tool
        def file_move(source_path: str, destination_path: str, overwrite: bool = False) -> Dict[str, Any]:
            """Move a file from source to destination.
            
            Args:
                source_path: Current path of the file
                destination_path: New path for the file
                overwrite: Whether to overwrite existing files (default: False)
                
            Returns:
                Dictionary containing operation result and metadata
            """
            try:
                source_obj = Path(source_path)
                dest_obj = Path(destination_path)
                
                if not source_obj.exists():
                    return {
                        "success": False,
                        "error": f"Source file does not exist: {source_path}",
                        "source_path": source_path,
                        "destination_path": destination_path
                    }
                
                if not source_obj.is_file():
                    return {
                        "success": False,
                        "error": f"Source path is not a file: {source_path}",
                        "source_path": source_path,
                        "destination_path": destination_path
                    }
                
                # Check if destination exists and overwrite is not allowed
                if dest_obj.exists() and not overwrite:
                    return {
                        "success": False,
                        "error": f"Destination file already exists: {destination_path}. Use overwrite=True to overwrite.",
                        "source_path": source_path,
                        "destination_path": destination_path
                    }
                
                # Ensure destination directory exists
                dest_obj.parent.mkdir(parents=True, exist_ok=True)
                
                # Get file info before move
                stat = source_obj.stat()
                file_size = stat.st_size
                
                # Move the file
                shutil.move(str(source_obj), str(dest_obj))
                
                return {
                    "success": True,
                    "source_path": source_path,
                    "destination_path": destination_path,
                    "moved": True,
                    "overwritten": dest_obj.exists() and overwrite,
                    "size_bytes": file_size
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to move file: {str(e)}",
                    "source_path": source_path,
                    "destination_path": destination_path
                }
        
        # Directory creation operations
        @self.mcp.tool
        def folder_create(folder_path: str, parents: bool = True, exist_ok: bool = True) -> Dict[str, Any]:
            """Create a directory.
            
            Args:
                folder_path: Path of the directory to create
                parents: Create parent directories if they don't exist (default: True)
                exist_ok: Don't raise error if directory already exists (default: True)
                
            Returns:
                Dictionary containing operation result and metadata
            """
            try:
                folder_path_obj = Path(folder_path)
                
                # Check if directory already exists
                already_exists = folder_path_obj.exists()
                
                if already_exists and not exist_ok:
                    return {
                        "success": False,
                        "error": f"Directory already exists: {folder_path}",
                        "folder_path": folder_path
                    }
                
                # Create directory
                folder_path_obj.mkdir(parents=parents, exist_ok=exist_ok)
                
                # Get directory info
                stat = folder_path_obj.stat()
                
                return {
                    "success": True,
                    "folder_path": str(folder_path_obj),
                    "created": not already_exists,
                    "parents_created": parents,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "permissions": oct(stat.st_mode)[-3:]
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to create directory: {str(e)}",
                    "folder_path": folder_path
                }
        
        # Directory listing operations
        @self.mcp.tool
        def folder_contents(folder_path: str, include_hidden: bool = False) -> Dict[str, Any]:
            """List contents of a directory.
            
            Args:
                folder_path: Path of the directory to list
                include_hidden: Include hidden files (default: False)
                
            Returns:
                Dictionary containing directory contents and metadata
            """
            try:
                folder_path_obj = Path(folder_path)
                
                if not folder_path_obj.exists():
                    return {
                        "success": False,
                        "error": f"Directory does not exist: {folder_path}",
                        "folder_path": folder_path
                    }
                
                if not folder_path_obj.is_dir():
                    return {
                        "success": False,
                        "error": f"Path is not a directory: {folder_path}",
                        "folder_path": folder_path
                    }
                
                # Get directory contents
                items = []
                for item in folder_path_obj.iterdir():
                    # Skip hidden files if not requested
                    if not include_hidden and item.name.startswith('.'):
                        continue
                    
                    stat = item.stat()
                    items.append({
                        "name": item.name,
                        "path": str(item),
                        "is_file": item.is_file(),
                        "is_directory": item.is_dir(),
                        "size_bytes": stat.st_size if item.is_file() else None,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "permissions": oct(stat.st_mode)[-3:]
                    })
                
                # Sort items: directories first, then files
                items.sort(key=lambda x: (not x["is_directory"], x["name"].lower()))
                
                return {
                    "success": True,
                    "folder_path": str(folder_path_obj),
                    "contents": items,
                    "total_items": len(items),
                    "include_hidden": include_hidden
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to list directory contents: {str(e)}",
                    "folder_path": folder_path
                }
        
        # Directory deletion operations
        @self.mcp.tool
        def folder_delete(folder_path: str, recursive: bool = False) -> Dict[str, Any]:
            """Delete a directory.
            
            Args:
                folder_path: Path of the directory to delete
                recursive: Delete directory and all contents (default: False)
                
            Returns:
                Dictionary containing operation result
            """
            try:
                folder_path_obj = Path(folder_path)
                
                if not folder_path_obj.exists():
                    return {
                        "success": False,
                        "error": f"Directory does not exist: {folder_path}",
                        "folder_path": folder_path
                    }
                
                if not folder_path_obj.is_dir():
                    return {
                        "success": False,
                        "error": f"Path is not a directory: {folder_path}",
                        "folder_path": folder_path
                    }
                
                # Check if directory is empty (when not recursive)
                if not recursive and any(folder_path_obj.iterdir()):
                    return {
                        "success": False,
                        "error": f"Directory is not empty: {folder_path}. Use recursive=True to delete contents.",
                        "folder_path": folder_path
                    }
                
                # Get directory info before deletion
                stat = folder_path_obj.stat()
                
                # Delete directory
                if recursive:
                    shutil.rmtree(folder_path_obj)
                else:
                    folder_path_obj.rmdir()
                
                return {
                    "success": True,
                    "folder_path": folder_path,
                    "deleted": True,
                    "recursive": recursive,
                    "deleted_at": datetime.now().isoformat()
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to delete directory: {str(e)}",
                    "folder_path": folder_path
                }
        
        # File existence check
        @self.mcp.tool
        def file_exists(file_path: str) -> Dict[str, Any]:
            """Check if a file exists.
            
            Args:
                file_path: Path to check
                
            Returns:
                Dictionary containing existence status and metadata
            """
            try:
                path_obj = Path(file_path)
                exists = path_obj.exists()
                
                if exists:
                    stat = path_obj.stat()
                    return {
                        "success": True,
                        "file_path": file_path,
                        "exists": True,
                        "is_file": path_obj.is_file(),
                        "is_directory": path_obj.is_dir(),
                        "size_bytes": stat.st_size if path_obj.is_file() else None,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "permissions": oct(stat.st_mode)[-3:]
                    }
                else:
                    return {
                        "success": True,
                        "file_path": file_path,
                        "exists": False,
                        "is_file": False,
                        "is_directory": False
                    }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to check file existence: {str(e)}",
                    "file_path": file_path
                }
        
        # Bulk operations
        @self.mcp.tool
        def call_tool_bulk(operations: List[Dict[str, Any]]) -> Dict[str, Any]:
            """Execute multiple filesystem operations in bulk.
            
            Args:
                operations: List of operations to execute, each with 'tool' and 'arguments' keys
                
            Returns:
                Dictionary containing results of all operations
            """
            try:
                results = []
                
                for i, operation in enumerate(operations):
                    tool_name = operation.get("tool")
                    arguments = operation.get("arguments", {})
                    
                    if not tool_name:
                        results.append({
                            "index": i,
                            "success": False,
                            "error": "Missing 'tool' key in operation"
                        })
                        continue
                    
                    # Get the tool function
                    tool = self.mcp.get_tool(tool_name)
                    if not tool:
                        results.append({
                            "index": i,
                            "success": False,
                            "error": f"Tool '{tool_name}' not found"
                        })
                        continue
                    
                    try:
                        # Execute the tool
                        result = tool.run(arguments)
                        results.append({
                            "index": i,
                            "tool": tool_name,
                            "success": True,
                            "result": result
                        })
                    except Exception as e:
                        results.append({
                            "index": i,
                            "tool": tool_name,
                            "success": False,
                            "error": str(e)
                        })
                
                return {
                    "success": True,
                    "total_operations": len(operations),
                    "successful_operations": sum(1 for r in results if r.get("success")),
                    "failed_operations": sum(1 for r in results if not r.get("success")),
                    "results": results
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Bulk operation failed: {str(e)}",
                    "total_operations": len(operations) if 'operations' in locals() else 0
                }
    
    def get_server(self) -> FastMCP:
        """Get the FastMCP server instance."""
        return self.mcp
    
    def run(self):
        """Run the MCP server."""
        if self.verbose:
            print(f"🚀 Starting File Operations MCP Server '{self.name}'...")
            print(f"🔧 Available tools: {list(self.mcp.get_tools().keys())}")
        
        self.mcp.run()
    
    def run_async(self, host: str = "localhost", port: int = 8000):
        """Run the MCP server asynchronously with HTTP transport."""
        if self.verbose:
            print(f"🚀 Starting File Operations MCP Server '{self.name}' on {host}:{port}...")
            print(f"🔧 Available tools: {list(self.mcp.get_tools().keys())}")
        
        return self.mcp.run_async(host=host, port=port)


# Convenience function to create and run the server
def create_file_operations_server(name: str = "FileOperations", verbose: bool = False) -> FileOperationsMCPServer:
    """Create a file operations MCP server.
    
    Args:
        name: Name of the MCP server
        verbose: Enable verbose logging
        
    Returns:
        Configured FileOperationsMCPServer instance
    """
    return FileOperationsMCPServer(name=name, verbose=verbose)


# Main entry point for running the server directly
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="File Operations MCP Server")
    parser.add_argument("--name", default="FileOperations", help="Server name")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--host", default="localhost", help="Host for HTTP transport")
    parser.add_argument("--port", type=int, default=8000, help="Port for HTTP transport")
    parser.add_argument("--http", action="store_true", help="Use HTTP transport instead of stdio")
    
    args = parser.parse_args()
    
    server = create_file_operations_server(name=args.name, verbose=args.verbose)
    
    if args.http:
        server.run_async(host=args.host, port=args.port)
    else:
        server.run()
