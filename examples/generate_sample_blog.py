#!/usr/bin/env python3
"""
Example script demonstrating how to use the I'm Poster blog generator.

This script shows how to generate a tech blog post programmatically.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.blog_generator import BlogGenerator


async def generate_sample_blog():
    """Generate a sample tech blog post."""
    print("🚀 I'm Poster - Sample Blog Generation")
    print("=" * 40)
    
    try:
        # Initialize the blog generator
        generator = BlogGenerator()
        
        # Define the blog parameters
        topic = "Building Multi-Agent Systems with LangGraph"
        goals = [
            "Understand the fundamentals of multi-agent systems",
            "Learn how to implement agent communication patterns",
            "Build a practical workflow orchestration system",
            "Explore best practices for agent state management"
        ]
        
        print(f"📝 Topic: {topic}")
        print(f"🎯 Goals: {len(goals)} goals defined")
        print("\n⏳ Generating blog post... (this may take a few minutes)")
        
        # Generate the blog post
        result = await generator.generate_tech_blog(
            topic=topic,
            goals=goals,
            target_audience="developers",
            tone="friendly",
            length="medium",
            include_code_examples=True,
            include_diagrams=True,
            custom_instructions="Focus on practical examples and real-world use cases"
        )
        
        if result.success and result.blog_post:
            print("\n✅ Blog generated successfully!")
            print(f"📊 Quality Score: {result.blog_post.generation_metadata.get('quality_score', 'N/A')}/10")
            print(f"⏱️  Generation Time: {result.generation_time:.2f} seconds")
            
            # Save the blog post
            saved_file = generator.save_blog_to_file(result.blog_post)
            print(f"📁 Saved to: {saved_file}")
            
            # Display blog summary
            print(f"\n📚 Blog Summary:")
            print(f"   Title: {result.blog_post.title}")
            print(f"   Type: {result.blog_post.blog_type.value}")
            print(f"   Sections: {len(result.blog_post.sections)}")
            print(f"   Code Examples: {sum(len(s.code_examples) for s in result.blog_post.sections)}")
            print(f"   Estimated Read Time: {result.blog_post.estimated_read_time} minutes")
            print(f"   Tags: {', '.join(result.blog_post.tags)}")
            
            print(f"\n🎉 Your blog post is ready! Check the file: {saved_file}")
            
        else:
            print(f"\n❌ Blog generation failed!")
            print(f"Error: {result.error_message}")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(generate_sample_blog())
