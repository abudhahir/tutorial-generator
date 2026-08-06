"""
I'm Poster - Multi-Agent Blog Generator

A sophisticated multi-agent AI system that generates high-quality blog posts
in multiple formats with rich Markdown formatting.
"""

__version__ = "0.1.0"
__author__ = "I'm Poster Team"
__email__ = "team@imposter.ai"

# Disable LangSmith by default to prevent API calls
import os
os.environ["LANGCHAIN_TRACING"] = "false"
os.environ["LANGCHAIN_ENDPOINT"] = ""
os.environ["LANGCHAIN_API_KEY"] = ""
os.environ["LANGCHAIN_PROJECT"] = ""
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_CALLBACKS"] = ""

from .core.blog_generator import BlogGenerator
from .core.config import Settings
from .core.models import BlogPost, BlogRequest, BlogType

__all__ = [
    "BlogGenerator",
    "Settings", 
    "BlogPost",
    "BlogRequest",
    "BlogType",
]
