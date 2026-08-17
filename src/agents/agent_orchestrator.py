"""
Agent Orchestrator for coordinating the multi-agent blog generation workflow.
"""

import asyncio
import time
import traceback
import uuid
from typing import Callable, Dict, List, Any, Optional, Tuple, TypedDict
try:
    from langgraph import StateGraph, END, START
except ImportError:
    from langgraph.graph import StateGraph, END, START

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.layout import Layout
from rich.columns import Columns

from .base_agent import BaseAgent
from .research_agent import ResearchAgent
from .content_agent import ContentAgent
from .code_agent import CodeAgent
from .formatting_agent import FormattingAgent
from .review_agent import ReviewAgent
from ..core.models import BlogRequest, BlogPost, BlogGenerationResult
from ..core.config import settings
from .runtime import AgentRuntime
from ..tui.events import EventKind, WorkflowEvent


# Define the workflow state structure

# Define the workflow state structure as a simple dict type annotation
AgentState = Dict[str, Any]


class AgentOrchestrator:
    """Orchestrates the multi-agent workflow for blog generation."""
    
    def __init__(self, verbose: bool = False, use_ollama: bool = False, ollama_base_url: Optional[str] = None, ollama_model: Optional[str] = None, use_lm_studio: bool = False, lm_studio_base_url: Optional[str] = None, lm_studio_model: Optional[str] = None, use_deepseek: bool = False, deepseek_base_url: Optional[str] = None, deepseek_model: Optional[str] = None, streaming: bool = True, stream_mode: str = "updates", agent_runtime: AgentRuntime | str = AgentRuntime.LANGCHAIN, event_sink: Optional[Callable[[WorkflowEvent], None]] = None, **kwargs):
        """Initialize the agent orchestrator."""
        self.verbose = verbose
        self.use_ollama = use_ollama
        self.ollama_base_url = ollama_base_url
        self.use_lm_studio = use_lm_studio
        self.lm_studio_base_url = lm_studio_base_url
        self.lm_studio_model = lm_studio_model
        self.use_deepseek = use_deepseek
        self.deepseek_base_url = deepseek_base_url
        self.deepseek_model = deepseek_model
        self.streaming = streaming
        self.stream_mode = stream_mode
        self.event_sink = event_sink
        self.run_id = str(uuid.uuid4())
        self.agent_runtime = agent_runtime if isinstance(agent_runtime, AgentRuntime) else AgentRuntime.parse(agent_runtime)
        if use_deepseek and self.agent_runtime is not AgentRuntime.LANGCHAIN:
            raise ValueError("DeepSeek backend is currently supported by the LangChain track only")
        if use_deepseek and (use_ollama or use_lm_studio):
            raise ValueError("DeepSeek cannot be combined with Ollama or LM Studio")
        
        # Initialize Rich console for beautiful output
        self.console = Console()
        
        # Disable LangSmith to prevent API calls
        try:
            import os
            os.environ["LANGCHAIN_TRACING"] = "false"
            os.environ["LANGCHAIN_ENDPOINT"] = ""
            os.environ["LANGCHAIN_API_KEY"] = ""
            os.environ["LANGCHAIN_PROJECT"] = ""
            os.environ["LANGCHAIN_TRACING_V2"] = "false"
            os.environ["LANGCHAIN_CALLBACKS"] = ""
        except Exception:
            pass
        
        if self.verbose:
            self.console.print(Panel(
                "[bold blue]🚀 Initializing Agent Orchestrator...[/bold blue]",
                title="[bold green]System Initialization[/bold green]",
                border_style="blue"
            ))
            if use_ollama:
                self.console.print(Panel(
                    f"[bold yellow]🦙 Using Ollama at:[/bold yellow] {ollama_base_url or 'http://localhost:11434'}",
                    title="[bold yellow]Ollama Configuration[/bold yellow]",
                    border_style="yellow"
                ))
            if use_lm_studio:
                self.console.print(Panel(
                    f"[bold blue]🖥️ Using LM Studio at:[/bold blue] {lm_studio_base_url or 'http://localhost:1234'}",
                    title="[bold blue]LM Studio Configuration[/bold blue]",
                    border_style="blue"
                ))
            if streaming:
                self.console.print(Panel(
                    f"[bold green]📡 Streaming output enabled[/bold green]\n"
                    f"[cyan]Real-time agent thinking and LLM responses will be displayed[/cyan]\n"
                    f"[yellow]Mode:[/yellow] {stream_mode}",
                    title="[bold green]Streaming Mode[/bold green]",
                    border_style="green"
                ))
        
        # Pass local model settings to all agents
        local_model_kwargs = {
            "verbose": verbose,
            "use_ollama": use_ollama,
            "ollama_base_url": ollama_base_url,
            "ollama_model": ollama_model,
            "use_lm_studio": use_lm_studio,
            "lm_studio_base_url": lm_studio_base_url,
            "lm_studio_model": lm_studio_model,
            "use_deepseek": use_deepseek,
            "deepseek_base_url": deepseek_base_url,
            "deepseek_model": deepseek_model,
            "streaming": streaming,
            "stream_mode": stream_mode,
            "agent_runtime": self.agent_runtime,
            "event_sink": event_sink,
            "run_id": self.run_id,
            "runtime": self.agent_runtime.value,
            **kwargs
        }
        
        self.research_agent = ResearchAgent(**local_model_kwargs)
        self.content_agent = ContentAgent(**local_model_kwargs)
        self.code_agent = CodeAgent(**local_model_kwargs)
        self.formatting_agent = FormattingAgent(**local_model_kwargs)
        self.review_agent = ReviewAgent(**local_model_kwargs)
        
        if self.verbose:
            self.console.print(Panel(
                "[bold green]✅ All agents initialized successfully[/bold green]",
                title="[bold green]Agent Status[/bold green]",
                border_style="green"
            ))
        
        # Initialize the workflow graph
        self.workflow = self._create_workflow()
        
        if self.verbose:
            self.console.print(Panel(
                "[bold green]✅ LangGraph workflow created and compiled[/bold green]\n"
                "[cyan]🔧 Enabling LangGraph verbose mode...[/cyan]",
                title="[bold green]Workflow Status[/bold green]",
                border_style="green"
            ))
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for blog generation."""
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent
        workflow.add_node("research", self._research_node)
        workflow.add_node("content", self._content_node)
        workflow.add_node("code", self._code_node)
        workflow.add_node("formatting", self._formatting_node)
        workflow.add_node("review", self._review_node)
        
        # Define the workflow flow
        workflow.set_entry_point("research")
        workflow.add_edge("research", "content")
        workflow.add_edge("content", "code")
        workflow.add_edge("code", "formatting")
        workflow.add_edge("formatting", "review")
        workflow.add_edge("review", END)
        
        # Compile the workflow
        return workflow.compile()

    def _publish_event(self, kind: EventKind, node: str = "", text: str = "", error: str = "", details: Optional[Dict[str, Any]] = None) -> None:
        """Publish a UI event when a consumer has opted in."""
        if not self.event_sink:
            return
        self.event_sink(WorkflowEvent(
            kind=kind,
            run_id=self.run_id,
            runtime=self.agent_runtime.value,
            node=node,
            text=text,
            error=error,
            details=details or {},
        ))
    
    async def _research_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the research agent node with enhanced streaming output."""
        self._publish_event(EventKind.NODE_STARTED, node="research")
        if self.verbose:
            self.console.print(Panel(
                f"[bold blue]🔍 [{self.research_agent.name}][/bold blue]\n"
                f"[cyan]Starting research phase...[/cyan]\n"
                f"[yellow]Topic:[/yellow] {state.get('blog_request', {}).topic}",
                title="[bold blue]Research Phase[/bold blue]",
                border_style="blue"
            ))
        
        try:
            blog_request = state["blog_request"]
            
            # Show research context
            if self.verbose:
                self.console.print(f"📚 [yellow]Research Goals:[/yellow] {', '.join(blog_request.goals)}")
                self.console.print(f"🎯 [yellow]Target Audience:[/yellow] {blog_request.target_audience}")
                self.console.print(f"📝 [yellow]Tone:[/yellow] {blog_request.tone}")
                self.console.print(f"📏 [yellow]Length:[/yellow] {blog_request.length}")
                if blog_request.custom_instructions:
                    self.console.print(f"💡 [yellow]Custom Instructions:[/yellow] {blog_request.custom_instructions}")
            
            # Execute research with streaming
            research_result = await self.research_agent.process(blog_request, {})
            self._publish_event(EventKind.NODE_COMPLETED, node="research", details={"output_size": len(str(research_result))})
            
            if self.verbose:
                self.console.print(Panel(
                    f"[bold green]✅ [{self.research_agent.name}][/bold green]\n"
                    f"[green]Research completed successfully[/green]\n"
                    f"[cyan]Key findings:[/cyan] {len(str(research_result))} characters of research data",
                    title="[bold green]Research Complete[/bold green]",
                    border_style="green"
                ))
            
            return {
                **state,
                "research_data": research_result,
                "metadata": {
                    **state.get("metadata", {}),
                    "research_completed": True,
                    "research_agent": self.research_agent.name
                }
            }
        except Exception as e:
            tb = traceback.format_exc()
            error_msg = f"Research failed: {str(e)}"
            self._publish_event(EventKind.NODE_FAILED, node="research", error=error_msg)
            self.console.print(Panel(
                f"[bold red]❌ [{self.research_agent.name}][/bold red]\n"
                f"[red]{error_msg}[/red]\n\n"
                f"[dim]{tb}[/dim]",
                title="[bold red]Research Error[/bold red]",
                border_style="red"
            ))

            return {
                **state,
                "errors": state.get("errors", []) + [error_msg]
            }
    
    async def _content_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the content agent node with enhanced streaming output."""
        self._publish_event(EventKind.NODE_STARTED, node="content")
        if self.verbose:
            self.console.print(Panel(
                f"[bold blue]✍️ [{self.content_agent.name}][/bold blue]\n"
                f"[cyan]Starting content generation...[/cyan]\n"
                f"[yellow]Using research data:[/yellow] {len(str(state.get('research_data', '')))} characters",
                title="[bold blue]Content Generation Phase[/bold blue]",
                border_style="blue"
            ))
        
        try:
            blog_request = state["blog_request"]
            research_data = state.get("research_data", {})
            
            # Create context for content generation
            context = {
                "research_data": research_data,
                "blog_request": blog_request
            }
            
            if self.verbose:
                self.console.print(f"🔗 [yellow]Context created with:[/yellow] research_data, blog_request")
                self.console.print(f"📝 [yellow]Generating blog content with streaming output...[/yellow]")
            
            # Execute content generation with streaming
            blog_post = await self.content_agent.process(research_data, context)
            self._publish_event(EventKind.NODE_COMPLETED, node="content", details={"output_size": len(str(blog_post))})
            
            if self.verbose:
                sections_count = len(blog_post.sections) if hasattr(blog_post, 'sections') else 0
                total_content = sum(len(s.content) for s in blog_post.sections) if hasattr(blog_post, 'sections') else 0
                
                self.console.print(Panel(
                    f"[bold green]✅ [{self.content_agent.name}][/bold green]\n"
                    f"[green]Content generation completed[/green]\n"
                    f"[cyan]Sections created:[/cyan] {sections_count}\n"
                    f"[cyan]Total content:[/cyan] {total_content} characters",
                    title="[bold green]Content Complete[/bold green]",
                    border_style="green"
                ))
            
            return {
                **state,
                "blog_post": blog_post,
                "metadata": {
                    **state.get("metadata", {}),
                    "content_completed": True,
                    "content_agent": self.content_agent.name
                }
            }
        except Exception as e:
            tb = traceback.format_exc()
            error_msg = f"Content generation failed: {str(e)}"
            self._publish_event(EventKind.NODE_FAILED, node="content", error=error_msg)
            self.console.print(Panel(
                f"[bold red]❌ [{self.content_agent.name}][/bold red]\n"
                f"[red]{error_msg}[/red]\n\n"
                f"[dim]{tb}[/dim]",
                title="[bold red]Content Generation Error[/bold red]",
                border_style="red"
            ))

            return {
                **state,
                "errors": state.get("errors", []) + [error_msg]
            }
    
    async def _code_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the code agent node with enhanced streaming output."""
        self._publish_event(EventKind.NODE_STARTED, node="code")
        # Check if we have a valid blog post to work with
        if "blog_post" not in state or state["blog_post"] is None:
            error_msg = "No blog post available for code generation"
            if self.verbose:
                self.console.print(Panel(
                    f"[bold red]❌ [{self.code_agent.name}][/bold red]\n"
                    f"[red]{error_msg}[/red]",
                    title="[bold red]Code Generation Error[/bold red]",
                    border_style="red"
                ))
            return {
                **state,
                "errors": state.get("errors", []) + [error_msg]
            }
        
        # Check if there are previous errors
        if state.get("errors"):
            if self.verbose:
                self.console.print(f"⚠️ [{self.code_agent.name}] Skipping code generation due to previous errors")
            return state
        
        if self.verbose:
            self.console.print(Panel(
                f"[bold blue]💻 [{self.code_agent.name}][/bold blue]\n"
                f"[cyan]Starting code example generation...[/cyan]\n"
                f"[yellow]Blog sections:[/yellow] {len(state.get('blog_post', {}).sections) if hasattr(state.get('blog_post', {}), 'sections') else 0}",
                title="[bold blue]Code Generation Phase[/bold blue]",
                border_style="blue"
            ))
        
        try:
            blog_post = state["blog_post"]
            blog_request = state["blog_request"]
            
            # Create context for the code agent
            context = {
                "blog_request": blog_request,
                "include_code_examples": blog_request.include_code_examples
            }
            
            if self.verbose:
                self.console.print(f"🔗 [yellow]Context created with:[/yellow] blog_request, include_code_examples")
                self.console.print(f"💻 [yellow]Generating code examples with streaming output...[/yellow]")
            
            enhanced_blog_post = await self.code_agent.process(blog_post, context)
            self._publish_event(EventKind.NODE_COMPLETED, node="code", details={"output_size": len(str(enhanced_blog_post))})
            
            if self.verbose:
                total_examples = sum(len(s.code_examples) for s in enhanced_blog_post.sections)
                self.console.print(Panel(
                    f"[bold green]✅ [{self.code_agent.name}][/bold green]\n"
                    f"[green]Code generation completed[/green]\n"
                    f"[cyan]Total code examples added:[/cyan] {total_examples}",
                    title="[bold green]Code Generation Complete[/bold green]",
                    border_style="green"
                ))
            
            return {
                **state,
                "blog_post": enhanced_blog_post,
                "metadata": {
                    **state.get("metadata", {}),
                    "code_completed": True,
                    "code_agent": self.code_agent.name
                }
            }
        except Exception as e:
            tb = traceback.format_exc()
            error_msg = f"Code generation failed: {str(e)}"
            self._publish_event(EventKind.NODE_FAILED, node="code", error=error_msg)
            self.console.print(Panel(
                f"[bold red]❌ [{self.code_agent.name}][/bold red]\n"
                f"[red]{error_msg}[/red]\n\n"
                f"[dim]{tb}[/dim]",
                title="[bold red]Code Generation Error[/bold red]",
                border_style="red"
            ))

            return {
                **state,
                "errors": state.get("errors", []) + [error_msg]
            }
    
    async def _formatting_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the formatting agent node with enhanced streaming output."""
        self._publish_event(EventKind.NODE_STARTED, node="formatting")
        # Check if we have a valid blog post to work with
        if "blog_post" not in state or state["blog_post"] is None:
            error_msg = "No blog post available for formatting"
            if self.verbose:
                self.console.print(Panel(
                    f"[bold red]❌ [{self.formatting_agent.name}][/bold red]\n"
                    f"[red]{error_msg}[/red]",
                    title="[bold red]Formatting Error[/bold red]",
                    border_style="red"
                ))
            return {
                **state,
                "errors": state.get("errors", []) + [error_msg]
            }
        
        # Check if there are previous errors
        if state.get("errors"):
            if self.verbose:
                self.console.print(f"⚠️ [{self.formatting_agent.name}] Skipping formatting due to previous errors")
            return state
        
        if self.verbose:
            self.console.print(Panel(
                f"[bold blue]🎨 [{self.formatting_agent.name}][/bold blue]\n"
                f"[cyan]Starting formatting and structure optimization...[/cyan]\n"
                f"[yellow]Blog sections:[/yellow] {len(state.get('blog_post', {}).sections) if hasattr(state.get('blog_post', {}), 'sections') else 0}",
                title="[bold blue]Formatting Phase[/bold blue]",
                border_style="blue"
            ))
        
        try:
            blog_post = state["blog_post"]
            
            if self.verbose:
                self.console.print(f"🎨 [yellow]Applying Markdown formatting and structure optimization...[/yellow]")
            
            formatted_blog_post = await self.formatting_agent.process(blog_post, {})
            self._publish_event(EventKind.NODE_COMPLETED, node="formatting", details={"output_size": len(str(formatted_blog_post))})
            
            if self.verbose:
                self.console.print(Panel(
                    f"[bold green]✅ [{self.formatting_agent.name}][/bold green]\n"
                    f"[green]Formatting completed[/green]\n"
                    f"[cyan]Blog structure optimized and Markdown applied[/cyan]",
                    title="[bold green]Formatting Complete[/bold green]",
                    border_style="green"
                ))
            
            return {
                **state,
                "blog_post": formatted_blog_post,
                "metadata": {
                    **state.get("metadata", {}),
                    "formatting_completed": True,
                    "formatting_agent": self.formatting_agent.name
                }
            }
        except Exception as e:
            tb = traceback.format_exc()
            error_msg = f"Formatting failed: {str(e)}"
            self._publish_event(EventKind.NODE_FAILED, node="formatting", error=error_msg)
            self.console.print(Panel(
                f"[bold red]❌ [{self.formatting_agent.name}][/bold red]\n"
                f"[red]{error_msg}[/red]\n\n"
                f"[dim]{tb}[/dim]",
                title="[bold red]Formatting Error[/bold red]",
                border_style="red"
            ))

            return {
                **state,
                "errors": state.get("errors", []) + [error_msg]
            }
    
    async def _review_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the review agent node with enhanced streaming output."""
        self._publish_event(EventKind.NODE_STARTED, node="review")
        # Check if we have a valid blog post to work with
        if "blog_post" not in state or state["blog_post"] is None:
            error_msg = "No blog post available for review"
            if self.verbose:
                self.console.print(Panel(
                    f"[bold red]❌ [{self.review_agent.name}][/bold red]\n"
                    f"[red]{error_msg}[/red]",
                    title="[bold red]Review Error[/bold red]",
                    border_style="red"
                ))
            return {
                **state,
                "errors": state.get("errors", []) + [error_msg]
            }
        
        # Check if there are previous errors
        if state.get("errors"):
            if self.verbose:
                self.console.print(f"⚠️ [{self.review_agent.name}] Skipping review due to previous errors")
            return state
        
        if self.verbose:
            self.console.print(Panel(
                f"[bold blue]🔍 [{self.review_agent.name}][/bold blue]\n"
                f"[cyan]Starting quality review and final assessment...[/cyan]\n"
                f"[yellow]Blog sections:[/yellow] {len(state.get('blog_post', {}).sections) if hasattr(state.get('blog_post', {}), 'sections') else 0}",
                title="[bold blue]Review Phase[/bold blue]",
                border_style="blue"
            ))
        
        try:
            blog_post = state["blog_post"]
            
            if self.verbose:
                self.console.print(f"🔍 [yellow]Performing comprehensive quality review...[/yellow]")
            
            # Review agent returns a tuple (final_blog_post, review_results)
            review_result = await self.review_agent.process(blog_post, {})
            self._publish_event(EventKind.NODE_COMPLETED, node="review")
            
            # Properly unpack the tuple
            if isinstance(review_result, tuple):
                final_blog_post, review_results = review_result
            else:
                # Fallback if not a tuple (shouldn't happen)
                final_blog_post = review_result
                review_results = {}
            
            if self.verbose:
                # Get quality score from the blog post's metadata
                quality_score = final_blog_post.generation_metadata.get('quality_score', 'N/A') if hasattr(final_blog_post, 'generation_metadata') else 'N/A'
                
                # Get review summary from review results
                review_summary = ""
                if isinstance(review_results, dict):
                    if review_results.get('final_review'):
                        review_summary = review_results['final_review'][:100] + "..." if len(review_results['final_review']) > 100 else review_results['final_review']
                    elif review_results.get('suggestions'):
                        review_summary = f"Suggestions: {', '.join(review_results['suggestions'][:2])}"
                
                self.console.print(Panel(
                    f"[bold green]✅ [{self.review_agent.name}][/bold green]\n"
                    f"[green]Review completed[/green]\n"
                    f"[cyan]Quality Score:[/cyan] {quality_score}\n"
                    f"[cyan]Review Notes:[/cyan] {review_summary}",
                    title="[bold green]Review Complete[/bold green]",
                    border_style="green"
                ))
            
            return {
                **state,
                "blog_post": final_blog_post,
                "final_blog_post": final_blog_post,  # Set the final_blog_post that the workflow expects
                "review_results": review_results,
                "metadata": {
                    **state.get("metadata", {}),
                    "review_completed": True,
                    "review_agent": self.review_agent.name,
                    "quality_score": final_blog_post.generation_metadata.get('quality_score') if hasattr(final_blog_post, 'generation_metadata') else None
                }
            }
        except Exception as e:
            tb = traceback.format_exc()
            error_msg = f"Review failed: {str(e)}"
            self._publish_event(EventKind.NODE_FAILED, node="review", error=error_msg)
            self.console.print(Panel(
                f"[bold red]❌ [{self.review_agent.name}][/bold red]\n"
                f"[red]{error_msg}[/red]\n\n"
                f"[dim]{tb}[/dim]",
                title="[bold red]Review Error[/bold red]",
                border_style="red"
            ))

            return {
                **state,
                "errors": state.get("errors", []) + [error_msg]
            }
    
    async def generate_blog(self, blog_request: BlogRequest) -> BlogGenerationResult:
        """Generate a blog post using the multi-agent workflow.
        
        Args:
            blog_request: The blog generation request
            
        Returns:
            Blog generation result with the final blog post
        """
        start_time = time.time()
        self._publish_event(
            EventKind.WORKFLOW_STARTED,
            details={"topic": blog_request.topic, "blog_type": blog_request.blog_type.value},
        )
        
        try:
            # Initialize the workflow state
            initial_state = {
                "blog_request": blog_request,
                "research_data": {},
                "blog_post": None,
                "review_results": {},
                "final_blog_post": None,
                "errors": [],
                "metadata": {
                    "workflow_started": True,
                    "blog_type": blog_request.blog_type.value,
                    "topic": blog_request.topic
                }
            }
            
            if self.verbose:
                self.console.print(Panel(
                    "[bold blue]🚀 Executing LangGraph workflow...[/bold blue]",
                    title="[bold green]Workflow Execution[/bold green]",
                    border_style="blue"
                ))
            
            # Execute the workflow with verbose callbacks if enabled
            if self.verbose:
                # Create a simple custom callback handler for workflow verbose logging
                from langchain_core.callbacks import BaseCallbackHandler
                
                class WorkflowCallbackHandler(BaseCallbackHandler):
                    def __init__(self, console):
                        self.console = console
                    
                    def on_chain_start(self, serialized, inputs, **kwargs):
                        try:
                            name = serialized.get('name', 'Unknown') if serialized else 'Unknown'
                            self.console.print(f"🔄 [Workflow] Chain started: {name}")
                        except Exception as e:
                            self.console.print(f"🔄 [Workflow] Chain started")
                    
                    def on_chain_end(self, outputs, **kwargs):
                        self.console.print(f"✅ [Workflow] Chain completed")
                    
                    def on_chain_error(self, error, **kwargs):
                        self.console.print(f"❌ [Workflow] Chain error: {error}")
                
                callbacks = [WorkflowCallbackHandler(self.console)]
                final_state = await self.workflow.ainvoke(initial_state, config={"callbacks": callbacks})
            else:
                final_state = await self.workflow.ainvoke(initial_state)
            
            if self.verbose:
                self.console.print(Panel(
                    f"[bold green]✅ Workflow completed[/bold green]\n"
                    f"[cyan]Final state keys:[/cyan] {list(final_state.keys())}",
                    title="[bold green]Workflow Status[/bold green]",
                    border_style="green"
                ))
                if final_state.get("errors"):
                    self.console.print(Panel(
                        f"[bold red]⚠️ Errors in final state:[/bold red]\n"
                        f"[red]{final_state['errors']}[/red]",
                        title="[bold red]Error Report[/bold red]",
                        border_style="red"
                    ))
            
            # Check for errors
            if final_state.get("errors"):
                error_msg = "; ".join(final_state["errors"])
                self._publish_event(EventKind.WORKFLOW_FAILED, error=error_msg)
                if self.verbose:
                    self.console.print(Panel(
                        f"[bold red]❌ Workflow completed with errors:[/bold red]\n"
                        f"[red]{error_msg}[/red]",
                        title="[bold red]Workflow Failed[/bold red]",
                        border_style="red"
                    ))
                return BlogGenerationResult(
                    success=False,
                    blog_post=None,
                    error_message=error_msg,
                    generation_time=time.time() - start_time,
                    tokens_used=None,
                    cost_estimate=None
                )
            
            # Extract the final blog post
            final_blog_post = final_state.get("final_blog_post")
            if not final_blog_post:
                self._publish_event(EventKind.WORKFLOW_FAILED, error="No blog post generated from workflow")
                if self.verbose:
                    print("❌ No final blog post found in workflow result")
                    print(f"Available keys: {list(final_state.keys())}")
                    if "blog_post" in final_state:
                        print(f"Blog post exists but not final: {type(final_state['blog_post'])}")
                
                return BlogGenerationResult(
                    success=False,
                    blog_post=None,
                    error_message="No blog post generated from workflow",
                    generation_time=time.time() - start_time,
                    tokens_used=None,
                    cost_estimate=None
                )
            
            metadata = final_state.get("metadata", {})
            
            if self.verbose:
                print(f"✅ Final blog post extracted: {final_blog_post.title}")
                print(f"📊 Metadata: {list(metadata.keys())}")
            
            # Calculate generation metrics
            generation_time = time.time() - start_time
            self._publish_event(
                EventKind.WORKFLOW_COMPLETED,
                details={"generation_time": generation_time},
            )
            
            return BlogGenerationResult(
                success=True,
                blog_post=final_blog_post,
                error_message=None,
                generation_time=generation_time,
                tokens_used=metadata.get("tokens_used"),
                cost_estimate=metadata.get("cost_estimate")
            )
            
        except Exception as e:
            tb = traceback.format_exc()
            self._publish_event(EventKind.WORKFLOW_FAILED, error=str(e))
            self.console.print(Panel(
                f"[bold red]❌ Workflow execution failed[/bold red]\n"
                f"[red]{str(e)}[/red]\n\n"
                f"[dim]{tb}[/dim]",
                title="[bold red]Workflow Error[/bold red]",
                border_style="red"
            ))
            return BlogGenerationResult(
                success=False,
                blog_post=None,
                error_message=f"Workflow execution failed: {str(e)}",
                generation_time=time.time() - start_time,
                tokens_used=None,
                cost_estimate=None
            )
    
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
        """Generate a tech blog post with the specified parameters.
        
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
        from ..core.models import BlogType
        
        blog_request = BlogRequest(
            topic=topic,
            blog_type=BlogType.TECH_BLOG,
            goals=goals,
            target_audience=target_audience,
            tone=tone,
            length=length,
            include_code_examples=include_code_examples,
            include_diagrams=include_diagrams,
            custom_instructions=custom_instructions
        )
        
        return await self.generate_blog(blog_request)
    
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
        from ..core.models import BlogType
        
        # Add difficulty to custom instructions
        if custom_instructions:
            custom_instructions = f"Difficulty level: {difficulty}. {custom_instructions}"
        else:
            custom_instructions = f"Difficulty level: {difficulty}"
        
        blog_request = BlogRequest(
            topic=topic,
            blog_type=BlogType.TUTORIAL,
            goals=goals,
            target_audience=target_audience,
            tone=tone,
            length=length,
            include_code_examples=include_code_examples,
            include_diagrams=False,
            custom_instructions=custom_instructions
        )
        
        return await self.generate_blog(blog_request)
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get the current status of the workflow."""
        return {
            "agents": {
                "research": self.research_agent.name,
                "content": self.content_agent.name,
                "code": self.code_agent.name,
                "formatting": self.formatting_agent.name,
                "review": self.review_agent.name
            },
            "workflow_compiled": self.workflow is not None,
            "settings": {
                "default_model": settings.default_model,
                "default_deepseek_model": settings.default_deepseek_model,
                "default_temperature": settings.default_temperature,
                "max_tokens": settings.max_tokens,
                "agent_runtime": self.agent_runtime.value,
            }
        }
