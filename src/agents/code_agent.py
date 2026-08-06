"""
Code Agent for generating code examples and snippets for blog posts.
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


class CodeAgent(BaseAgent):
    """Agent responsible for generating code examples and snippets for blog posts."""
    
    def __init__(self, **kwargs):
        """Initialize the code agent."""
        super().__init__(
            name="Code Agent",
            description="""You are an expert programmer specializing in creating clear, 
            well-commented code examples for educational content. Your role is to generate 
            practical, runnable code snippets that illustrate concepts discussed in blog posts.
            
            You excel at:
            - Writing clean, readable code
            - Adding helpful inline comments
            - Creating practical examples
            - Explaining complex concepts through code
            - Following best practices and conventions
            - Making code accessible to different skill levels
            - Providing context and explanations for code""",
            **kwargs
        )
    
    async def process(self, input_data: BlogPost, context: Optional[Dict[str, Any]] = None) -> BlogPost:
        """Process the blog post and add code examples to relevant sections.
        
        Args:
            input_data: Blog post from the content agent
            context: Additional context information
            
        Returns:
            Blog post with code examples added to sections
        """
        # Analyze the blog content to identify where code examples would be helpful
        sections_with_code = await self._add_code_examples_to_sections(input_data.sections, input_data)
        
        # Create a new blog post with the enhanced sections
        enhanced_blog_post = input_data.model_copy(update={
            "sections": sections_with_code,
            "generation_metadata": {
                **input_data.generation_metadata,
                "code_agent": self.name,
                "code_examples_count": sum(len(section.code_examples) for section in sections_with_code)
            }
        })
        
        return enhanced_blog_post
    
    async def _add_code_examples_to_sections(self, sections: List[BlogSection], blog_post: BlogPost) -> List[BlogSection]:
        """Add code examples to sections where they would be helpful."""
        enhanced_sections = []
        
        for section in sections:
            # Determine if this section needs code examples
            if self._should_include_code_examples(section, blog_post):
                # Generate code examples for this section
                code_examples = await self._generate_code_examples_for_section(section, blog_post)
                
                # Create enhanced section with code examples
                enhanced_section = section.model_copy(update={
                    "code_examples": code_examples
                })
            else:
                enhanced_section = section
            
            enhanced_sections.append(enhanced_section)
        
        return enhanced_sections
    
    def _should_include_code_examples(self, section: BlogSection, blog_post: BlogPost) -> bool:
        """Determine if a section should include code examples."""
        # Check if the blog post is supposed to include code examples
        if not blog_post.generation_metadata.get("include_code_examples", True):
            return False
        
        # Check if the section content suggests code would be helpful
        content_lower = section.content.lower()
        code_indicators = [
            "code", "function", "class", "method", "api", "implementation",
            "example", "snippet", "script", "program", "algorithm",
            "data structure", "database", "query", "configuration",
            "setup", "installation", "deployment", "testing"
        ]
        
        return any(indicator in content_lower for indicator in code_indicators)
    
    async def _generate_code_examples_for_section(self, section: BlogSection, blog_post: BlogPost) -> List[CodeExample]:
        """Generate code examples for a specific section."""
        code_examples = []
        
        # Analyze the section content to determine what kind of code examples would be helpful
        content_analysis = await self._analyze_section_content(section, blog_post)
        
        # Generate code examples based on the analysis
        for code_request in content_analysis.get("code_requests", []):
            code_example = await self._generate_single_code_example(code_request, section, blog_post)
            if code_example:
                code_examples.append(code_example)
        
        return code_examples
    
    async def _analyze_section_content(self, section: BlogSection, blog_post: BlogPost) -> Dict[str, Any]:
        """Analyze section content to determine what code examples would be helpful."""
        prompt = f"""Analyze this blog section content and identify where code examples would be helpful:

SECTION TITLE: {section.title}
SECTION CONTENT:
{section.content[:1000]}

