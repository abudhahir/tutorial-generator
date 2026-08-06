"""
Formatting Agent for ensuring proper Markdown formatting and structure.
"""

from typing import Dict, List, Any, Optional
try:
    from langchain.schema import BaseMessage
except ImportError:
    try:
        from langchain_core.messages import BaseMessage
    except ImportError:
        from langchain.schema.messages import BaseMessage

from .base_agent import BaseAgent
from ..core.models import BlogPost, BlogSection, CodeExample


class FormattingAgent(BaseAgent):
    """Agent responsible for ensuring proper Markdown formatting and structure."""
    
    def __init__(self, **kwargs):
        """Initialize the formatting agent."""
        super().__init__(
            name="Formatting Agent",
            description="""You are an expert in Markdown formatting and content structure. 
            Your role is to ensure that blog posts are properly formatted, well-structured, 
            and follow best practices for readability and presentation.
            
            You excel at:
            - Ensuring consistent Markdown syntax
            - Improving content structure and flow
            - Adding proper headings and subheadings
            - Formatting code blocks correctly
            - Enhancing readability with proper spacing
            - Adding visual elements like lists and emphasis
            - Ensuring accessibility and SEO best practices
            - Creating professional, polished content""",
            **kwargs
        )
    
    async def process(self, input_data: BlogPost, context: Optional[Dict[str, Any]] = None) -> BlogPost:
        """Process the blog post and improve its formatting and structure.
        
        Args:
            input_data: Blog post from the code agent
            context: Additional context information
            
        Returns:
            Blog post with improved formatting and structure
        """
        # Format the introduction
        formatted_introduction = await self._format_introduction(input_data.introduction, input_data)
        
        # Format each section
        formatted_sections = await self._format_sections(input_data.sections, input_data)
        
        # Format the conclusion
        formatted_conclusion = await self._format_conclusion(input_data.conclusion, input_data)
        
        # Format the wrapup and next steps
        formatted_wrapup = await self._format_wrapup(input_data.wrapup, input_data)
        formatted_next_steps = await self._format_next_steps(input_data.next_steps, input_data)
        
        # Format references
        formatted_references = await self._format_references(input_data.references, input_data)
        
        # Create the formatted blog post
        formatted_blog_post = input_data.model_copy(update={
            "introduction": formatted_introduction,
            "sections": formatted_sections,
            "conclusion": formatted_conclusion,
            "wrapup": formatted_wrapup,
            "next_steps": formatted_next_steps,
            "references": formatted_references,
            "generation_metadata": {
                **input_data.generation_metadata,
                "formatting_agent": self.name,
                "formatting_applied": True
            }
        })
        
        return formatted_blog_post
    
    async def _format_introduction(self, introduction: str, blog_post: BlogPost) -> str:
        """Format the introduction section."""
        prompt = f"""Format and improve this blog introduction:

ORIGINAL INTRODUCTION:
{introduction}

BLOG TITLE: {blog_post.title}
BLOG TOPIC: {blog_post.generation_metadata.get('research_data', 'Unknown')}

Please improve the formatting by:
1. Ensuring proper Markdown syntax
2. Adding appropriate headings and structure
3. Improving readability with proper spacing
4. Adding emphasis where appropriate
5. Making it engaging and hook the reader
6. Ensuring it flows well into the main content

Return the formatted introduction in clean Markdown."""
        
        return await self.generate_response(prompt)
    
    async def _format_sections(self, sections: List[BlogSection], blog_post: BlogPost) -> List[BlogSection]:
        """Format all sections of the blog post."""
        formatted_sections = []
        
        for i, section in enumerate(sections):
            # Format the section content
            formatted_content = await self._format_section_content(section, i + 1, blog_post)
            
            # Format code examples in the section
            formatted_code_examples = await self._format_code_examples(section.code_examples, section, blog_post)
            
            # Create formatted section
            formatted_section = section.model_copy(update={
                "content": formatted_content,
                "code_examples": formatted_code_examples
            })
            
            formatted_sections.append(formatted_section)
        
        return formatted_sections
    
    async def _format_section_content(self, section: BlogSection, section_number: int, blog_post: BlogPost) -> str:
        """Format the content of a specific section."""
        prompt = f"""Format and improve this blog section:

SECTION {section_number}: {section.title}
ORIGINAL CONTENT:
{section.content}

BLOG CONTEXT: {blog_post.title}
TARGET AUDIENCE: {blog_post.generation_metadata.get('audience_context', {}).get('target_audience', 'developers')}

Please improve the formatting by:
1. Adding proper section heading with Markdown
2. Ensuring consistent paragraph structure
3. Adding appropriate emphasis and formatting
4. Improving readability with proper spacing
5. Adding subheadings where helpful
6. Ensuring proper list formatting
7. Making it visually appealing and easy to read

Return the formatted section content in clean Markdown."""
        
        return await self.generate_response(prompt)
    
    async def _format_code_examples(self, code_examples: List[CodeExample], section: BlogSection, blog_post: BlogPost) -> List[CodeExample]:
        """Format code examples in a section."""
        formatted_examples = []
        
        for example in code_examples:
            # Format the code description
            formatted_description = await self._format_code_description(example, section, blog_post)
            
            # Create formatted code example
            formatted_example = example.model_copy(update={
                "description": formatted_description
            })
            
            formatted_examples.append(formatted_example)
        
        return formatted_examples
    
    async def _format_code_description(self, code_example: CodeExample, section: BlogSection, blog_post: BlogPost) -> str:
        """Format the description of a code example."""
        prompt = f"""Format and improve this code example description:

CODE EXAMPLE:
Language: {code_example.language}
Filename: {code_example.filename}
Original Description: {code_example.description}

SECTION CONTEXT: {section.title}
BLOG TOPIC: {blog_post.title}

Please improve the description by:
1. Making it clear and concise
2. Explaining what the code does
3. Adding context about when to use it
4. Ensuring proper Markdown formatting
5. Making it helpful for the target audience

Return the formatted description in clean Markdown."""
        
        return await self.generate_response(prompt)
    
    async def _format_conclusion(self, conclusion: str, blog_post: BlogPost) -> str:
        """Format the conclusion section."""
        prompt = f"""Format and improve this blog conclusion:

ORIGINAL CONCLUSION:
{conclusion}

BLOG TITLE: {blog_post.title}
WRAPUP POINTS: {blog_post.wrapup}

Please improve the formatting by:
1. Adding a clear conclusion heading
2. Ensuring proper paragraph structure
3. Adding emphasis to key points
4. Improving readability with proper spacing
5. Making it compelling and actionable
6. Ensuring it ties back to the introduction

Return the formatted conclusion in clean Markdown."""
        
        return await self.generate_response(prompt)
    
    async def _format_wrapup(self, wrapup: List[str], blog_post: BlogPost) -> List[str]:
        """Format the wrapup points."""
        if not wrapup:
            return wrapup
        
        prompt = f"""Format and improve these wrapup points:

ORIGINAL WRAPUP POINTS:
{chr(10).join(f"- {point}" for point in wrapup)}

BLOG TITLE: {blog_post.title}
BLOG TOPIC: {blog_post.generation_metadata.get('research_data', 'Unknown')}

Please improve the formatting by:
1. Making each point clear and actionable
2. Ensuring consistent formatting
3. Adding emphasis where appropriate
4. Making them memorable and impactful
5. Ensuring they summarize the key learnings

Return the formatted wrapup points as a clean list."""
        
        response = await self.generate_response(prompt)
        return self._extract_formatted_points(response)
    
    async def _format_next_steps(self, next_steps: List[str], blog_post: BlogPost) -> List[str]:
        """Format the next steps."""
        if not next_steps:
            return next_steps
        
        prompt = f"""Format and improve these next steps:

ORIGINAL NEXT STEPS:
{chr(10).join(f"- {step}" for step in next_steps)}

BLOG TITLE: {blog_post.title}
TARGET AUDIENCE: {blog_post.generation_metadata.get('audience_context', {}).get('target_audience', 'developers')}

Please improve the formatting by:
1. Making each step practical and actionable
2. Ensuring clear, specific instructions
3. Adding context about why each step matters
4. Making them motivating and achievable
5. Ensuring they build on what was learned

Return the formatted next steps as a clean list."""
        
        response = await self.generate_response(prompt)
        return self._extract_formatted_points(response)
    
    async def _format_references(self, references: List[Dict[str, str]], blog_post: BlogPost) -> List[Dict[str, str]]:
        """Format the references section."""
        if not references:
            return references
        
        prompt = f"""Format and improve these references:

ORIGINAL REFERENCES:
{chr(10).join(f"- {ref.get('title', 'Unknown')}: {ref.get('url', 'No URL')}" for ref in references)}

BLOG TITLE: {blog_post.title}
BLOG TOPIC: {blog_post.generation_metadata.get('research_data', 'Unknown')}

Please improve the references by:
1. Ensuring each reference has a clear title and description
2. Adding context about why each reference is valuable
3. Organizing them logically (e.g., by topic or difficulty)
4. Making them easy to follow up on
5. Ensuring they're authoritative and relevant

Return the formatted references with improved titles and descriptions."""
        
        response = await self.generate_response(prompt)
        return self._parse_formatted_references(response, references)
    
    def _extract_formatted_points(self, response: str) -> List[str]:
        """Extract formatted points from the response."""
        points = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith(('- ', '1.', '2.', '3.', '4.', '5.')):
                if line.startswith('- '):
                    points.append(line.split('- ', 1)[1].strip())
                else:
                    # Handle numbered lists
                    parts = line.split('.', 1)
                    if len(parts) > 1:
                        points.append(parts[1].strip())
        
        return points[:10]  # Limit to 10 points
    
    def _parse_formatted_references(self, response: str, original_references: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Parse formatted references from the response."""
        # For now, return the original references with basic formatting
        # In production, you might want more sophisticated parsing
        formatted_refs = []
        
        for ref in original_references:
            formatted_ref = {
                "title": ref.get("title", "Unknown Reference"),
                "url": ref.get("url", ""),
                "description": ref.get("description", "Additional reading material")
            }
            formatted_refs.append(formatted_ref)
        
        return formatted_refs
