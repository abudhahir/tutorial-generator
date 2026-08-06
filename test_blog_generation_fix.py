#!/usr/bin/env python3
"""
Test script to verify the blog generation fix.
This script tests that the review agent properly returns a tuple and 
the workflow correctly handles it to produce a final blog post.
"""

import asyncio
from src.core.blog_generator import BlogGenerator
from src.core.models import BlogType

async def test_blog_generation():
    """Test blog generation with a simple request."""
    try:
        print("🚀 Starting blog generation test...")
        
        # Create blog generator with verbose mode to see the full process
        generator = BlogGenerator(verbose=True)
        
        # Generate a simple tutorial blog
        result = await generator.generate_tutorial_blog(
            topic="Quick Test - Writing Clean Code",
            goals=["Understand clean code principles", "Apply best practices"],
            difficulty="beginner",
            target_audience="developers",
            tone="friendly",
            length="short",
            include_code_examples=True
        )
        
        # Check the result
        if result.success:
            print("\n✅ SUCCESS: Blog generation completed successfully!")
            print(f"📝 Blog Title: {result.blog_post.title}")
            print(f"📊 Quality Score: {result.blog_post.generation_metadata.get('quality_score', 'N/A')}/10")
            print(f"⏱️  Generation Time: {result.generation_time:.2f} seconds")
            print(f"📄 Blog Type: {result.blog_post.blog_type.value}")
            print(f"📑 Number of Sections: {len(result.blog_post.sections)}")
            
            # Verify that final_blog_post was properly set (not a tuple)
            assert not isinstance(result.blog_post, tuple), "Blog post should not be a tuple!"
            assert hasattr(result.blog_post, 'title'), "Blog post should have a title attribute"
            assert hasattr(result.blog_post, 'sections'), "Blog post should have sections"
            
            print("\n✅ All assertions passed! The fix is working correctly.")
            return True
        else:
            print(f"\n❌ FAILED: Blog generation failed with error: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: Unexpected error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_blog_generation())
    exit(0 if success else 1)