BLOG TOPIC: {blog_post.generation_metadata.get('research_data', 'Unknown')}
TARGET AUDIENCE: {blog_post.generation_metadata.get('audience_context', {}).get('target_audience', 'developers')}

Please identify:
1. What programming concepts are discussed?
2. What code examples would illustrate these concepts?
3. What programming language would be most appropriate?
4. What level of complexity should the examples have?

Format your response as:
CODE REQUESTS:
- Concept: [concept name]
  Language: [programming language]
  Complexity: [beginner/intermediate/advanced]
  Purpose: [what this example demonstrates]
  Description: [brief description of what the code should do]

Be specific about what code examples would be most valuable."""
        
        response = await self.generate_response(prompt)
        return self._parse_content_analysis(response)
    
    async def _generate_single_code_example(self, code_request: Dict[str, str], section: BlogSection, blog_post: BlogPost) -> Optional[CodeExample]:
        """Generate a single code example based on the request."""
        prompt = f"""Create a code example for this blog section:

SECTION: {section.title}
CONCEPT: {code_request.get('concept', 'Unknown')}
LANGUAGE: {code_request.get('language', 'Python')}
COMPLEXITY: {code_request.get('complexity', 'intermediate')}
PURPOSE: {code_request.get('purpose', 'Demonstrate the concept')}
DESCRIPTION: {code_request.get('description', 'Code example')}

BLOG CONTEXT:
{section.content[:500]}

Please create:
1. A practical, runnable code example
2. Clear inline comments explaining key parts
3. A brief description of what the code does
4. A suggested filename for the code

The code should:
- Be well-structured and readable
- Follow best practices for the language
- Include helpful comments
- Be appropriate for {code_request.get('complexity', 'intermediate')} level
- Actually demonstrate the concept being discussed

Format your response as:
CODE:
```[language]
[your code here]
```

DESCRIPTION: [brief description]
FILENAME: [suggested filename]"""
        
        response = await self.generate_response(prompt)
        return self._parse_code_example(response, code_request.get('language', 'Python'))
    
    def _parse_content_analysis(self, response: str) -> Dict[str, Any]:
        """Parse the content analysis response."""
        analysis = {"code_requests": []}
        current_request = {}
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('CODE REQUESTS:'):
                continue
            elif line.startswith('- Concept:'):
                if current_request:
                    analysis["code_requests"].append(current_request)
                current_request = {"concept": line.split('Concept:', 1)[1].strip()}
            elif line.startswith('Language:'):
                current_request["language"] = line.split('Language:', 1)[1].strip()
            elif line.startswith('Complexity:'):
                current_request["complexity"] = line.split('Complexity:', 1)[1].strip()
            elif line.startswith('Purpose:'):
                current_request["purpose"] = line.split('Purpose:', 1)[1].strip()
            elif line.startswith('Description:'):
                current_request["description"] = line.split('Description:', 1)[1].strip()
        
        if current_request:
            analysis["code_requests"].append(current_request)
        
        return analysis
    
    def _parse_code_example(self, response: str, language: str) -> Optional[CodeExample]:
        """Parse the code example response."""
        code_start = response.find('```')
        if code_start == -1:
            return None
        
        # Find the end of the code block
        code_end = response.find('```', code_start + 3)
        if code_end == -1:
            return None
        
        # Extract the code
        code = response[code_start + 3:code_end].strip()
        
        # Extract description and filename
        remaining = response[code_end + 3:].strip()
        description = ""
        filename = f"example.{language.lower()}"
        
        if 'DESCRIPTION:' in remaining:
            desc_parts = remaining.split('DESCRIPTION:', 1)
            description = desc_parts[1].split('FILENAME:', 1)[0].strip()
            
            if 'FILENAME:' in remaining:
                filename = remaining.split('FILENAME:', 1)[1].strip()
        
        return CodeExample(
            language=language,
            code=code,
            description=description or f"Code example for {language}",
            filename=filename,
            inline_comments=True
        )
