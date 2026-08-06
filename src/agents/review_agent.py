"""
Review Agent for quality checks and final review of blog posts.
"""

from typing import Dict, List, Any, Optional, Tuple
try:
    from langchain.schema import BaseMessage
except ImportError:
    try:
        from langchain_core.messages import BaseMessage
    except ImportError:
        from langchain.schema.messages import BaseMessage

from .base_agent import BaseAgent
from ..core.models import BlogPost, BlogSection, CodeExample


class ReviewAgent(BaseAgent):
    """Agent responsible for quality checks and final review of blog posts."""
    
    def __init__(self, **kwargs):
        """Initialize the review agent."""
        super().__init__(
            name="Review Agent",
            description="""You are an expert content reviewer and quality assurance specialist. 
            Your role is to perform comprehensive quality checks on blog posts, ensuring they 
            meet high standards for content, structure, and presentation.
            
            You excel at:
            - Identifying content gaps and inconsistencies
            - Ensuring logical flow and structure
            - Checking for accuracy and completeness
            - Validating code examples and technical content
            - Ensuring proper formatting and readability
            - Providing actionable feedback for improvements
            - Maintaining high quality standards
            - Ensuring content meets the stated goals""",
            **kwargs
        )
    
    async def process(self, input_data: BlogPost, context: Optional[Dict[str, Any]] = None) -> Tuple[BlogPost, Dict[str, Any]]:
        """Process the blog post and perform quality review.
        
        Args:
            input_data: Blog post from the formatting agent
            context: Additional context information including original request
            
        Returns:
            Tuple of (reviewed blog post, review results)
        """
        # Perform comprehensive review
        review_results = await self._perform_comprehensive_review(input_data, context)
        
        # Apply improvements if needed
        improved_blog_post = await self._apply_improvements(input_data, review_results, context)
        
        # Generate final review summary
        final_review = await self._generate_final_review(improved_blog_post, review_results, context)
        
        # Update the blog post with review metadata
        final_blog_post = improved_blog_post.model_copy(update={
            "generation_metadata": {
                **improved_blog_post.generation_metadata,
                "review_agent": self.name,
                "review_results": review_results,
                "final_review": final_review,
                "quality_score": self._calculate_quality_score(review_results)
            }
        })
        
        return final_blog_post, review_results
    
    async def _perform_comprehensive_review(self, blog_post: BlogPost, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform a comprehensive review of the blog post."""
        review_results = {
            "content_quality": {},
            "structure_quality": {},
            "technical_accuracy": {},
            "readability": {},
            "goal_achievement": {},
            "overall_score": 0,
            "issues_found": [],
            "suggestions": []
        }
        
        # Review content quality
        review_results["content_quality"] = await self._review_content_quality(blog_post, context)
        
        # Review structure quality
        review_results["structure_quality"] = await self._review_structure_quality(blog_post, context)
        
        # Review technical accuracy
        review_results["technical_accuracy"] = await self._review_technical_accuracy(blog_post, context)
        
        # Review readability
        review_results["readability"] = await self._review_readability(blog_post, context)
        
        # Review goal achievement
        review_results["goal_achievement"] = await self._review_goal_achievement(blog_post, context)
        
        # Calculate overall score
        review_results["overall_score"] = self._calculate_overall_score(review_results)
        
        return review_results
    
    async def _review_content_quality(self, blog_post: BlogPost, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Review the quality of the blog content."""
        prompt = f"""Review the content quality of this blog post:

TITLE: {blog_post.title}
TOPIC: {blog_post.generation_metadata.get('research_data', 'Unknown')}
GOALS: {blog_post.goals}

INTRODUCTION:
{blog_post.introduction[:500]}

SECTIONS: {len(blog_post.sections)} sections
CONCLUSION: {blog_post.conclusion[:300]}

Please evaluate:

1. CONTENT COMPLETENESS: Does the content cover all necessary aspects?
2. ACCURACY: Is the information accurate and up-to-date?
3. DEPTH: Is the content sufficiently detailed?
4. ENGAGEMENT: Is the content engaging and interesting?
5. CLARITY: Is the content clear and easy to understand?

For each aspect, provide:
- Score (1-10)
- Issues found
- Suggestions for improvement

Format your response clearly for parsing."""
        
        response = await self.generate_response(prompt)
        return self._parse_content_quality_review(response)
    
    async def _review_structure_quality(self, blog_post: BlogPost, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Review the structure and organization of the blog post."""
        prompt = f"""Review the structure and organization of this blog post:

TITLE: {blog_post.title}
TOPIC BREAKUP: {blog_post.topic_breakup}
APPROACH: {blog_post.approach}

SECTIONS: {len(blog_post.sections)} sections
- {chr(10).join(f"- {section.title}" for section in blog_post.sections)}

Please evaluate:

1. LOGICAL FLOW: Does the content flow logically from one section to the next?
2. SECTION BALANCE: Are the sections well-balanced in terms of content?
3. TRANSITIONS: Are there smooth transitions between sections?
4. HEADING STRUCTURE: Is the heading structure clear and consistent?
5. CONTENT ORGANIZATION: Is the content well-organized within each section?

For each aspect, provide:
- Score (1-10)
- Issues found
- Suggestions for improvement

Format your response clearly for parsing."""
        
        response = await self.generate_response(prompt)
        return self._parse_structure_quality_review(response)
    
    async def _review_technical_accuracy(self, blog_post: BlogPost, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Review the technical accuracy of the blog post."""
        prompt = f"""Review the technical accuracy of this blog post:

TITLE: {blog_post.title}
TOPIC: {blog_post.generation_metadata.get('research_data', 'Unknown')}
CODE EXAMPLES: {sum(len(section.code_examples) for section in blog_post.sections)} total

Please evaluate:

1. TECHNICAL CORRECTNESS: Are the technical concepts explained correctly?
2. CODE QUALITY: Are the code examples accurate and well-written?
3. BEST PRACTICES: Does the content follow current best practices?
4. UP-TO-DATE INFORMATION: Is the information current and relevant?
5. TECHNICAL DEPTH: Is the technical depth appropriate for the audience?

For each aspect, provide:
- Score (1-10)
- Issues found
- Suggestions for improvement

Format your response clearly for parsing."""
        
        response = await self.generate_response(prompt)
        return self._parse_technical_accuracy_review(response)
    
    async def _review_readability(self, blog_post: BlogPost, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Review the readability and accessibility of the blog post."""
        prompt = f"""Review the readability and accessibility of this blog post:

TITLE: {blog_post.title}
TARGET AUDIENCE: {blog_post.generation_metadata.get('audience_context', {}).get('target_audience', 'developers')}
ESTIMATED READ TIME: {blog_post.estimated_read_time} minutes

Please evaluate:

1. LANGUAGE CLARITY: Is the language clear and accessible?
2. SENTENCE STRUCTURE: Are sentences well-structured and readable?
3. PARAGRAPH LENGTH: Are paragraphs appropriately sized?
4. TECHNICAL JARGON: Is technical jargon explained appropriately?
5. VISUAL PRESENTATION: Is the content visually appealing and easy to scan?

For each aspect, provide:
- Score (1-10)
- Issues found
- Suggestions for improvement

Format your response clearly for parsing."""
        
        response = await self.generate_response(prompt)
        return self._parse_readability_review(response)
    
    async def _review_goal_achievement(self, blog_post: BlogPost, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Review whether the blog post achieves its stated goals."""
        prompt = f"""Review whether this blog post achieves its stated goals:

TITLE: {blog_post.title}
STATED GOALS: {blog_post.goals}

CONTENT SUMMARY:
- Introduction: {blog_post.introduction[:200]}...
- Sections: {len(blog_post.sections)} sections covering {blog_post.topic_breakup}
- Conclusion: {blog_post.conclusion[:200]}...
- Wrapup: {blog_post.wrapup}
- Next Steps: {blog_post.next_steps}

Please evaluate:

1. GOAL COVERAGE: Does the content cover all stated goals?
2. GOAL DEPTH: Is each goal addressed with sufficient depth?
3. PRACTICAL VALUE: Does the content provide practical value for achieving the goals?
4. MEASURABLE OUTCOMES: Are the outcomes measurable and achievable?
5. GOAL ALIGNMENT: Is the content aligned with the stated goals?

For each aspect, provide:
- Score (1-10)
- Issues found
- Suggestions for improvement

Format your response clearly for parsing."""
        
        response = await self.generate_response(prompt)
        return self._parse_goal_achievement_review(response)
    
    async def _apply_improvements(self, blog_post: BlogPost, review_results: Dict[str, Any], context: Optional[Dict[str, Any]]) -> BlogPost:
        """Apply improvements based on review results."""
        # For now, return the blog post as-is
        # In production, you might want to implement automatic improvements
        return blog_post
    
    async def _generate_final_review(self, blog_post: BlogPost, review_results: Dict[str, Any], context: Optional[Dict[str, Any]]) -> str:
        """Generate a final review summary."""
        prompt = f"""Generate a final review summary for this blog post:

TITLE: {blog_post.title}
OVERALL SCORE: {review_results.get('overall_score', 0)}/10

REVIEW SUMMARY:
- Content Quality: {review_results.get('content_quality', {}).get('overall_score', 0)}/10
- Structure Quality: {review_results.get('structure_quality', {}).get('overall_score', 0)}/10
- Technical Accuracy: {review_results.get('technical_accuracy', {}).get('overall_score', 0)}/10
- Readability: {review_results.get('readability', {}).get('overall_score', 0)}/10
- Goal Achievement: {review_results.get('goal_achievement', {}).get('overall_score', 0)}/10

Please provide:
1. Overall assessment of the blog post quality
2. Key strengths
3. Areas for improvement
4. Final recommendation (publish, revise, or major rewrite)
5. Brief summary of the review process

Keep it concise but comprehensive."""
        
        return await self.generate_response(prompt)
    
    def _calculate_overall_score(self, review_results: Dict[str, Any]) -> float:
        """Calculate the overall quality score."""
        scores = []
        
        for category in ["content_quality", "structure_quality", "technical_accuracy", "readability", "goal_achievement"]:
            if category in review_results and "overall_score" in review_results[category]:
                scores.append(review_results[category]["overall_score"])
        
        if scores:
            return sum(scores) / len(scores)
        return 0.0
    
    def _calculate_quality_score(self, review_results: Dict[str, Any]) -> float:
        """Calculate a quality score for metadata."""
        return review_results.get("overall_score", 0.0)
    
    # Parsing methods for review responses
    def _parse_content_quality_review(self, response: str) -> Dict[str, Any]:
        """Parse content quality review response."""
        return self._parse_generic_review(response, "content_quality")
    
    def _parse_structure_quality_review(self, response: str) -> Dict[str, Any]:
        """Parse structure quality review response."""
        return self._parse_generic_review(response, "structure_quality")
    
    def _parse_technical_accuracy_review(self, response: str) -> Dict[str, Any]:
        """Parse technical accuracy review response."""
        return self._parse_generic_review(response, "technical_accuracy")
    
    def _parse_readability_review(self, response: str) -> Dict[str, Any]:
        """Parse readability review response."""
        return self._parse_generic_review(response, "readability")
    
    def _parse_goal_achievement_review(self, response: str) -> Dict[str, Any]:
        """Parse goal achievement review response."""
        return self._parse_generic_review(response, "goal_achievement")
    
    def _parse_generic_review(self, response: str, category: str) -> Dict[str, Any]:
        """Parse a generic review response."""
        # Simple parsing - in production, use more sophisticated parsing
        review_data = {
            "overall_score": 7,  # Default score
            "issues": [],
            "suggestions": []
        }
        
        # Basic parsing logic
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if 'score' in line.lower() and any(char.isdigit() for char in line):
                try:
                    score = int(line.split()[-1])
                    if 1 <= score <= 10:
                        review_data["overall_score"] = score
                except (ValueError, IndexError):
                    pass
        
        return review_data
