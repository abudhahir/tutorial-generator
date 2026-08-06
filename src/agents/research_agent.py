"""
Research Agent for gathering information and context for blog generation.
"""

import asyncio
from typing import Dict, List, Any, Optional
try:
    from langchain.schema import BaseMessage
except ImportError:
    try:
        from langchain_core.messages import BaseMessage
    except ImportError:
        from langchain.schema.messages import BaseMessage

from .base_agent import BaseAgent
from ..core.models import BlogRequest


class ResearchAgent(BaseAgent):
    """Agent responsible for researching topics and gathering context for blog generation."""
    
    def __init__(self, **kwargs):
        """Initialize the research agent."""
        super().__init__(
            name="Research Agent",
            description="""You are an expert researcher specializing in technology topics. 
            Your role is to gather comprehensive information about the requested topic, 
            identify key concepts, find relevant examples, and provide context for blog generation.
            
            You excel at:
            - Understanding complex technical concepts
            - Finding relevant examples and use cases
            - Identifying current trends and best practices
            - Gathering authoritative sources and references
            - Providing context for different audience levels""",
            **kwargs
        )
    
    async def process(self, input_data: BlogRequest, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process the blog request and gather research information.
        
        Args:
            input_data: Blog request containing topic and requirements
            context: Additional context information
            
        Returns:
            Research results including key concepts, examples, and references
        """
        # Create research prompt
        research_prompt = self._create_research_prompt(input_data)
        
        # Generate research content
        research_content = await self.generate_response(research_prompt, context)
        
        # Parse and structure the research results
        research_results = self._parse_research_results(research_content, input_data)
        
        return research_results
    
    def _create_research_prompt(self, blog_request: BlogRequest) -> str:
        """Create a comprehensive research prompt based on the blog request.
        
        Args:
            blog_request: The blog generation request
            
        Returns:
            Formatted research prompt
        """
        prompt = f"""Please research the following topic for a blog post:

TOPIC: {blog_request.topic}
BLOG TYPE: {blog_request.blog_type.value}
TARGET AUDIENCE: {blog_request.target_audience}
TONE: {blog_request.tone}
LENGTH: {blog_request.length}

GOALS TO ACHIEVE:
{chr(10).join(f"- {goal}" for goal in blog_request.goals)}

Please provide comprehensive research including:

1. KEY CONCEPTS: Define and explain the main concepts related to this topic
2. CURRENT STATE: What's the current state of this technology/concept?
3. BEST PRACTICES: What are the established best practices?
4. EXAMPLES: Provide concrete examples and use cases
5. TRENDS: What are the emerging trends and future directions?
6. CHALLENGES: What are common challenges and how to overcome them?
7. REFERENCES: Suggest authoritative sources, documentation, and further reading
8. AUDIENCE CONTEXT: How should this be presented for {blog_request.target_audience}?

Format your response in a structured way that can be easily used for blog generation.
Be thorough but focused on practical, actionable information."""
        
        if blog_request.custom_instructions:
            prompt += f"\n\nADDITIONAL INSTRUCTIONS: {blog_request.custom_instructions}"
        
        return prompt
    
    def _parse_research_results(self, research_content: str, blog_request: BlogRequest) -> Dict[str, Any]:
        """Parse the research content into structured results.
        
        Args:
            research_content: Raw research content from LLM
            blog_request: Original blog request
            
        Returns:
            Structured research results
        """
        # For now, return the raw content with some basic structure
        # In a production system, you might want to use more sophisticated parsing
        return {
            "topic": blog_request.topic,
            "blog_type": blog_request.blog_type,
            "goals": blog_request.goals,  # Add goals to research results
            "research_content": research_content,
            "key_concepts": self._extract_key_concepts(research_content),
            "examples": self._extract_examples(research_content),
            "references": self._extract_references(research_content),
            "challenges": self._extract_challenges(research_content),
            "best_practices": self._extract_best_practices(research_content),
            "audience_context": {
                "target_audience": blog_request.target_audience,
                "tone": blog_request.tone,
                "length": blog_request.length
            }
        }
    
    def _extract_key_concepts(self, content: str) -> List[str]:
        """Extract key concepts from research content."""
        # Simple extraction - in production, use more sophisticated NLP
        concepts = []
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith(('KEY CONCEPTS:', 'CONCEPTS:', '- ')):
                if '- ' in line:
                    concepts.append(line.split('- ', 1)[1].strip())
                elif ':' in line:
                    # Extract concepts from subsequent lines
                    continue
        return concepts[:5]  # Limit to top 5 concepts
    
    def _extract_examples(self, content: str) -> List[str]:
        """Extract examples from research content."""
        examples = []
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith(('EXAMPLES:', 'USE CASES:', '- ')):
                if '- ' in line:
                    examples.append(line.split('- ', 1)[1].strip())
        return examples[:3]  # Limit to top 3 examples
    
    def _extract_references(self, content: str) -> List[str]:
        """Extract references from research content."""
        references = []
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith(('REFERENCES:', 'SOURCES:', '- ')):
                if '- ' in line:
                    references.append(line.split('- ', 1)[1].strip())
        return references[:5]  # Limit to top 5 references
    
    def _extract_challenges(self, content: str) -> List[str]:
        """Extract challenges from research content."""
        challenges = []
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith(('CHALLENGES:', 'ISSUES:', '- ')):
                if '- ' in line:
                    challenges.append(line.split('- ', 1)[1].strip())
        return challenges[:3]  # Limit to top 3 challenges
    
    def _extract_best_practices(self, content: str) -> List[str]:
        """Extract best practices from research content."""
        practices = []
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith(('BEST PRACTICES:', 'PRACTICES:', '- ')):
                if '- ' in line:
                    practices.append(line.split('- ', 1)[1].strip())
        return practices[:5]  # Limit to top 5 practices
