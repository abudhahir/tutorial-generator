"""
Main Blog Generator class that provides a simple interface for blog generation.
"""

import asyncio
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from datetime import datetime

from .models import BlogRequest, BlogPost, BlogGenerationResult, BlogType
from .config import settings
from ..agents.agent_orchestrator import AgentOrchestrator
from .integrated_mcp_service import IntegratedMCPService, write_file_integrated_mcp


class BlogGenerator:
    """Main interface for generating blog posts using the multi-agent system."""
    
    def __init__(self, verbose: bool = False, use_ollama: bool = False, ollama_base_url: Optional[str] = None, ollama_model: Optional[str] = None, use_lm_studio: bool = False, lm_studio_base_url: Optional[str] = None, lm_studio_model: Optional[str] = None, streaming: bool = True, stream_mode: str = "updates", **kwargs):
        """Initialize the blog generator."""
        self.verbose = verbose
        self.use_ollama = use_ollama
        self.ollama_base_url = ollama_base_url
        self.use_lm_studio = use_lm_studio
        self.lm_studio_base_url = lm_studio_base_url
        self.lm_studio_model = lm_studio_model
        self.streaming = streaming
        self.stream_mode = stream_mode
        
        # Initialize Rich console for beautiful output
        self.console = Console()
        
        if self.verbose:
            self.console.print(Panel(
                "[bold blue]🚀 Initializing Blog Generator...[/bold blue]",
                title="[bold green]System Initialization[/bold green]",
                border_style="blue"
            ))
            if use_ollama:
                self.console.print(Panel(
                    f"[bold yellow]🦙 Using Ollama for local testing[/bold yellow]",
                    title="[bold yellow]Ollama Configuration[/bold yellow]",
                    border_style="yellow"
                ))
            if use_lm_studio:
                self.console.print(Panel(
                    f"[bold blue]🖥️ Using LM Studio for local testing[/bold blue]",
                    title="[bold blue]LM Studio Configuration[/bold blue]",
                    border_style="blue"
                ))
            if streaming:
                self.console.print(Panel(
                    "[bold green]📡 Streaming output enabled[/bold green]\n"
                    "[cyan]Real-time agent thinking and LLM responses will be displayed[/cyan]",
                    title="[bold green]Streaming Mode[/bold green]",
                    border_style="green"
                ))
            
            # Set LangChain environment variables for verbose logging
            if verbose:
                os.environ["LANGCHAIN_VERBOSE"] = "true"
                os.environ["LANGCHAIN_TRACING"] = "false"  # Disable LangSmith tracing
                os.environ["LANGCHAIN_ENDPOINT"] = ""  # Disable LangSmith endpoint
                os.environ["LANGCHAIN_API_KEY"] = ""  # Clear any API key
                os.environ["LANGCHAIN_PROJECT"] = ""  # Disable project tracking
                os.environ["LANGCHAIN_TRACING_V2"] = "false"  # Disable v2 tracing
                os.environ["LANGCHAIN_CALLBACKS"] = ""  # Disable callbacks
                
                # LangSmith is disabled via environment variables above
                
                self.console.print(Panel(
                    "[bold green]🔧 LangChain verbose mode enabled[/bold green]\n"
                    "[yellow]📊 LangSmith tracing disabled[/yellow]",
                    title="[bold green]LangChain Status[/bold green]",
                    border_style="green"
                ))
        
        self.orchestrator = AgentOrchestrator(
            verbose=verbose, 
            use_ollama=use_ollama, 
            ollama_base_url=ollama_base_url,
            ollama_model=ollama_model,
            use_lm_studio=use_lm_studio,
            lm_studio_base_url=lm_studio_base_url,
            lm_studio_model=lm_studio_model,
            streaming=streaming,
            stream_mode=stream_mode,
            **kwargs
        )
        
        # Initialize Integrated MCP file service
        self.integrated_mcp_service = IntegratedMCPService(verbose=verbose)
        
        # Ensure output directories exist
        self._ensure_directories()
        
        if self.verbose:
            self.console.print(Panel(
                "[bold green]✅ Blog Generator initialized successfully[/bold green]",
                title="[bold green]Initialization Complete[/bold green]",
                border_style="green"
            ))
    
    def _ensure_directories(self):
        """Ensure that necessary directories exist."""
        # Create blogs directory
        blogs_dir = Path(settings.blog_output_dir)
        blogs_dir.mkdir(parents=True, exist_ok=True)
        
        # Create templates directory
        templates_dir = Path(settings.template_dir)
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Create data directory for ChromaDB
        data_dir = Path(settings.chroma_persist_directory)
        data_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_tech_blog(
        self,
        topic: str,
        goals: List[str],
        target_audience: str = "developers",
        tone: str = "friendly",
        length: str = "medium",
        include_code_examples: bool = True,
        include_diagrams: bool = False,
        custom_instructions: Optional[str] = None
    ) -> BlogGenerationResult:
        """Generate a tech blog post.
        
        Args:
            topic: Main topic of the blog post
            goals: List of goals to achieve
            target_audience: Target audience for the blog
            tone: Tone of the blog (friendly, professional, humorous)
            length: Length of the blog (short, medium, long)
            include_code_examples: Whether to include code examples
            include_diagrams: Whether to include diagrams
            custom_instructions: Additional custom instructions
            
        Returns:
            Blog generation result
        """
        return await self.orchestrator.generate_tech_blog(
            topic=topic,
            goals=goals,
            target_audience=target_audience,
            tone=tone,
            length=length,
            include_code_examples=include_code_examples,
            include_diagrams=include_diagrams,
            custom_instructions=custom_instructions
        )
    
    async def generate_tutorial_blog(
        self,
        topic: str,
        goals: List[str],
        difficulty: str = "intermediate",
        target_audience: str = "developers",
        tone: str = "friendly",
        length: str = "medium",
        include_code_examples: bool = True,
        custom_instructions: Optional[str] = None
    ) -> BlogGenerationResult:
        """Generate a tutorial blog post.
        
        Args:
            topic: Main topic of the tutorial
            goals: List of learning goals
            difficulty: Difficulty level (beginner, intermediate, advanced)
            target_audience: Target audience
            tone: Tone of the tutorial
            length: Length of the tutorial
            include_code_examples: Whether to include code examples
            custom_instructions: Additional custom instructions
            
        Returns:
            Blog generation result
        """
        return await self.orchestrator.generate_tutorial_blog(
            topic=topic,
            goals=goals,
            difficulty=difficulty,
            target_audience=target_audience,
            tone=tone,
            length=length,
            include_code_examples=include_code_examples,
            custom_instructions=custom_instructions
        )
    
    async def generate_comparison_blog(
        self,
        topic: str,
        items: List[str],
        goals: List[str],
        target_audience: str = "developers",
        tone: str = "friendly",
        length: str = "medium",
        include_code_examples: bool = True,
        custom_instructions: Optional[str] = None
    ) -> BlogGenerationResult:
        """Generate a comparison blog post.
        
        Args:
            topic: Main topic of the comparison
            items: List of items to compare
            goals: List of goals to achieve
            target_audience: Target audience
            tone: Tone of the blog
            length: Length of the blog
            include_code_examples: Whether to include code examples
            custom_instructions: Additional custom instructions
            
        Returns:
            Blog generation result
        """
        # Create custom instructions for comparison
        comparison_instructions = f"Compare and analyze: {', '.join(items)}. "
        if custom_instructions:
            comparison_instructions += custom_instructions
        
        blog_request = BlogRequest(
            topic=topic,
            blog_type=BlogType.COMPARISON,
            goals=goals,
            target_audience=target_audience,
            tone=tone,
            length=length,
            include_code_examples=include_code_examples,
            include_diagrams=False,
            custom_instructions=comparison_instructions
        )
        
        return await self.orchestrator.generate_blog(blog_request)
    
    async def generate_case_study_blog(
        self,
        topic: str,
        goals: List[str],
        target_audience: str = "developers",
        tone: str = "professional",
        length: str = "long",
        include_code_examples: bool = True,
        custom_instructions: Optional[str] = None
    ) -> BlogGenerationResult:
        """Generate a case study blog post.
        
        Args:
            topic: Main topic of the case study
            goals: List of goals to achieve
            target_audience: Target audience
            tone: Tone of the blog
            length: Length of the blog
            include_code_examples: Whether to include code examples
            custom_instructions: Additional custom instructions
            
        Returns:
            Blog generation result
        """
        case_study_instructions = "Present as a detailed case study with real-world examples, challenges, and solutions. "
        if custom_instructions:
            case_study_instructions += custom_instructions
        
        blog_request = BlogRequest(
            topic=topic,
            blog_type=BlogType.CASE_STUDY,
            goals=goals,
            target_audience=target_audience,
            tone=tone,
            length=length,
            include_code_examples=include_code_examples,
            include_diagrams=True,
            custom_instructions=case_study_instructions
        )
        
        return await self.orchestrator.generate_blog(blog_request)
    
    async def generate_blog_from_request(self, blog_request: BlogRequest) -> BlogGenerationResult:
        """Generate a blog post from a custom blog request.
        
        Args:
            blog_request: Custom blog request
            
        Returns:
            Blog generation result
        """
        return await self.orchestrator.generate_blog(blog_request)
    
    def save_blog_to_file(self, blog_post: BlogPost, filename: Optional[str] = None) -> str:
        """Save a blog post to a Markdown file.
        
        Args:
            blog_post: The blog post to save
            filename: Optional filename (if not provided, generates one)
            
        Returns:
            Path to the saved file
        """
        if not filename:
            # Generate filename from title
            safe_title = "".join(c for c in blog_post.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '-').lower()
            filename = f"{safe_title}.md"
        
        # Ensure .md extension
        if not filename.endswith('.md'):
            filename += '.md'
        
        # Create full path
        file_path = Path(settings.blog_output_dir) / filename
        
        # Generate the markdown content
        markdown_content = self._generate_markdown_content(blog_post)
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return str(file_path)
    
    def _generate_markdown_content(self, blog_post: BlogPost) -> str:
        """Generate markdown content from a blog post."""
        lines = []
        
        # Front Matter
        lines.append("---")
        lines.append(f'title: "{blog_post.title}"')
        lines.append(f'date: "{blog_post.created_at.strftime("%Y-%m-%d")}"')
        
        # Generate excerpt from introduction or first section
        excerpt = blog_post.introduction[:200] if blog_post.introduction else "A comprehensive guide covering key concepts and practical examples."
        if len(excerpt) < len(blog_post.introduction):
            excerpt += "..."
        lines.append(f'excerpt: "{excerpt}"')
        
        # Tags
        if blog_post.tags:
            lines.append(f'tags: {blog_post.tags}')
        else:
            # Generate default tags based on blog type and content
            default_tags = [blog_post.blog_type.value.replace('_', ' ').title()]
            if 'python' in blog_post.title.lower():
                default_tags.append("Python")
            if 'javascript' in blog_post.title.lower():
                default_tags.append("JavaScript")
            if 'ai' in blog_post.title.lower() or 'machine learning' in blog_post.title.lower():
                default_tags.append("AI/ML")
            lines.append(f'tags: {default_tags}')
        
        lines.append(f'author: "{blog_post.author}"')
        lines.append(f'featured: true')
        lines.append(f'readTime: "{blog_post.estimated_read_time} min read"')
        lines.append("---")
        
        # Main content starts here
        lines.append("")
        
        # Main Title
        lines.append(f"# {blog_post.title}")
        if blog_post.subtitle:
            lines.append(f"\n{blog_post.subtitle}")
        lines.append("")
        
        # Goals
        lines.append(f"## 🎯 Goals")
        for goal in blog_post.goals:
            lines.append(f"- {goal}")
        
        # Approach
        lines.append(f"\n## 🚀 Approach")
        lines.append(blog_post.approach)
        
        # Topic Breakup
        lines.append(f"\n## 📚 What We'll Cover")
        for topic in blog_post.topic_breakup:
            lines.append(f"- {topic}")
        
        # Introduction
        lines.append(f"\n## 📖 Introduction")
        lines.append(blog_post.introduction)
        
        # Main Content Sections
        for i, section in enumerate(blog_post.sections, 1):
            lines.append(f"\n## {i}. {section.title}")
            lines.append(section.content)
            
            # Code examples
            if section.code_examples:
                for j, example in enumerate(section.code_examples, 1):
                    lines.append(f"\n### Code Example {j}: {example.description}")
                    if example.filename:
                        lines.append(f"**File:** `{example.filename}`")
                    lines.append(f"\n```{example.language}")
                    lines.append(example.code)
                    lines.append("```")
        
        # Wrapup
        lines.append(f"\n## 🔑 Key Takeaways")
        for point in blog_post.wrapup:
            lines.append(f"- {point}")
        
        # Conclusion
        lines.append(f"\n## 🏁 Conclusion")
        lines.append(blog_post.conclusion)
        
        # Next Steps
        lines.append(f"\n## 🚀 Next Steps")
        for step in blog_post.next_steps:
            lines.append(f"- {step}")
        
        # References
        if blog_post.references:
            lines.append(f"\n## 📚 References & Further Reading")
            for ref in blog_post.references:
                title = ref.get('title', 'Unknown')
                url = ref.get('url', '')
                description = ref.get('description', '')
                
                if url:
                    lines.append(f"- [{title}]({url}) - {description}")
                else:
                    lines.append(f"- **{title}** - {description}")
        
        # Generation Metadata
        lines.append(f"\n---")
        lines.append(f"*Generated by I'm Poster AI using {blog_post.model_used}*")
        if blog_post.generation_metadata.get('quality_score'):
            lines.append(f"*Quality Score: {blog_post.generation_metadata['quality_score']}/10*")
        
        return "\n".join(lines)
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the blog generator."""
        return {
            "orchestrator_status": self.orchestrator.get_workflow_status(),
            "output_directory": settings.blog_output_dir,
            "template_directory": settings.template_dir,
            "chroma_host": f"{settings.chroma_host}:{settings.chroma_port}",
            "default_model": settings.default_model
        }
    
    def list_generated_blogs(self) -> List[str]:
        """List all generated blog files."""
        blogs_dir = Path(settings.blog_output_dir)
        if not blogs_dir.exists():
            return []
        
        blog_files = list(blogs_dir.glob("*.md"))
        return [f.name for f in blog_files]
    
    def get_blog_content(self, filename: str) -> Optional[str]:
        """Get the content of a generated blog file.
        
        Args:
            filename: Name of the blog file
            
        Returns:
            Blog content as string, or None if file doesn't exist
        """
        file_path = Path(settings.blog_output_dir) / filename
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
    
    def _create_blog_directory(self, blog_post: BlogPost) -> tuple[Path, str]:
        """Create a blog-specific directory and return the directory path and filename."""
        # Create base output directory
        output_dir = Path(settings.blog_output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create blog-specific subdirectory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c for c in blog_post.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_topic = safe_topic.replace(' ', '_')
        blog_dir_name = f"{safe_topic}_{timestamp}"
        blog_dir = output_dir / blog_dir_name
        blog_dir.mkdir(exist_ok=True)
        
        # Generate filename
        filename = f"{blog_post.title.replace(' ', '_')}.md"
        
        return blog_dir, filename
    
    def _has_code_examples(self, blog_post: BlogPost) -> bool:
        """Check if the blog post has code examples."""
        if not blog_post.sections:
            return False
        return any(len(section.code_examples) > 0 for section in blog_post.sections)
    
    def _save_code_examples(self, blog_post: BlogPost, code_dir: Path):
        """Save code examples to separate files."""
        for section in blog_post.sections:
            if section.code_examples:
                for i, code_example in enumerate(section.code_examples):
                    # Create filename for code example
                    safe_section = "".join(c for c in section.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_section = safe_section.replace(' ', '_')
                    code_filename = f"{safe_section}_example_{i+1}.{code_example.language.lower()}"
                    code_path = code_dir / code_filename
                    
                    # Save code with description header
                    with open(code_path, 'w', encoding='utf-8') as f:
                        f.write(f"# {code_example.description}\n")
                        f.write(f"# Language: {code_example.language}\n")
                        f.write(f"# Section: {section.title}\n\n")
                        f.write(code_example.code)
    
    async def save_blog_to_file_mcp(self, blog_post: BlogPost, filename: Optional[str] = None) -> str:
        """Save a blog post to a Markdown file with proper directory structure using MCP.
        
        Args:
            blog_post: The blog post to save
            filename: Optional filename (if not provided, generates one)
            
        Returns:
            Path to the saved file
        """
        # Initialize Integrated MCP file service
        await self.integrated_mcp_service.initialize()
        
        try:
            # Create blog-specific directory structure
            blog_dir, blog_filename = self._create_blog_directory(blog_post)
            
            # Save the blog post using MCP
            blog_path = blog_dir / blog_filename
            blog_content = self._generate_markdown_content(blog_post)
            
            success = await self.integrated_mcp_service.write_file(str(blog_path), blog_content)
            if not success:
                if self.verbose:
                    self.console.print(f"⚠️ MCP file writing failed, using fallback method")
                # Fallback to standard method
                with open(blog_path, 'w', encoding='utf-8') as f:
                    f.write(blog_content)
            
            # Save code examples to separate files if they exist
            code_examples_path = blog_dir / "code"
            if self._has_code_examples(blog_post):
                await self.integrated_mcp_service.create_directory(str(code_examples_path))
                await self._save_code_examples_mcp(blog_post, code_examples_path)
            
            if self.verbose:
                self.console.print(f"✅ Blog post saved to: {blog_path}")
                if code_examples_path.exists():
                    self.console.print(f"💻 Code examples saved to: {code_examples_path}")
            
            return str(blog_path)
            
        finally:
            await self.integrated_mcp_service.cleanup()
    
    async def _save_code_examples_mcp(self, blog_post: BlogPost, code_dir: Path):
        """Save code examples to separate files using MCP."""
        for section in blog_post.sections:
            if section.code_examples:
                for i, code_example in enumerate(section.code_examples):
                    # Create filename for code example
                    safe_section = "".join(c for c in section.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_section = safe_section.replace(' ', '_')
                    code_filename = f"{safe_section}_example_{i+1}.{code_example.language.lower()}"
                    code_path = code_dir / code_filename
                    
                    # Prepare code content with description header
                    code_content = f"# {code_example.description}\n"
                    code_content += f"# Language: {code_example.language}\n"
                    code_content += f"# Section: {section.title}\n\n"
                    code_content += code_example.code
                    
                    # Save using MCP
                    success = await self.integrated_mcp_service.write_file(str(code_path), code_content)
                    if not success and self.verbose:
                        self.console.print(f"⚠️ Failed to save code example: {code_path}")

