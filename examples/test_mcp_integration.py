#!/usr/bin/env python3
"""
Test script for MCP (Model Context Protocol) integration in the blog generator.

This script demonstrates how to use the MCP file service for enhanced file operations.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.mcp_file_service import MCPFileService, write_file_mcp
from core.mcp_config import get_mcp_config, get_mcp_tools


async def test_mcp_file_service():
    """Test the MCP file service functionality."""
    print("🧪 Testing MCP File Service Integration")
    print("=" * 50)
    
    # Test 1: Basic MCP file service initialization
    print("\n1️⃣ Testing MCP File Service Initialization")
    service = MCPFileService(verbose=True)
    await service.initialize()
    
    # Test 2: Directory creation
    print("\n2️⃣ Testing Directory Creation")
    test_dir = "./test_mcp_output"
    success = await service.create_directory(test_dir)
    print(f"Directory creation: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 3: File writing
    print("\n3️⃣ Testing File Writing")
    test_file = f"{test_dir}/test_blog.md"
    test_content = """# Test Blog Post

This is a test blog post generated using the MCP file service.

## Features
- MCP integration
- Robust error handling
- Fallback to standard methods
- Cross-platform compatibility

## Code Example
```python
# This is a test code block
def hello_mcp():
    print("Hello from MCP!")
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
        print(f"File size: {file_info['size']} bytes")
        print(f"Modified: {file_info['modified']}")
        print(f"Is file: {file_info['is_file']}")
    else:
        print("❌ Failed to get file info")
    
    # Test 6: Directory listing
    print("\n6️⃣ Testing Directory Listing")
    contents = await service.list_directory(test_dir)
    print(f"Directory contents: {contents}")
    
    # Test 7: Quick file writing function
    print("\n7️⃣ Testing Quick File Writing Function")
    quick_file = f"{test_dir}/quick_test.txt"
    success = await write_file_mcp(quick_file, "Quick test content!", verbose=True)
    print(f"Quick file writing: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 8: MCP configuration
    print("\n8️⃣ Testing MCP Configuration")
    config = get_mcp_config()
    print(f"Server type: {config.server_type}")
    print(f"Connection timeout: {config.connection_timeout}s")
    
    tools = get_mcp_tools()
    print(f"Available tools: {len(tools)}")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # Cleanup
    await service.cleanup()
    
    print("\n" + "=" * 50)
    print("✅ MCP File Service Test Completed!")
    print(f"📁 Test files created in: {test_dir}")
    print("🔧 Check the test output above for any issues")


async def test_mcp_integration_with_blog():
    """Test MCP integration with actual blog generation."""
    print("\n🧪 Testing MCP Integration with Blog Generation")
    print("=" * 50)
    
    try:
        from core.blog_generator import BlogGenerator
        
        # Initialize blog generator with MCP
        generator = BlogGenerator(verbose=True)
        
        # Create a simple test blog post
        from core.models import BlogPost, BlogSection, CodeExample
        
        # Create a test section
        test_section = BlogSection(
            title="MCP Integration Test",
            content="This section tests MCP file writing capabilities.",
            code_examples=[
                CodeExample(
                    language="python",
                    code="print('Hello from MCP!')",
                    description="Simple MCP test",
                    filename="mcp_test.py"
                )
            ],
            subsections=[]
        )
        
        # Create a test blog post
        test_blog = BlogPost(
            title="MCP Integration Test Blog",
            subtitle="Testing MCP file operations",
            goals=["Test MCP integration", "Verify file operations"],
            approach="We'll test various MCP file operations",
            topic_breakup=["Introduction", "MCP Testing", "Results"],
            introduction="This blog tests MCP integration.",
            sections=[test_section],
            wrapup=["MCP works!", "File operations successful"],
            conclusion="MCP integration is working well!",
            next_steps=["Extend MCP tools", "Add more features"],
            references=[],
            tags=["mcp", "testing", "integration"],
            estimated_read_time=5,
            blog_type="tech_blog",
            model_used="test",
            generation_metadata={}
        )
        
        # Test MCP save
        print("📝 Testing MCP blog save...")
        saved_path = await generator.save_blog_to_file_mcp(test_blog)
        print(f"✅ Blog saved to: {saved_path}")
        
    except ImportError as e:
        print(f"⚠️ Could not import blog generator: {e}")
        print("This is expected if running outside the main project context")
    except Exception as e:
        print(f"❌ Blog generation test failed: {e}")


async def main():
    """Main test function."""
    print("🚀 MCP Integration Test Suite")
    print("Testing Model Context Protocol integration with the blog generator")
    
    # Test basic MCP functionality
    await test_mcp_file_service()
    
    # Test MCP integration with blog generation
    await test_mcp_integration_with_blog()
    
    print("\n🎉 All tests completed!")
    print("Check the output above for any issues or warnings")


if __name__ == "__main__":
    asyncio.run(main())
