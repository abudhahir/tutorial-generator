"""
Data models for the I'm Poster blog generator.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class BlogType(str, Enum):
    """Types of blogs that can be generated."""
    
    TECH_BLOG = "tech_blog"
    TUTORIAL = "tutorial"
    COMPARISON = "comparison"
    CASE_STUDY = "case_study"
    NEWS_ANALYSIS = "news_analysis"
    OPINION = "opinion"


class BlogRequest(BaseModel):
    """Request model for blog generation."""
    
    topic: str = Field(..., description="Main topic of the blog post")
    blog_type: BlogType = Field(..., description="Type of blog to generate")
    goals: List[str] = Field(..., description="List of goals to achieve in the blog")
    target_audience: str = Field("developers", description="Target audience for the blog")
    tone: str = Field("friendly", description="Tone of the blog (friendly, professional, humorous)")
    length: str = Field("medium", description="Length of the blog (short, medium, long)")
    include_code_examples: bool = Field(True, description="Whether to include code examples")
    include_diagrams: bool = Field(False, description="Whether to include diagrams")
    custom_instructions: Optional[str] = Field(None, description="Additional custom instructions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Building Multi-Agent Systems with LangGraph",
                "blog_type": "tech_blog",
                "goals": [
                    "Understand agent communication patterns",
                    "Implement workflow orchestration",
                    "Handle state management in multi-agent systems"
                ],
                "target_audience": "developers",
                "tone": "friendly",
                "length": "medium",
                "include_code_examples": True,
                "include_diagrams": True
            }
        }


class CodeExample(BaseModel):
    """Model for code examples in blog posts."""
    
    language: str = Field(..., description="Programming language")
    code: str = Field(..., description="Code snippet")
    description: str = Field(..., description="Description of what the code does")
    filename: Optional[str] = Field(None, description="Suggested filename for the code")
    inline_comments: bool = Field(True, description="Whether to include inline comments")


class BlogSection(BaseModel):
    """Model for individual sections of a blog post."""
    
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content in Markdown")
    code_examples: List[CodeExample] = Field(default_factory=list, description="Code examples for this section")
    subsections: List["BlogSection"] = Field(default_factory=list, description="Subsections within this section")


class BlogPost(BaseModel):
    """Complete blog post model."""
    
    # Metadata
    title: str = Field(..., description="Blog post title")
    subtitle: Optional[str] = Field(None, description="Blog post subtitle")
    author: str = Field("I'm Poster AI", description="Author of the blog post")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    # Content structure
    goals: List[str] = Field(..., description="Goals of the blog post")
    approach: str = Field(..., description="Overall approach to achieve the goals")
    topic_breakup: List[str] = Field(..., description="Breakdown of topics covered")
    
    # Main content
    introduction: str = Field(..., description="Introduction section")
    sections: List[BlogSection] = Field(..., description="Main content sections")
    wrapup: List[str] = Field(..., description="Summary points")
    conclusion: str = Field(..., description="Conclusion section")
    next_steps: List[str] = Field(..., description="Suggested next steps")
    
    # References and metadata
    references: List[Dict[str, str]] = Field(default_factory=list, description="References and further reading")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    estimated_read_time: int = Field(..., description="Estimated reading time in minutes")
    
    # Generation metadata
    blog_type: BlogType = Field(..., description="Type of blog generated")
    model_used: str = Field(..., description="AI model used for generation")
    generation_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional generation metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Building Multi-Agent Systems with LangGraph",
                "goals": ["Understand agent communication", "Implement workflows"],
                "approach": "Step-by-step guide with practical examples",
                "topic_breakup": ["Agent Basics", "Communication Patterns", "Workflow Orchestration"],
                "introduction": "Multi-agent systems are revolutionizing AI applications...",
                "sections": [],
                "wrapup": ["Key takeaways", "Best practices"],
                "conclusion": "Multi-agent systems offer powerful capabilities...",
                "next_steps": ["Explore advanced patterns", "Build custom agents"],
                "estimated_read_time": 15,
                "blog_type": "tech_blog",
                "model_used": "gpt-4"
            }
        }


class BlogGenerationResult(BaseModel):
    """Result of blog generation process."""
    
    success: bool = Field(..., description="Whether generation was successful")
    blog_post: Optional[BlogPost] = Field(None, description="Generated blog post")
    error_message: Optional[str] = Field(None, description="Error message if generation failed")
    generation_time: float = Field(..., description="Time taken for generation in seconds")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    cost_estimate: Optional[float] = Field(None, description="Estimated cost of generation")


# Update forward references
BlogSection.model_rebuild()
