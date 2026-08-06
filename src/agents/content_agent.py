"""
Content Agent for generating the main blog content.
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
from ..core.models import BlogRequest, BlogPost, BlogSection


class ContentAgent(BaseAgent):
    """Agent responsible for generating the main blog content based on research."""
    
    def __init__(self, **kwargs):
        """Initialize the content agent."""
        super().__init__(
            name="Content Agent",
            description="""You are an expert content writer specializing in technology blogs. 
            Your role is to create engaging, informative, and well-structured blog content 
            based on research and requirements.
            
            You excel at:
            - Writing clear, engaging introductions
            - Structuring content logically with proper flow
            - Explaining complex concepts in accessible ways
            - Creating compelling conclusions and next steps
            - Maintaining consistent tone and style
            - Writing for different audience levels
            - Creating content that achieves specific goals""",
            **kwargs
        )
    
    async def process(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> BlogPost:
        """Process research data and generate blog content.
        
        Args:
            input_data: Research results from the research agent
            context: Additional context information
            
        Returns:
            Complete blog post with all content sections
        """
        try:
            if self.verbose:
                print(f"🔍 [{self.name}] Processing input data with keys: {list(input_data.keys())}")
                if context:
                    print(f"🔗 Context keys: {list(context.keys())}")
            
            # Extract blog request from research data
            blog_request = context.get("blog_request") if context else None
            
            if self.verbose:
                print(f"📝 [{self.name}] Blog request extracted: {blog_request.topic if blog_request else 'None'}")
            
            # Generate the blog structure
            blog_structure = await self._generate_blog_structure(input_data, blog_request)
            
            if self.verbose:
                print(f"✅ [{self.name}] Blog structure generated with {len(blog_structure.get('topic_breakup', []))} topics")
            
            # Generate each section
            sections = await self._generate_sections(blog_structure, input_data, blog_request)
            
            if self.verbose:
                print(f"✅ [{self.name}] {len(sections)} sections generated")
            
            # Generate introduction and conclusion
            introduction = await self._generate_introduction(blog_structure, input_data, blog_request)
            conclusion = await self._generate_conclusion(blog_structure, input_data, blog_request)
            next_steps = await self._generate_next_steps(blog_structure, input_data, blog_request)
            
            if self.verbose:
                print(f"✅ [{self.name}] Introduction, conclusion, and next steps generated")
            
            # Generate references
            references = await self._generate_references(input_data, blog_request)
            
            if self.verbose:
                print(f"✅ [{self.name}] {len(references)} references generated")
            
            # Create the complete blog post
            blog_post = BlogPost(
                title=blog_structure["title"],
                subtitle=blog_structure.get("subtitle"),
                goals=input_data.get("goals", []),
                approach=blog_structure["approach"],
                topic_breakup=blog_structure["topic_breakup"],
                introduction=introduction,
                sections=sections,
                wrapup=blog_structure["wrapup"],
                conclusion=conclusion,
                next_steps=next_steps,
                references=references,
                tags=blog_structure.get("tags", []),
                estimated_read_time=blog_structure.get("estimated_read_time", 10),
                blog_type=input_data.get("blog_type"),
                model_used=self.model_name,
                generation_metadata={
                    "agent": self.name,
                    "research_data": input_data.get("research_content", "")[:500]  # Truncate for metadata
                }
            )
            
            if self.verbose:
                print(f"✅ [{self.name}] Blog post object created successfully")
            
            return blog_post
            
        except Exception as e:
            if self.verbose:
                print(f"❌ [{self.name}] Error in process method: {str(e)}")
                import traceback
                print(f"🔍 Traceback: {traceback.format_exc()}")
            raise
    
    async def _generate_blog_structure(self, research_data: Dict[str, Any], blog_request: Optional[BlogRequest]) -> Dict[str, Any]:
        """Generate the overall structure and outline for the blog."""
        prompt = f"""Create blog structure for: {research_data.get('topic', 'Unknown Topic')}

GOALS: {blog_request.goals if blog_request else []}

RESEARCH: {research_data.get('research_content', '')[:500]}

Provide the following in EXACT format:

TITLE: "Compelling, descriptive title that captures the topic"
APPROACH: "How we'll approach this topic"
TOPIC BREAKUP:
- Topic 1
- Topic 2
- Topic 3
- Topic 4
WRAPUP:
- Key takeaway 1
- Key takeaway 2
- Key takeaway 3
TAGS: ["tag1", "tag2", "tag3", "tag4", "tag5"]
ESTIMATED READ TIME: 10

