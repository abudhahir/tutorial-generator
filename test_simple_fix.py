#!/usr/bin/env python3
"""
Simple test to verify the tuple unpacking fix in the review agent.
"""

import asyncio
from unittest.mock import MagicMock, AsyncMock
from src.agents.agent_orchestrator import AgentOrchestrator
from src.core.models import BlogPost, BlogSection, BlogType
from datetime import datetime

async def test_review_node_tuple_handling():
    """Test that the review node properly handles tuple from review agent."""
    print("🧪 Testing review node tuple handling...")
    
    # Create a mock orchestrator
    orchestrator = AgentOrchestrator(verbose=True)
    
    # Create a mock blog post
    mock_blog_post = BlogPost(
        title="Test Blog",
        blog_type=BlogType.TUTORIAL,
        sections=[
            BlogSection(
                title="Section 1",
                content="Test content",
                subsections=[],
                code_examples=[]
            )
        ],
        tags=["test"],
        estimated_read_time=5,
        generation_metadata={}
    )
    
    # Mock the review agent to return a tuple
    review_results = {
        "quality_score": 8.5,
        "suggestions": ["Add more examples", "Improve introduction"],
        "final_review": "Good blog post with minor improvements needed"
    }
    
    # Update blog post with review metadata
    reviewed_blog_post = mock_blog_post.model_copy(update={
        "generation_metadata": {
            "quality_score": 8.5,
            "review_completed": True
        }
    })
    
    # Mock the review agent's process method to return a tuple
    orchestrator.review_agent.process = AsyncMock(return_value=(reviewed_blog_post, review_results))
    
    # Create initial state
    state = {
        "blog_post": mock_blog_post,
        "metadata": {}
    }
    
    # Run the review node
    result_state = await orchestrator._review_node(state)
    
    # Verify results
    assert "final_blog_post" in result_state, "final_blog_post should be in state"
    assert "review_results" in result_state, "review_results should be in state"
    assert not isinstance(result_state["final_blog_post"], tuple), "final_blog_post should not be a tuple"
    assert isinstance(result_state["final_blog_post"], BlogPost), "final_blog_post should be a BlogPost object"
    assert result_state["final_blog_post"].title == "Test Blog", "Blog title should be preserved"
    assert result_state["review_results"] == review_results, "Review results should be stored"
    assert result_state["metadata"]["quality_score"] == 8.5, "Quality score should be in metadata"
    
    print("✅ All tests passed!")
    print(f"📝 Final blog post type: {type(result_state['final_blog_post'])}")
    print(f"📊 Quality score: {result_state['metadata'].get('quality_score')}")
    print(f"📋 Review results keys: {list(result_state.get('review_results', {}).keys())}")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_review_node_tuple_handling())
    print("\n🎉 The tuple unpacking fix is working correctly!")
    exit(0 if success else 1)