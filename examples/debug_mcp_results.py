#!/usr/bin/env python3
"""
Debug script to see what FastMCP tools actually return.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.mcp_file_server import FileOperationsMCPServer


async def debug_mcp_results():
    """Debug what FastMCP tools return."""
    print("🔍 Debugging FastMCP Tool Results")
    print("=" * 40)
    
    # Create server
    server = FileOperationsMCPServer(verbose=True)
    
    # Test file_exists tool
    print("\n1️⃣ Testing file_exists tool")
    tool = await server.mcp.get_tool("file_exists")
    print(f"Tool type: {type(tool)}")
    print(f"Tool: {tool}")
    
    # Test running the tool
    print("\n2️⃣ Running file_exists tool")
    result = await tool.run({"file_path": "nonexistent.txt"})
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
    print(f"Result dir: {dir(result)}")
    
    # Check for common attributes
    print("\n3️⃣ Checking result attributes")
    if hasattr(result, 'data'):
        print(f"✅ Has 'data' attribute: {result.data}")
    else:
        print("❌ No 'data' attribute")
    
    if hasattr(result, 'text'):
        print(f"✅ Has 'text' attribute: {result.text}")
    else:
        print("❌ No 'text' attribute")
    
    if hasattr(result, 'content'):
        print(f"✅ Has 'content' attribute: {result.content}")
    else:
        print("❌ No 'content' attribute")
    
    if hasattr(result, 'success'):
        print(f"✅ Has 'success' attribute: {result.success}")
    else:
        print("❌ No 'success' attribute")
    
    # Try to convert to dict
    print("\n4️⃣ Converting result to dict")
    try:
        if hasattr(result, '__dict__'):
            print(f"✅ Has __dict__: {result.__dict__}")
        else:
            print("❌ No __dict__")
    except Exception as e:
        print(f"❌ Error accessing __dict__: {e}")
    
    # Test folder_contents tool
    print("\n5️⃣ Testing folder_contents tool")
    tool2 = await server.mcp.get_tool("folder_contents")
    result2 = await tool2.run({"folder_path": "."})
    print(f"Folder contents result type: {type(result2)}")
    print(f"Folder contents result: {result2}")
    
    if hasattr(result2, 'data'):
        print(f"✅ Has 'data' attribute: {result2.data}")
    else:
        print("❌ No 'data' attribute")


if __name__ == "__main__":
    asyncio.run(debug_mcp_results())
