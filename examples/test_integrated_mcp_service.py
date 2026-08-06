#!/usr/bin/env python3
"""
Test script for Integrated MCP Service in the blog generator.

This script demonstrates the integrated MCP service that can work with
both internal and external MCP servers.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.integrated_mcp_service import (
    IntegratedMCPService, 
    write_file_integrated_mcp,
    create_directory_integrated_mcp,
    start_external_mcp_server,
    stop_external_mcp_server
)


async def test_internal_mcp_service():
    """Test the integrated MCP service in internal mode."""
    print("🧪 Testing Integrated MCP Service (Internal Mode)")
    print("=" * 50)
    
    # Test 1: Basic service initialization
    print("\n1️⃣ Testing Service Initialization")
    service = IntegratedMCPService(verbose=True)
    init_success = await service.initialize()
    print(f"Service initialization: {'✅ Success' if init_success else '❌ Failed'}")
    
    if not init_success:
        print("❌ Cannot proceed with internal mode tests")
        return False
    
    # Test 2: Get service status
    print("\n2️⃣ Testing Service Status")
    status = service.get_status()
    print(f"Service mode: {status['mode']}")
    print(f"Available tools: {status['available_tools']}")
    
    # Test 3: Directory creation
    print("\n3️⃣ Testing Directory Creation")
    test_dir = "./test_integrated_mcp_internal"
    success = await service.create_directory(test_dir)
    print(f"Directory creation: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 4: File writing
    print("\n4️⃣ Testing File Writing")
    test_file = f"{test_dir}/test_blog_internal.md"
    test_content = """# Integrated MCP Test Blog Post (Internal Mode)

This is a test blog post generated using the integrated MCP service in internal mode.

## Features
- Internal MCP server
- Real MCP tools
- Comprehensive filesystem operations
- Production-ready architecture

## Code Example
```python
# This is a test code block using integrated MCP
def hello_integrated_mcp():
    print("Hello from Integrated MCP!")
    return "Integrated MCP is working in internal mode!"
```
"""
    
    success = await service.write_file(test_file, test_content)
    print(f"File writing: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 5: File existence check
    print("\n5️⃣ Testing File Existence Check")
    exists = await service.file_exists(test_file)
    print(f"File exists: {'✅ Yes' if exists else '❌ No'}")
    
    # Test 6: File info retrieval
    print("\n6️⃣ Testing File Info Retrieval")
    file_info = await service.get_file_info(test_file)
    if file_info:
        print(f"File size: {file_info.get('size_bytes', 'N/A')} bytes")
        print(f"Modified: {file_info.get('modified', 'N/A')}")
        print(f"Is file: {file_info.get('is_file', 'N/A')}")
        print(f"Permissions: {file_info.get('permissions', 'N/A')}")
    else:
        print("❌ Failed to get file info")
    
    # Test 7: Directory listing
    print("\n7️⃣ Testing Directory Listing")
    contents = await service.list_directory(test_dir)
    print(f"Directory contents: {contents}")
    
    # Test 8: Direct tool calls
    print("\n8️⃣ Testing Direct MCP Tool Calls")
    result = await service.call_tool("file_read", {
        "file_path": test_file,
        "encoding": "utf-8"
    })
    
    print(f"Direct tool call result: {'✅ Success' if result.get('success') else '❌ Failed'}")
    if result.get("success") and result.get("content"):
        content_preview = result["content"][:100] + "..." if len(result["content"]) > 100 else result["content"]
        print(f"  Content preview: {content_preview}")
    
    # Test 9: Multiple file operations
    print("\n9️⃣ Testing Multiple File Operations")
    files_to_create = [
        (f"{test_dir}/file1.txt", "Content for file 1"),
        (f"{test_dir}/file2.txt", "Content for file 2"),
        (f"{test_dir}/file3.txt", "Content for 3"),
    ]
    
    for file_path, content in files_to_create:
        success = await service.write_file(file_path, content)
        print(f"Created {file_path}: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 10: Final directory listing
    print("\n🔟 Final Directory Listing")
    final_contents = await service.list_directory(test_dir)
    print(f"Final directory contents: {final_contents}")
    
    # Test 11: Quick convenience functions
    print("\n1️⃣1️⃣ Testing Quick Convenience Functions")
    quick_file = f"{test_dir}/quick_test_internal.txt"
    success = await write_file_integrated_mcp(quick_file, "Quick internal MCP test content!")
    print(f"Quick file writing: {'✅ Success' if success else '❌ Failed'}")
    
    # Cleanup
    await service.cleanup()
    
    print("\n" + "=" * 50)
    print("✅ Internal MCP Service Test Completed!")
    print(f"📁 Test files created in: {test_dir}")
    return True


async def test_external_mcp_service():
    """Test the integrated MCP service in external mode."""
    print("\n🧪 Testing Integrated MCP Service (External Mode)")
    print("=" * 50)
    
    # Test 1: Start external MCP server
    print("\n1️⃣ Starting External MCP Server")
    try:
        server_process = start_external_mcp_server(
            server_script="src/core/mcp_file_server.py",
            host="localhost",
            port=8001,  # Use different port to avoid conflicts
            verbose=True
        )
        print(f"✅ External MCP server started with PID: {server_process.pid}")
        
        # Give server time to fully start
        time.sleep(3)
        
    except Exception as e:
        print(f"❌ Failed to start external MCP server: {e}")
        return False
    
    # Test 2: Connect to external server
    print("\n2️⃣ Testing Connection to External Server")
    service = IntegratedMCPService(
        verbose=True, 
        external_server="http://localhost:8001/sse"
    )
    
    init_success = await service.initialize()
    print(f"External server connection: {'✅ Success' if init_success else '❌ Failed'}")
    
    if not init_success:
        print("⚠️ External server connection failed, stopping server...")
        stop_external_mcp_server(server_process, verbose=True)
        return False
    
    # Test 3: Get service status
    print("\n3️⃣ Testing Service Status")
    status = service.get_status()
    print(f"Service mode: {status['mode']}")
    print(f"External server: {status['external_server']}")
    print(f"External client connected: {status['external_client_connected']}")
    print(f"Available tools: {status['available_tools']}")
    
    # Test 4: Directory creation via external server
    print("\n4️⃣ Testing Directory Creation via External Server")
    test_dir = "./test_integrated_mcp_external"
    success = await service.create_directory(test_dir)
    print(f"Directory creation: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 5: File writing via external server
    print("\n5️⃣ Testing File Writing via External Server")
    test_file = f"{test_dir}/test_blog_external.md"
    test_content = """# Integrated MCP Test Blog Post (External Mode)

