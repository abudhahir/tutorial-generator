"""
Main application entry point for I'm Poster blog generator.
"""

import asyncio
import sys
from pathlib import Path

from .core.blog_generator import BlogGenerator
from .core.config import settings


async def main():
    """Main application function."""
    print("🚀 I'm Poster - Multi-Agent AI Blog Generator")
    print("=" * 50)
    
    try:
        # Show basic info without initializing complex components
        print(f"✅ Application structure loaded")
        print(f"📁 Project directory: {Path.cwd()}")
        print(f"🤖 Python version: {sys.version}")
        
        # Example usage
        print("\n📚 Example Usage:")
        print("1. Generate a tech blog:")
        print("   im-poster generate-tech-blog 'Building Multi-Agent Systems' --goal 'Understand agents' --goal 'Implement workflows'")
        print("\n2. Generate a tutorial:")
        print("   im-poster generate-tutorial 'LangGraph Basics' --goal 'Learn fundamentals' --goal 'Build first workflow'")
        print("\n3. Check status:")
        print("   im-poster status")
        
        print("\n🔧 For more options, use: im-poster --help")
        
    except Exception as e:
        print(f"❌ Error initializing application: {e}")
        print(f"   This might be due to missing API keys or configuration")
        print(f"   Please check your .env file and try again")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
