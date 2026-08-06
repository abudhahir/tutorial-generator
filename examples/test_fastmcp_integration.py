#!/usr/bin/env python3
"""
Test script for FastMCP integration in the blog generator.

This script demonstrates how to use the FastMCP file service for real file operations.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.fastmcp_file_service import FastMCPFileService, write_file_fastmcp


async def test_fastmcp_file_service():
    """Test the FastMCP file service functionality."""
    print("🧪 Testing FastMCP File Service Integration")
    print("=" * 50)
    
    # Test 1: Basic FastMCP file service initialization
    print("\n1️⃣ Testing FastMCP File Service Initialization")
    service = FastMCPFileService(verbose=True)
    init_success = await service.initialize()
    print(f"FastMCP initialization: {'✅ Success' if init_success else '❌ Failed'}")
    
    if not init_success:
        print("⚠️ FastMCP not available, will use fallback methods")
    
    # Test 2: Directory creation
    print("\n2️⃣ Testing Directory Creation")
    test_dir = "./test_fastmcp_output"
    success = await service.create_directory(test_dir)
    print(f"Directory creation: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 3: File writing
    print("\n3️⃣ Testing File Writing")
    test_file = f"{test_dir}/test_blog_fastmcp.md"
    test_content = """# FastMCP Test Blog Post

This is a test blog post generated using the FastMCP file service.

## Features
- Real FastMCP integration
- Robust error handling
- Fallback to standard methods
- Cross-platform compatibility

## Code Example
```python
# This is a test code block using FastMCP
def hello_fastmcp():
    print("Hello from FastMCP!")
    return "FastMCP is working!"
```
"""
    
    success = await service.write_file(test_file, test_content)
    print(f"File writing: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 4: File existence check
    print("\n4️⃣ Testing File Existence Check")
    exists = await service.file_exists(test_file)
    print(f"File exists: {'✅ Yes' if exists else '❌ No'}")
    
    # Test 5: File info retrieval
    print("\n5️⃣ Testing File Info Retrieval")
    file_info = await service.get_file_info(test_file)
    if file_info:
        print(f"File size: {file_info.get('size', 'N/A')} bytes")
        print(f"Modified: {file_info.get('modified', 'N/A')}")
        print(f"Is file: {file_info.get('is_file', 'N/A')}")
    else:
        print("❌ Failed to get file info")
    
    # Test 6: Directory listing
    print("\n6️⃣ Testing Directory Listing")
    contents = await service.list_directory(test_dir)
    print(f"Directory contents: {contents}")
    
    # Test 7: Quick file writing function
    print("\n7️⃣ Testing Quick File Writing Function")
    quick_file = f"{test_dir}/quick_test_fastmcp.txt"
    success = await write_file_fastmcp(quick_file, "Quick FastMCP test content!", verbose=True)
    print(f"Quick file writing: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 8: Multiple file operations
    print("\n8️⃣ Testing Multiple File Operations")
    files_to_create = [
        (f"{test_dir}/file1.txt", "Content for file 1"),
        (f"{test_dir}/file2.txt", "Content for file 2"),
        (f"{test_dir}/file3.txt", "Content for file 3"),
    ]
    
    for file_path, content in files_to_create:
        success = await service.write_file(file_path, content)
        print(f"Created {file_path}: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 9: Final directory listing
    print("\n9️⃣ Final Directory Listing")
    final_contents = await service.list_directory(test_dir)
    print(f"Final directory contents: {final_contents}")
    
    # Cleanup
    await service.cleanup()
    
    print("\n" + "=" * 50)
    print("✅ FastMCP File Service Test Completed!")
    print(f"📁 Test files created in: {test_dir}")
    print("🔧 Check the test output above for any issues")


async def test_fastmcp_vs_standard():
    """Compare FastMCP vs standard file operations."""
    print("\n🧪 Testing FastMCP vs Standard File Operations")
    print("=" * 50)
    
    # Create two services
    fastmcp_service = FastMCPFileService(verbose=True)
    await fastmcp_service.initialize()
    
    test_dir = "./test_comparison"
    await fastmcp_service.create_directory(test_dir)
    
    # Test file writing with both methods
    test_file = f"{test_dir}/comparison_test.txt"
    content = "This is a comparison test between FastMCP and standard methods."
    
    print("\n📝 Testing FastMCP file writing...")
    fastmcp_start = asyncio.get_event_loop().time()
    fastmcp_success = await fastmcp_service.write_file(test_file, content)
    fastmcp_time = asyncio.get_event_loop().time() - fastmcp_start
    
    print(f"FastMCP result: {'✅ Success' if fastmcp_success else '❌ Failed'}")
    print(f"FastMCP time: {fastmcp_time:.4f} seconds")
    
    # Test standard method
    print("\n📝 Testing standard file writing...")
    standard_start = asyncio.get_event_loop().time()
    
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        standard_success = True
    except Exception as e:
        standard_success = False
        print(f"Standard method error: {e}")
    
    standard_time = asyncio.get_event_loop().time() - standard_start
    print(f"Standard result: {'✅ Success' if standard_success else '❌ Failed'}")
    print(f"Standard time: {standard_time:.4f} seconds")
    
    # Comparison
    if fastmcp_success and standard_success:
        print(f"\n📊 Performance Comparison:")
        print(f"FastMCP: {fastmcp_time:.4f}s")
        print(f"Standard: {standard_time:.4f}s")
        if fastmcp_time < standard_time:
            print("🚀 FastMCP is faster!")
        elif fastmcp_time > standard_time:
            print("⚡ Standard method is faster")
        else:
            print("⚖️ Both methods are equally fast")
    
    await fastmcp_service.cleanup()


async def main():
    """Main test function."""
    print("🚀 FastMCP Integration Test Suite")
    print("Testing FastMCP integration with the blog generator")
    
    # Test basic FastMCP functionality
    await test_fastmcp_file_service()
    
    # Test FastMCP vs standard comparison
    await test_fastmcp_vs_standard()
    
    print("\n🎉 All FastMCP tests completed!")
    print("Check the output above for any issues or warnings")


if __name__ == "__main__":
    asyncio.run(main())