IMPORTANT: 
- Start each section with the exact label (TITLE:, APPROACH:, etc.)
- Use quotes around the title
- Use bullet points (-) for lists
- Provide a compelling, descriptive title that reflects the topic"""
        
        response = await self.generate_response(prompt)
        return self._parse_structure_response(response, research_data)
    
    async def _generate_sections(self, structure: Dict[str, Any], research_data: Dict[str, Any], blog_request: Optional[BlogRequest]) -> List[BlogSection]:
        """Generate content for each section of the blog."""
        sections = []
        
        for i, topic in enumerate(structure.get("topic_breakup", [])):
            if self.verbose:
                print(f"📝 [{self.name}] Generating content for section {i+1}: {topic}")
            
            # Generate section content
            section_content = await self._generate_section_content(topic, i + 1, research_data, blog_request)
            
            # Create section object
            section = BlogSection(
                title=topic,
                content=section_content,
                code_examples=[],  # Will be populated by code agent
                subsections=[]
            )
            
            sections.append(section)
            
            if self.verbose:
                print(f"✅ [{self.name}] Section {i+1} completed: {len(section_content)} characters")
        
        if self.verbose:
            print(f"📊 [{self.name}] Total sections generated: {len(sections)}")
        
        return sections
    
    async def _generate_section_content(self, topic: str, section_number: int, research_data: Dict[str, Any], blog_request: Optional[BlogRequest]) -> str:
        """Generate content for a specific section."""
        prompt = f"""Write content for Section {section_number}: {topic}

This is part of a blog about: {research_data.get('topic', 'Unknown Topic')}

RESEARCH CONTEXT:
{research_data.get('research_content', '')[:800]}

AUDIENCE: {research_data.get('audience_context', {}).get('target_control', 'developers')}
TONE: {research_data.get('audience_context', {}).get('tone', 'friendly')}

Please write COMPLETE, WELL-STRUCTURED content that includes:
- Engaging introduction to the topic
- Clear explanations with practical examples
- Code snippets where relevant (use markdown code blocks)
- Practical insights and actionable tips
- Smooth transition to the next section

Write in a conversational, engaging style with the specified tone.
Use proper markdown formatting for structure.
Make it comprehensive and actionable.
Focus on providing real value to the reader.

IMPORTANT: Write complete, finished content. Do not include thinking tags or incomplete sections."""
        
        response = await self.generate_response(prompt)
        
        # Clean the response to remove any artifacts
        if response:
            # Remove thinking tags and other artifacts
            response = response.replace('<think>', '').replace('</think>', '')
            response = response.replace('<|im_start|>', '').replace('<|im_end|>', '')
            response = response.strip()
        
        return response
    
    async def _generate_introduction(self, structure: Dict[str, Any], research_data: Dict[str, Any], blog_request: Optional[BlogRequest]) -> str:
        """Generate the blog introduction."""
        prompt = f"""Write an engaging introduction for this blog post:

TITLE: {structure.get('title', 'Unknown Title')}
TOPIC: {research_data.get('topic', 'Unknown Topic')}
GOALS: {research_data.get('goals', [])}

RESEARCH CONTEXT:
{research_data.get('research_content', '')[:600]}

AUDIENCE: {research_data.get('audience_context', {}).get('target_audience', 'developers')}
TONE: {research_data.get('audience_context', {}).get('tone', 'friendly')}

The introduction should:
- Hook the reader immediately
- Clearly state what they'll learn
- Set expectations for the content
- Be engaging and conversational
- Use the specified tone

Write in markdown format."""
        
        return await self.generate_response(prompt)
    
    async def _generate_conclusion(self, structure: Dict[str, Any], research_data: Dict[str, Any], blog_request: Optional[BlogRequest]) -> str:
        """Generate the blog conclusion."""
        prompt = f"""Write a compelling conclusion for this blog post:

TITLE: {structure.get('title', 'Unknown Title')}
TOPIC: {research_data.get('topic', 'Unknown Topic')}
WRAPUP POINTS: {structure.get('wrapup', [])}

The conclusion should:
- Summarize key points
- Reinforce the main message
- Provide a sense of completion
- Be inspiring and actionable
- Use the specified tone: {research_data.get('audience_context', {}).get('tone', 'friendly')}

Write in markdown format."""
        
        return await self.generate_response(prompt)
    
    async def _generate_next_steps(self, structure: Dict[str, Any], research_data: Dict[str, Any], blog_request: Optional[BlogRequest]) -> List[str]:
        """Generate suggested next steps for readers."""
        prompt = f"""Based on this blog post about {research_data.get('topic', 'Unknown Topic')}, suggest 3-5 next steps for readers.

The next steps should:
- Be practical and actionable
- Build on what they've learned
- Provide clear direction
- Be appropriate for the audience: {research_data.get('audience_context', {}).get('target_audience', 'developers')}

