"""
Base agent class for the multi-agent blog generation system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, AsyncGenerator
try:
    from langchain.schema import BaseMessage
except ImportError:
    try:
        from langchain_core.messages import BaseMessage
    except ImportError:
        from langchain.schema.messages import BaseMessage

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.spinner import Spinner

from ..core.config import settings


class StreamingCallbackHandler:
    """Custom callback handler for streaming LLM responses with agent context."""
    
    def __init__(self, agent_name: str, console: Console, verbose: bool = False, stream_mode: str = "updates"):
        self.agent_name = agent_name
        self.console = console
        self.verbose = verbose
        self.current_response = ""
        self.is_streaming = False
        self.stream_mode = stream_mode
        self.live_display = None
        self.streaming_panel = None
        # LangChain compatibility attributes
        self.run_inline = False
        self.ignore_chat_model = False
        self.raise_error = False
        self.ignore_llm = False
    
    def on_llm_start(self, serialized, prompts, **kwargs):
        """Called when LLM starts generating."""
        if self.verbose:
            self.console.print(f"🔄 [{self.agent_name}] LLM generation started...")
        self.is_streaming = True
        self.current_response = ""
        
        # Create streaming panel
        from rich.panel import Panel
        from rich.live import Live
        from rich.text import Text
        
        self.streaming_panel = Panel(
            Text("", style="cyan"),
            title=f"[bold cyan]{self.agent_name} - Streaming Output[/bold cyan]",
            border_style="cyan",
            padding=(0, 1),
            width=min(120, self.console.width - 4),  # Use most of console width
            height=min(20, self.console.height - 10)  # Reasonable height limit
        )
        
        # Start live display
        self.live_display = Live(self.streaming_panel, console=self.console, refresh_per_second=10)
        self.live_display.start()
    
    def on_chat_model_start(self, serialized, messages, **kwargs):
        """Called when chat model starts generating (LangChain compatibility)."""
        if self.verbose:
            self.console.print(f"🔄 [{self.agent_name}] Chat model generation started...")
        self.is_streaming = True
        self.current_response = ""
        
        # Create streaming panel
        from rich.panel import Panel
        from rich.live import Live
        from rich.text import Text
        
        self.streaming_panel = Panel(
            Text("", style="cyan"),
            title=f"[bold cyan]{self.agent_name} - Streaming Output[/bold cyan]",
            border_style="cyan",
            padding=(0, 1),
            width=min(120, self.console.width - 4),  # Use most of console width
            height=min(20, self.console.height - 10)  # Reasonable height limit
        )
        
        # Start live display
        self.live_display = Live(self.streaming_panel, console=self.console, refresh_per_second=10)
        self.live_display.start()
    
    def on_llm_new_token(self, token, **kwargs):
        """Called for each new token generated (LangChain compatibility)."""
        if self.verbose and self.live_display and self.streaming_panel:
            self.current_response += str(token)
            
            # Update the streaming panel with current content
            from rich.text import Text
            from rich.console import Group
            from rich.panel import Panel
            
            # Split content into lines and handle overflow
            lines = self.current_response.split('\n')
            
            # Calculate max height (leave room for other UI elements)
            max_height = max(10, self.console.height - 20)  # Reserve 20 lines for other content
            
            # If content exceeds max height, show only the last portion
            if len(lines) > max_height:
                # Show the last max_height lines with an indicator
                visible_lines = lines[-max_height:]
                overflow_indicator = f"[dim]... (showing last {max_height} lines, {len(lines) - max_height} more above)[/dim]"
                visible_lines.insert(0, overflow_indicator)
            else:
                visible_lines = lines
            
            # Create wrapped content for each line
            wrapped_content = Text()
            max_width = min(100, self.console.width - 20)  # Reserve 20 chars for margins
            
            for line in visible_lines:
                # Handle very long lines by wrapping them
                if len(line) > max_width:
                    # Wrap long lines
                    for i in range(0, len(line), max_width):
                        chunk = line[i:i + max_width]
                        wrapped_content.append(chunk + '\n', style="cyan")
                else:
                    wrapped_content.append(line + '\n', style="cyan")
            
            # Update the panel with the wrapped content
            self.streaming_panel.renderable = wrapped_content
            self.live_display.update(self.streaming_panel)
    
    def on_llm_end(self, response, **kwargs):
        """Called when LLM generation ends."""
        if self.verbose:
            # Stop live display
            if self.live_display:
                self.live_display.stop()
                self.live_display = None
            
            # Show completion message
            self.console.print(f"✅ [{self.agent_name}] Generation completed ({len(self.current_response)} characters)")
            
            # Show final content in a clean panel
            from rich.panel import Panel
            from rich.text import Text
            
            # Create a better final output panel that handles long content
            from rich.console import Group
            from rich.text import Text
            
            # Split content into manageable chunks
            lines = self.current_response.split('\n')
            max_display_lines = min(30, self.console.height - 15)  # Show max 30 lines or what fits
            
            if len(lines) > max_display_lines:
                # Show first and last portions with ellipsis
                first_lines = lines[:max_display_lines//2]
                last_lines = lines[-(max_display_lines//2):]
                
                display_content = Group(
                    Text('\n'.join(first_lines), style="green"),
                    Text(f"\n[dim]... ({len(lines) - max_display_lines} lines omitted) ...[/dim]\n", style="dim"),
                    Text('\n'.join(last_lines), style="green")
                )
                
                # Add a note about full content
                self.console.print(f"[dim]📄 Full content length: {len(self.current_response)} characters[/dim]")
            else:
                display_content = Text(self.current_response, style="green")
            
            final_panel = Panel(
                display_content,
                title=f"[bold green]{self.agent_name} - Final Output[/bold green]",
                border_style="green",
                padding=(0, 1),
                width=min(120, self.console.width - 4)
            )
            self.console.print(final_panel)
            
        self.is_streaming = False
    
    def on_llm_error(self, error, **kwargs):
        """Called when LLM encounters an error."""
        if self.verbose:
            # Stop live display
            if self.live_display:
                self.live_display.stop()
                self.live_display = None
            
            self.console.print(f"❌ [{self.agent_name}] LLM error: {error}")
        self.is_streaming = False


class BaseAgent(ABC):
    """Base class for all agents in the blog generation system."""
    
    def __init__(
        self,
        name: str,
        description: str,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        verbose: bool = False,
        use_ollama: bool = False,
        ollama_base_url: Optional[str] = None,
        ollama_model: Optional[str] = None,
        use_lm_studio: bool = False,
        lm_studio_base_url: Optional[str] = None,
        lm_studio_model: Optional[str] = None,
        streaming: bool = True,  # Enable streaming by default
        stream_mode: str = "updates",  # Streaming mode for output
        request_timeout: float = 120.0,  # Max seconds to wait for LLM response
    ):
        """Initialize the base agent.
        
        Args:
            name: Name of the agent
            description: Description of what the agent does
            model_name: AI model to use (defaults to settings)
            temperature: Temperature for generation (defaults to settings)
            max_tokens: Maximum tokens for generation (defaults to settings)
            streaming: Whether to enable streaming output
        """
        self.name = name
        self.description = description
        self.verbose = verbose
        self.use_ollama = use_ollama
        self.ollama_base_url = ollama_base_url or "http://localhost:11434"
        self.use_lm_studio = use_lm_studio
        self.lm_studio_base_url = lm_studio_base_url or "http://localhost:1234"
        self.lm_studio_model = lm_studio_model
        self.streaming = streaming
        self.stream_mode = stream_mode
        self.request_timeout = request_timeout
        
        # Set model name based on local model usage
        if use_ollama:
            self.model_name = ollama_model or model_name or settings.default_ollama_model
        elif use_lm_studio:
            self.model_name = lm_studio_model or model_name or settings.default_lm_studio_model
        else:
            self.model_name = model_name or settings.default_model
            
        self.temperature = temperature or settings.default_temperature
        self.max_tokens = max_tokens or settings.max_tokens
        
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
        
        # Initialize the language model
        self._init_llm()
    
    def _init_llm(self):
        """Initialize the language model based on configuration or Ollama."""
        try:
            if self.use_ollama:
                # Use Ollama for local testing
                try:
                    # Quick connectivity check to fail fast instead of hanging
                    try:
                        import httpx
                        httpx.get(f"{self.ollama_base_url}/api/tags", timeout=5.0)
                    except Exception as e:
                        raise Exception(
                            f"Cannot reach Ollama at {self.ollama_base_url}: {e}. Ensure Ollama is running or disable --ollama."
                        )

                    from langchain_ollama import OllamaLLM
                    if self.verbose:
                        self.console.print(f"🦙 [{self.name}] Initializing Ollama with model: {self.model_name}")
                    
                    # Note: Model validation will happen during first use
                    if self.verbose:
                        self.console.print(f"🦙 [{self.name}] Model validation will occur on first use")
                    
                    self.llm = OllamaLLM(
                        model=self.model_name,
                        base_url=self.ollama_base_url,
                        temperature=self.temperature,
                        # Add options to help with token limits
                        options={
                            "num_ctx": 4096,  # Context window size
                            "num_predict": 2048,  # Max tokens to generate
                            "stop": ["<|im_end|>", "<|endoftext|>", "<|endofprompt|>"]  # Stop tokens
                        }
                    )
                    
                    if self.verbose:
                        self.console.print(f"✅ [{self.name}] Modern Ollama initialized successfully")
                        
                except ImportError as e:
                    if self.verbose:
                        self.console.print(f"⚠️ [{self.name}] Modern Ollama import failed: {e}")
                    # Fallback to deprecated version
                    from langchain_community.llms import Ollama
                    if self.verbose:
                        self.console.print(f"🦙 [{self.name}] Initializing Ollama (legacy) with model: {self.model_name}")
                    self.llm = Ollama(
                        model=self.model_name,
                        base_url=self.ollama_base_url,
                        temperature=self.temperature,
                        verbose=self.verbose
                        # Note: Legacy Ollama doesn't support options parameter
                    )
                except ImportError:
                    # Fallback to deprecated version
                    from langchain_community.llms import Ollama
                    if self.verbose:
                        self.console.print(f"🦙 [{self.name}] Initializing Ollama (legacy) with model: {self.model_name}")
                    self.llm = Ollama(
                        model=self.model_name,
                        base_url=self.ollama_base_url,
                        temperature=self.temperature,
                        verbose=self.verbose
                        # Note: Legacy Ollama doesn't support options parameter
                    )
            elif self.use_lm_studio:
                # Use LM Studio for local testing (OpenAI-compatible API)
                if self.verbose:
                    self.console.print(f"🖥️ [{self.name}] Initializing LM Studio with model: {self.model_name}")
                # Quick connectivity check to fail fast instead of hanging
                try:
                    import httpx
                    httpx.get(f"{self.lm_studio_base_url}/v1/models", timeout=5.0)
                except Exception as e:
                    raise Exception(
                        f"Cannot reach LM Studio at {self.lm_studio_base_url}: {e}. Start LM Studio or set --no-lm-studio."
                    )

                # LM Studio provides an OpenAI-compatible API, so we can use ChatOpenAI
                self.llm = ChatOpenAI(
                    model=self.model_name,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    base_url=self.lm_studio_base_url + "/v1",  # LM Studio uses /v1 endpoint
                    api_key="not-needed",  # LM Studio doesn't require API key
                    verbose=self.verbose,
                    streaming=self.streaming,
                    timeout=self.request_timeout,
                )
                
                if self.verbose:
                    self.console.print(f"✅ [{self.name}] LM Studio initialized successfully")
                    
            elif self.model_name.startswith("gpt-"):
                self.llm = ChatOpenAI(
                    model=self.model_name,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    api_key=settings.openai_api_key,
                    verbose=self.verbose,
                    streaming=self.streaming,  # Enable streaming for OpenAI
                    timeout=self.request_timeout,
                )
            elif self.model_name.startswith("claude-"):
                if not settings.anthropic_api_key:
                    raise ValueError("Anthropic API key required for Claude models")
                self.llm = ChatAnthropic(
                    model=self.model_name,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    api_key=settings.anthropic_api_key,
                    verbose=self.verbose,
                    streaming=self.streaming  # Enable streaming for Anthropic
                )
            else:
                # Default to OpenAI
                self.llm = ChatOpenAI(
                    model=self.model_name,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    api_key=settings.openai_api_key,
                    verbose=self.verbose,
                    streaming=self.streaming,  # Enable streaming for OpenAI
                    timeout=self.request_timeout,
                )
        except ImportError as e:
            raise ImportError(f"Required package not installed: {e}")
        except Exception as e:
            raise Exception(f"Failed to initialize LLM: {e}")
    
    @abstractmethod
    async def process(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """Process the input data and return results.
        
        Args:
            input_data: Input data for the agent to process
            context: Additional context information
            
        Returns:
            Processed results
        """
        pass
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent.
        
        Returns:
            System prompt string
        """
        return f"You are {self.name}, {self.description}"
    
    def create_messages(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> list[BaseMessage]:
        """Create the message list for the LLM.
        
        Args:
            user_input: User input message
            context: Additional context information
            
        Returns:
            List of messages for the LLM
        """
        if self.use_ollama:
            # For Ollama, create a simple prompt string
            system_prompt = self.get_system_prompt()
            if context:
                context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
                return f"{system_prompt}\n\nContext:\n{context_str}\n\nUser Input:\n{user_input}"
            else:
                return f"{system_prompt}\n\nUser Input:\n{user_input}"
        else:
            # For other models, use structured messages
            messages = [
                {"role": "system", "content": self.get_system_prompt()}
            ]
            
            if context:
                context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
                messages.append({"role": "user", "content": f"Context:\n{context_str}\n\nUser Input:\n{user_input}"})
            else:
                messages.append({"role": "user", "content": user_input})
            
            return messages
    
    async def generate_response(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response using the LLM with streaming support.
        
        Args:
            user_input: User input message
            context: Additional context information
            
        Returns:
            Generated response
        """
        if self.verbose:
            self.console.print(Panel(
                f"[bold blue]🤖 {self.name}[/bold blue]\n"
                f"[cyan]Generating response...[/cyan]",
                title="[bold green]Agent Activity[/bold green]",
                border_style="blue"
            ))
            self.console.print(f"📝 [yellow]Input length:[/yellow] {len(user_input)} characters")
            if context:
                self.console.print(f"🔗 [yellow]Context keys:[/yellow] {list(context.keys())}")
        
        messages = self.create_messages(user_input, context)
        
        # Create streaming callback handler
        callbacks = None
        if self.verbose and self.streaming:
            callbacks = [StreamingCallbackHandler(self.name, self.console, self.verbose)]
        
        # Handle different input formats for Ollama vs other models
        try:
            import asyncio as _asyncio
            if self.use_ollama and isinstance(messages, str):
                # For Ollama with string prompt
                response = await _asyncio.wait_for(
                    self.llm.ainvoke(messages, config={"callbacks": callbacks}),
                    timeout=self.request_timeout,
                )
            else:
                # For other models with message list
                response = await _asyncio.wait_for(
                    self.llm.ainvoke(messages, config={"callbacks": callbacks}),
                    timeout=self.request_timeout,
                )
        except Exception as e:
            # Surface timeout clearly
            import asyncio as _asyncio
            if isinstance(e, _asyncio.TimeoutError):
                raise Exception(f"LLM request timed out after {self.request_timeout} seconds")
            if "Chunk too big" in str(e) or "too long" in str(e).lower():
                # Handle token limit issues by chunking the input
                if self.verbose:
                    self.console.print(f"⚠️ [{self.name}] Token limit exceeded, attempting to chunk input...")
                
                if self.use_ollama and isinstance(messages, str):
                    # Split the prompt into smaller chunks
                    chunked_response = await self._handle_chunked_input(messages, callbacks)
                    return chunked_response
                else:
                    # For message-based models, try to simplify the prompt
                    simplified_messages = self._simplify_messages(messages)
                    response = await self.llm.ainvoke(simplified_messages, config={"callbacks": callbacks})
                    return self._clean_response(self._extract_content(response))
            else:
                # Re-raise other errors
                raise
        
        # Handle different response types (Ollama vs other models)
        if hasattr(response, 'content'):
            response_content = response.content
        elif isinstance(response, str):
            response_content = response
        else:
            # Try to get content from different possible attributes
            response_content = getattr(response, 'text', str(response))
        
        # Clean the response content (remove thinking tags, etc.)
        response_content = self._clean_response(response_content)
        
        if self.verbose:
            self.console.print(Panel(
                f"[bold green]✅ {self.name}[/bold green]\n"
                f"[green]Response generated ({len(response_content)} characters)[/green]\n"
                f"[cyan]Preview:[/cyan] {response_content[:100]}...",
                title="[bold green]Response Complete[/bold green]",
                border_style="green"
            ))
        
        return response_content
    
    async def generate_response_streaming(self, user_input: str, context: Optional[Dict[str, Any]] = None, stream_mode: str = "updates") -> AsyncGenerator[str, None]:
        """Generate a streaming response using the LLM with enhanced streaming modes.
        
        Args:
            user_input: User input message
            context: Additional context information
            stream_mode: Streaming mode - "updates", "messages", "tokens", or "all"
            
        Yields:
            Generated response tokens as they arrive
        """
        if self.verbose:
            self.console.print(Panel(
                f"[bold blue]🤖 {self.name}[/bold blue]\n"
                f"[cyan]Starting streaming generation...[/cyan]\n"
                f"[yellow]Mode:[/yellow] {stream_mode}",
                title="[bold green]Agent Activity[/bold green]",
                border_style="blue"
            ))
        
        messages = self.create_messages(user_input, context)
        
        # Create enhanced streaming callback handler
        callbacks = None
        if self.verbose:
            callbacks = [StreamingCallbackHandler(self.name, self.console, self.verbose, stream_mode)]
        
        try:
            if self.use_ollama and isinstance(messages, str):
                # For Ollama, we'll need to handle streaming differently
                if self.verbose:
                    self.console.print(f"⚠️ [{self.name}] Ollama streaming not fully supported, falling back to regular generation")
                response = await self.llm.ainvoke(messages, config={"callbacks": callbacks})
                response_content = self._extract_content(response)
                yield response_content
            else:
                # For other models with streaming support
                if stream_mode == "tokens":
                    # Stream individual tokens
                    async for chunk in self.llm.astream(messages, config={"callbacks": callbacks}):
                        if hasattr(chunk, 'content'):
                            yield chunk.content
                        elif isinstance(chunk, str):
                            yield chunk
                        else:
                            yield str(chunk)
                elif stream_mode == "messages":
                    # Stream complete messages
                    async for chunk in self.llm.astream(messages, config={"callbacks": callbacks}):
                        if hasattr(chunk, 'content'):
                            yield chunk.content
                        elif isinstance(chunk, str):
                            yield chunk
                        else:
                            yield str(chunk)
                elif stream_mode == "updates":
                    # Stream updates with metadata
                    async for chunk in self.llm.astream(messages, config={"callbacks": callbacks}):
                        if hasattr(chunk, 'content'):
                            yield chunk.content
                        elif isinstance(chunk, str):
                            yield chunk
                        else:
                            yield str(chunk)
                elif stream_mode == "all":
                    # Stream everything with enhanced metadata
                    async for chunk in self.llm.astream(messages, config={"callbacks": callbacks}):
                        if hasattr(chunk, 'content'):
                            yield chunk.content
                        elif isinstance(chunk, str):
                            yield chunk
                        else:
                            yield str(chunk)
                else:
                    # Default to token streaming
                    async for chunk in self.llm.astream(messages, config={"callbacks": callbacks}):
                        if hasattr(chunk, 'content'):
                            yield chunk.content
                        elif isinstance(chunk, str):
                            yield chunk
                        else:
                            yield str(chunk)
        except Exception as e:
            if self.verbose:
                self.console.print(f"❌ [{self.name}] Streaming generation failed: {e}")
                self.console.print(f"🔄 [{self.name}] Falling back to regular generation...")
            # Fallback to regular generation
            response = await self.generate_response(user_input, context)
            yield response
    
    async def _handle_chunked_input(self, prompt: str, callbacks) -> str:
        """Handle long prompts by splitting them into smaller chunks.
        
        Args:
            prompt: The full prompt that was too long
            callbacks: Callback handlers for logging
            
        Returns:
            Combined response from chunked processing
        """
        # Split the prompt into smaller chunks (roughly 2000 characters each)
        chunk_size = 2000
        chunks = []
        
        # Split by paragraphs first, then by sentences if needed
        paragraphs = prompt.split('\n\n')
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) < chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        if self.verbose:
            self.console.print(f"📝 [{self.name}] Split prompt into {len(chunks)} chunks")
        
        # Process each chunk and combine results
        responses = []
        for i, chunk in enumerate(chunks):
            if self.verbose:
                self.console.print(f"🔄 [{self.name}] Processing chunk {i+1}/{len(chunks)}...")
            
            try:
                chunk_response = await self.llm.ainvoke(chunk, config={"callbacks": callbacks})
                chunk_content = self._extract_content(chunk_response)
                responses.append(chunk_content)
            except Exception as e:
                if self.verbose:
                    self.console.print(f"⚠️ [{self.name}] Chunk {i+1} failed: {e}")
                # Continue with other chunks
                continue
        
        # Combine all responses
        combined_response = "\n\n".join(responses)
        return combined_response
    
    def _extract_content(self, response) -> str:
        """Extract content from response object or string."""
        if hasattr(response, 'content'):
            return response.content
        elif isinstance(response, str):
            return response
        else:
            return getattr(response, 'text', str(response))
    
    def _simplify_messages(self, messages: list) -> list:
        """Simplify messages to reduce token count."""
        simplified = []
        for msg in messages:
            if isinstance(msg, dict):
                # Keep only essential content, truncate if too long
                content = msg.get('content', '')
                if len(content) > 1000:
                    content = content[:1000] + "..."
                simplified.append({"role": msg.get('role', 'user'), "content": content})
        return simplified
    
    def _clean_response(self, response: str) -> str:
        """Clean the response content by removing thinking tags and other artifacts.
        
        Args:
            response: Raw response from the LLM
            
        Returns:
            Cleaned response content
        """
        if not response:
            return ""
        
        # Remove thinking tags and their content
        import re
        
        # Remove <think>...</think> blocks
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        
        # Remove <|im_start|> and <|im_end|> tags
        response = re.sub(r'<\|im_start\|.*?<\|im_end\|>', '', response, flags=re.DOTALL)
        
        # Remove other common thinking patterns
        response = re.sub(r'<|im_start|>.*?<|im_end|>', '', response, flags=re.DOTALL)
        response = re.sub(r'<|system|>.*?<|user|>', '', response, flags=re.DOTALL)
        
        # Clean up extra whitespace
        response = re.sub(r'\n\s*\n\s*\n', '\n\n', response)
        response = response.strip()
        
        return response
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.name}: {self.description}"
    
    def __repr__(self) -> str:
        """Detailed string representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.name}', model='{self.model_name}')"