This is a test blog post generated using the integrated MCP service in external mode.

## Features
- External MCP server
- Real MCP tools over HTTP/SSE
- Network-based filesystem operations
- Production deployment ready

## Code Example
```python
# This is a test code block using external MCP
def hello_external_mcp():
    print("Hello from External MCP!")
    return "External MCP is working over the network!"
```
"""
    
    success = await service.write_file(test_file, test_content)
    print(f"File writing: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 6: File operations via external server
    print("\n6️⃣ Testing File Operations via External Server")
    exists = await service.file_exists(test_file)
    print(f"File exists: {'✅ Yes' if exists else '❌ No'}")
    
    file_info = await service.get_file_info(test_file)
    if file_info:
        print(f"File size: {file_info.get('size_bytes', 'N/A')} bytes")
        print(f"Modified: {file_info.get('modified', 'N/A')}")
    
    # Test 7: Directory listing via external server
    print("\n7️⃣ Testing Directory Listing via External Server")
    contents = await service.list_directory(test_dir)
    print(f"Directory contents: {contents}")
    
    # Test 8: Quick convenience functions with external server
    print("\n8️⃣ Testing Quick Convenience Functions with External Server")
    quick_file = f"{test_dir}/quick_test_external.txt"
    success = await write_file_integrated_mcp(
        quick_file, 
        "Quick external MCP test content!",
        external_server="http://localhost:8001/sse"
    )
    print(f"Quick file writing: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 9: Final directory listing
    print("\n9️⃣ Final Directory Listing via External Server")
    final_contents = await service.list_directory(test_dir)
    print(f"Final directory contents: {final_contents}")
    
    # Cleanup
    await service.cleanup()
    
    # Stop external server
    print("\n🛑 Stopping External MCP Server")
    stop_external_mcp_server(server_process, verbose=True)
    
    print("\n" + "=" * 50)
    print("✅ External MCP Service Test Completed!")
    print(f"📁 Test files created in: {test_dir}")
    return True


async def test_mcp_tool_comparison():
    """Compare internal vs external MCP tool performance."""
    print("\n🧪 Testing MCP Tool Performance Comparison")
    print("=" * 50)
    
    # Test internal mode performance
    print("\n📊 Internal MCP Mode Performance Test")
    internal_service = IntegratedMCPService(verbose=False)
    await internal_service.initialize()
    
    internal_start = time.time()
    for i in range(5):
        test_file = f"./test_performance_internal/file_{i}.txt"
        await internal_service.create_directory("./test_performance_internal")
        await internal_service.write_file(test_file, f"Performance test content {i}")
    
    internal_time = time.time() - internal_start
    print(f"Internal mode: {internal_time:.4f} seconds for 5 operations")
    
    await internal_service.cleanup()
    
    # Test external mode performance (if we can start a server)
    print("\n📊 External MCP Mode Performance Test")
    try:
        server_process = start_external_mcp_server(
            server_script="src/core/mcp_file_server.py",
            host="localhost",
            port=8002,
            verbose=False
        )
        
        time.sleep(3)  # Wait for server to start
        
        external_service = IntegratedMCPService(
            verbose=False,
            external_server="http://localhost:8002/sse"
        )
        
        if await external_service.initialize():
            external_start = time.time()
            for i in range(5):
                test_file = f"./test_performance_external/file_{i}.txt"
                await external_service.create_directory("./test_performance_external")
                await external_service.write_file(test_file, f"Performance test content {i}")
            
            external_time = time.time() - external_start
            print(f"External mode: {external_time:.4f} seconds for 5 operations")
            
            await external_service.cleanup()
        else:
            print("⚠️ External server connection failed")
        
        stop_external_mcp_server(server_process, verbose=False)
        
    except Exception as e:
        print(f"⚠️ External performance test skipped: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Performance Comparison Test Completed!")


async def main():
    """Main test function."""
    print("🚀 Integrated MCP Service Test Suite")
    print("Testing integrated MCP service with internal and external modes")
    
    # Test internal mode
    internal_success = await test_internal_mcp_service()
    
    # Test external mode
    external_success = await test_external_mcp_service()
    
    # Test performance comparison
    await test_mcp_tool_comparison()
    
    print("\n🎉 All Integrated MCP Service tests completed!")
    print("Check the output above for any issues or warnings")
    
    if internal_success and external_success:
        print("✅ All tests passed successfully!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    asyncio.run(main())