Format as a simple list of actionable items."""
        
        response = await self.generate_response(prompt)
        return self._extract_next_steps(response)
    
    def _parse_structure_response(self, response: str, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the structure response into a structured format."""
        # Simple parsing - in production, use more sophisticated parsing
        structure = {
            "title": "Untitled Blog Post",
            "subtitle": None,
            "approach": "We'll explore this topic step by step",
            "topic_breakup": [],
            "wrapup": [],
            "tags": [],
            "estimated_read_time": 10
        }
        
        # Clean the response first
        response = response.replace('<think>', '').replace('</think>', '')
        response = response.replace('<|im_start|>', '').replace('<|im_end|>', '')
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('TITLE:'):
                title = line.split('TITLE:', 1)[1].strip()
                # Clean up the title - remove quotes and extra formatting
                title = title.strip('"\'')
                structure["title"] = title
            elif line.startswith('SUBTITLE:'):
                subtitle = line.split('SUBTITLE:', 1)[1].strip()
                subtitle = subtitle.strip('"\'')
                structure["subtitle"] = subtitle
            elif line.startswith('APPROACH:'):
                structure["approach"] = line.split('APPROACH:', 1)[1].strip()
            elif line.startswith('TOPIC BREAKUP:'):
                current_section = "topic_breakup"
            elif line.startswith('WRAPUP:'):
                current_section = "wrapup"
            elif line.startswith('TAGS:'):
                current_section = "tags"
            elif line.startswith('ESTIMATED READ TIME:'):
                try:
                    time_str = line.split('ESTIMATED READ TIME:', 1)[1].strip()
                    structure["estimated_read_time"] = int(time_str.split()[0])
                except (ValueError, IndexError):
                    pass
            elif line.startswith('- ') and current_section:
                item = line.split('- ', 1)[1].strip()
                if current_section in structure:
                    structure[current_section].append(item)
            elif line.startswith('* ') and current_section:
                item = line.split('* ', 1)[1].strip()
                if current_section in structure:
                    structure[current_section].append(item)
            elif line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.') or line.startswith('5.'):
                if current_section:
                    item = line.split('.', 1)[1].strip()
                    if current_section in structure:
                        structure[current_section].append(item)
        
        # Fallback: if no topics were parsed, create some basic ones
        if not structure["topic_breakup"]:
            structure["topic_breakup"] = [
                "Introduction and Overview",
                "Core Concepts and Fundamentals", 
                "Practical Examples and Implementation",
                "Best Practices and Tips",
                "Conclusion and Next Steps"
            ]
        
        # Fallback: if no wrapup was parsed, create some basic ones
        if not structure["wrapup"]:
            structure["wrapup"] = [
                "Understanding the fundamentals is key",
                "Practice with real examples",
                "Explore advanced features gradually"
            ]
        
        # Fallback: if no title was parsed or title is still default, use topic
        if not structure["title"] or structure["title"] == "Untitled Blog Post":
            # Try to get topic from research data or generate a descriptive title
            topic = research_data.get('topic', 'Unknown Topic')
            if topic and topic != 'Unknown Topic':
                # Generate a more descriptive title from the topic
                structure["title"] = f"Complete Guide to {topic}"
            else:
                structure["title"] = "Comprehensive Tutorial Guide"
        
        return structure
    
    async def _generate_references(self, research_data: Dict[str, Any], blog_request: Optional[BlogRequest]) -> List[Dict[str, str]]:
        """Generate relevant references and further reading recommendations."""
        prompt = f"""Based on the research data, create a list of relevant references for:

TOPIC: {research_data.get('topic', 'Unknown Topic')}
BLOG TYPE: {research_data.get('blog_type', 'tech_blog')}

RESEARCH SUMMARY:
{research_data.get('research_content', '')[:1000]}

Please provide 3-5 references in this EXACT format:
1. TITLE: "Reference Title"
   URL: "https://example.com/reference"
   DESCRIPTION: "Brief description of what this reference covers"

2. TITLE: "Another Reference"
   URL: "https://example.com/another"
   DESCRIPTION: "Description of this reference"

IMPORTANT: Each reference must have exactly 3 fields: TITLE, URL, and DESCRIPTION.
Format each reference with TITLE, URL, and DESCRIPTION on separate lines.
Do not include any other text or formatting."""
        
        response = await self.generate_response(prompt)
        return self._parse_references_response(response)
    
    def _parse_references_response(self, response: str) -> List[Dict[str, str]]:
        """Parse the references response into proper Reference objects."""
        references = []
        lines = response.split('\n')
        current_ref = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('TITLE:'):
                if current_ref:
                    references.append(current_ref)
                current_ref = {'title': line.split('TITLE:', 1)[1].strip().strip('"')}
            elif line.startswith('URL:'):
                current_ref['url'] = line.split('URL:', 1)[1].strip().strip('"')
            elif line.startswith('DESCRIPTION:'):
                current_ref['description'] = line.split('DESCRIPTION:', 1)[1].strip().strip('"')
        
        # Add the last reference if it exists
        if current_ref and len(current_ref) == 3:
            references.append(current_ref)
        
        # Ensure we have valid references
        if not references:
            # Fallback references
            references = [
                {
                    'title': 'Official Documentation',
                    'url': 'https://docs.example.com',
                    'description': 'Official documentation for further reading'
                }
            ]
        
        return references
    
    def _extract_next_steps(self, response: str) -> List[str]:
        """Extract next steps from the response."""
        steps = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith(('- ', '1.', '2.', '3.', '4.', '5.')):
                if line.startswith('- '):
                    steps.append(line.split('- ', 1)[1].strip())
                else:
                    # Handle numbered lists
                    parts = line.split('.', 1)
                    if len(parts) > 1:
                        steps.append(parts[1].strip())
        
        return steps[:5]  # Limit to 5 steps
