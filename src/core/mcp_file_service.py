"""
MCP (Model Context Protocol) File Writing Service for the blog generator.

This service provides standardized file operations using MCP tools,
making file writing more robust and cross-platform compatible.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Warning: MCP not available, falling back to standard file operations")


class MCPFileService:
    """Service for handling file operations using MCP tools."""
    
    def __init__(self, verbose: bool = False):
        """Initialize the MCP file service.
        
        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.mcp_available = MCP_AVAILABLE
        self.session: Optional[ClientSession] = None
        
        if self.verbose:
            print(f"🔧 MCP File Service initialized - MCP available: {self.mcp_available}")
    
    async def initialize(self):
        """Initialize MCP connection if available."""
        if not self.mcp_available:
            return False
        
        try:
            # Initialize MCP client
            # For now, we'll use a simple approach that can be extended
            if self.verbose:
                print("🔧 Initializing MCP connection...")
            
            # This is a placeholder for actual MCP initialization
            # In a real implementation, you'd connect to an MCP server
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️ MCP initialization failed: {e}")
            self.mcp_available = False
            return False
    
    async def write_file(self, file_path: str, content: str, encoding: str = "utf-8") -> bool:
        """Write content to a file using MCP if available, fallback to standard methods.
        
        Args:
            file_path: Path to the file to write
            content: Content to write to the file
            encoding: File encoding (default: utf-8)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            if self.mcp_available and self.session:
                # Use MCP file writing
                return await self._write_file_mcp(file_path, content, encoding)
            else:
                # Fallback to standard file writing
                return await self._write_file_standard(file_path, content, encoding)
                
        except Exception as e:
            if self.verbose:
                print(f"❌ File writing failed: {e}")
            return False
    
    async def _write_file_mcp(self, file_path: str, content: str, encoding: str) -> bool:
        """Write file using MCP tools."""
        try:
            # This would use actual MCP file writing tools
            # For now, we'll simulate it
            if self.verbose:
                print(f"🔧 Writing file via MCP: {file_path}")
            
            # Placeholder for MCP file writing
            # In a real implementation, you'd call MCP file writing methods
            return await self._write_file_standard(file_path, content, encoding)
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️ MCP file writing failed, falling back to standard: {e}")
            return await self._write_file_standard(file_path, content, encoding)
    
    async def _write_file_standard(self, file_path: str, content: str, encoding: str) -> bool:
        """Write file using standard Python file operations."""
        try:
            if self.verbose:
                print(f"📝 Writing file: {file_path}")
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            if self.verbose:
                print(f"✅ File written successfully: {file_path}")
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Standard file writing failed: {e}")
            return False
    
    async def create_directory(self, dir_path: str) -> bool:
        """Create a directory using MCP if available.
        
        Args:
            dir_path: Path to the directory to create
            
        Returns:
            True if successful, False otherwise
        """
        try:
            dir_path_obj = Path(dir_path)
            dir_path_obj.mkdir(parents=True, exist_ok=True)
            
            if self.verbose:
                print(f"📁 Directory created/verified: {dir_path}")
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Directory creation failed: {e}")
            return False
    
    async def list_directory(self, dir_path: str) -> List[str]:
        """List contents of a directory.
        
        Args:
            dir_path: Path to the directory to list
            
        Returns:
            List of file/directory names
        """
        try:
            dir_path_obj = Path(dir_path)
            if not dir_path_obj.exists():
                return []
            
            contents = [item.name for item in dir_path_obj.iterdir()]
            if self.verbose:
                print(f"📋 Directory contents ({dir_path}): {contents}")
            return contents
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Directory listing failed: {e}")
            return []
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if a file exists.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            exists = Path(file_path).exists()
            if self.verbose:
                print(f"🔍 File exists check ({file_path}): {exists}")
            return exists
            
        except Exception as e:
            if self.verbose:
                print(f"❌ File existence check failed: {e}")
            return False
    
    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information or None if failed
        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return None
            
            stat = file_path_obj.stat()
            info = {
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "is_file": file_path_obj.is_file(),
                "is_dir": file_path_obj.is_dir()
            }
            
            if self.verbose:
                print(f"📊 File info ({file_path}): {info}")
            return info
            
        except Exception as e:
            if self.verbose:
                print(f"❌ File info retrieval failed: {e}")
            return None
    
    async def cleanup(self):
        """Clean up MCP resources."""
        if self.session:
            try:
                await self.session.close()
                if self.verbose:
                    print("🔧 MCP session closed")
            except Exception as e:
                if self.verbose:
                    print(f"⚠️ MCP cleanup failed: {e}")


# Convenience function for quick file writing
async def write_file_mcp(file_path: str, content: str, verbose: bool = False) -> bool:
    """Quick function to write a file using MCP service.
    
    Args:
        file_path: Path to the file
        content: Content to write
        verbose: Enable verbose logging
        
    Returns:
        True if successful, False otherwise
    """
    service = MCPFileService(verbose=verbose)
    await service.initialize()
    try:
        return await service.write_file(file_path, content)
    finally:
        await service.cleanup()
