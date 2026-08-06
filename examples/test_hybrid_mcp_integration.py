#!/usr/bin/env python3
"""
Test script for Hybrid MCP integration in the blog generator.

This script demonstrates how to use the hybrid MCP service that provides
real MCP-like functionality with actual file operations.
"""

import asyncio
import sys
from pathlib import Path
import json

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.hybrid_mcp_service import HybridMCPService, write_file_hybrid_mcp


async def test_hybrid_mcp_service():
    """Test the hybrid MCP service functionality."""
    print("🧪 Testing Hybrid MCP Service Integration")
    print("=" * 50)
    
    # Test 1: Basic hybrid MCP service initialization
    print("\n1️⃣ Testing Hybrid MCP Service Initialization")
    service = HybridMCPService(verbose=True)
    print(f"✅ Hybrid MCP Service initialized with {len(service.tools)} tools")
    
    # Test 2: List available tools
    print("\n2️⃣ Testing Tool Discovery")
    tools = service.list_tools()
    print(f"Available tools: {tools}")
    
    for tool_name in tools:
        tool_info = service.get_tool_info(tool_name)
        print(f"  - {tool_name}: {tool_info.description}")
    
    # Test 3: Directory creation using MCP tools
    print("\n3️⃣ Testing Directory Creation via MCP")
    test_dir = "./test_hybrid_mcp_output"
    success = await service.create_directory(test_dir)
    print(f"Directory creation: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 4: File writing using MCP tools
    print("\n4️⃣ Testing File Writing via MCP")
    test_file = f"{test_dir}/test_blog_hybrid_mcp.md"
    test_content = """# Hybrid MCP Test Blog Post

This is a test blog post generated using the hybrid MCP file service.

## Features
- Real MCP-like interface
- Actual file operations
- Tool schemas and validation
- Easy to extend with real MCP tools

## Code Example
```python
# This is a test code block using hybrid MCP
def hello_hybrid_mcp():
    print("Hello from Hybrid MCP!")
    return "Hybrid MCP is working!"
```
"""
    
    success = await service.write_file(test_file, test_content)
    print(f"File writing: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 5: File existence check using MCP tools
    print("\n5️⃣ Testing File Existence Check via MCP")
    exists = await service.file_exists(test_file)
    print(f"File exists: {'✅ Yes' if exists else '❌ No'}")
    
    # Test 6: File info retrieval using MCP tools
    print("\n6️⃣ Testing File Info Retrieval via MCP")
    file_info = await service.get_file_info(test_file)
    if file_info:
        print(f"File size: {file_info.get('size', 'N/A')} bytes")
        print(f"Modified: {file_info.get('modified', 'N/A')}")
        print(f"Is file: {file_info.get('is_file', 'N/A')}")
        print(f"Permissions: {file_info.get('permissions', 'N/A')}")
    else:
        print("❌ Failed to get file info")
    
    # Test 7: Directory listing using MCP tools
    print("\n7️⃣ Testing Directory Listing via MCP")
    contents = await service.list_directory(test_dir)
    print(f"Directory contents: {contents}")
    
    # Test 8: Direct tool calls
    print("\n8️⃣ Testing Direct MCP Tool Calls")
    
    # Test file writing tool directly
    result = await service.call_tool("filesystem_write_file", {
        "file_path": f"{test_dir}/direct_tool_test.txt",
        "content": "This was written using a direct MCP tool call!",
        "encoding": "utf-8"
    })
    
    print(f"Direct tool call result: {'✅ Success' if result.success else '❌ Failed'}")
    if result.success and result.data:
        print(f"  Bytes written: {result.data.get('bytes_written', 'N/A')}")
        print(f"  Encoding: {result.data.get('encoding', 'N/A')}")
        if result.metadata:
            print(f"  File size: {result.metadata.get('file_size', 'N/A')} bytes")
    
    # Test 9: Multiple file operations
    print("\n9️⃣ Testing Multiple File Operations via MCP")
    files_to_create = [
        (f"{test_dir}/file1.txt", "Content for file 1"),
        (f"{test_dir}/file2.txt", "Content for file 2"),
        (f"{test_dir}/file3.txt", "Content for file 3"),
    ]
    
    for file_path, content in files_to_create:
        success = await service.write_file(file_path, content)
        print(f"Created {file_path}: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 10: Final directory listing
    print("\n🔟 Final Directory Listing via MCP")
    final_contents = await service.list_directory(test_dir)
    print(f"Final directory contents: {final_contents}")
    
    # Test 11: Quick file writing function
    print("\n1️⃣1️⃣ Testing Quick File Writing Function")
    quick_file = f"{test_dir}/quick_test_hybrid_mcp.txt"
    success = await write_file_hybrid_mcp(quick_file, "Quick hybrid MCP test content!", verbose=True)
    print(f"Quick file writing: {'✅ Success' if success else '❌ Failed'}")
    
    # Cleanup
    await service.cleanup()
    
    print("\n" + "=" * 50)
    print("✅ Hybrid MCP Service Test Completed!")
    print(f"📁 Test files created in: {test_dir}")
    print("🔧 Check the test output above for any issues")


async def test_mcp_tool_schemas():
    """Test MCP tool schemas and validation."""
    print("\n🧪 Testing MCP Tool Schemas and Validation")
    print("=" * 50)
    
    service = HybridMCPService(verbose=True)
    
    # Test tool schemas
    print("\n📋 Tool Schema Information:")
    for tool_name in service.list_tools():
        tool = service.get_tool_info(tool_name)
        print(f"\n🔧 {tool.name}:")
        print(f"  Description: {tool.description}")
        print(f"  Input Schema: {json.dumps(tool.input_schema, indent=2)}")
        print(f"  Output Schema: {json.dumps(tool.output_schema, indent=2)}")
    
    # Test invalid tool calls
    print("\n❌ Testing Invalid Tool Calls:")
    
    # Test non-existent tool
    result = await service.call_tool("non_existent_tool", {})
    print(f"Non-existent tool call: {'❌ Failed as expected' if not result.success else '⚠️ Unexpected success'}")
    if not result.success:
        print(f"  Error: {result.error}")
    
    # Test invalid arguments
    result = await service.call_tool("filesystem_write_file", {
        "invalid_arg": "this should fail"
    })
    print(f"Invalid arguments: {'❌ Failed as expected' if not result.success else '⚠️ Unexpected success'}")
    
    await service.cleanup()


async def main():
    """Main test function."""
    print("🚀 Hybrid MCP Integration Test Suite")
    print("Testing hybrid MCP service that provides real MCP-like functionality")
    
    # Test basic hybrid MCP functionality
    await test_hybrid_mcp_service()
    
    # Test MCP tool schemas and validation
    await test_mcp_tool_schemas()
    
    print("\n🎉 All Hybrid MCP tests completed!")
    print("Check the output above for any issues or warnings")


if __name__ == "__main__":
    asyncio.run(main())
