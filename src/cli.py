"""
Command-line interface for the I'm Poster blog generator.
"""

# Disable LangSmith by default to prevent API calls
import os
os.environ["LANGCHAIN_TRACING"] = "false"
os.environ["LANGCHAIN_ENDPOINT"] = ""
os.environ["LANGCHAIN_API_KEY"] = ""
os.environ["LANGCHAIN_PROJECT"] = ""
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_CALLBACKS"] = ""

import asyncio
import sys
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

import typer
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .core.blog_generator import BlogGenerator
from .core.models import BlogType
from .cli_prompts import (
    show_welcome_banner,
    rich_select,
    rich_text_prompt,
    rich_goals_prompt,
    rich_confirm,
    rich_blog_type_select,
    rich_backend_select,
    show_config_summary,
)

# Initialize Typer app
app = typer.Typer(
    name="im-poster",
    help="I'm Poster - Multi-Agent AI Blog Generator",
    add_completion=False,
    invoke_without_command=True,
)

# Initialize Rich console
console = Console()


@app.callback(invoke_without_command=True)
def default_interactive(ctx: typer.Context):
    """Launch interactive mode when no subcommand is provided."""
    if ctx.invoked_subcommand is not None:
        return

    show_welcome_banner()

    blog_type = rich_blog_type_select()

    if blog_type == "tech_blog":
        _interactive_tech_blog()
    elif blog_type == "tutorial":
        _interactive_tutorial()
    elif blog_type == "comparison":
        _interactive_comparison()


def _interactive_tech_blog():
    """Full interactive flow for tech blog generation."""
    topic = rich_text_prompt("Blog Topic", hint="e.g. Building Multi-Agent Systems with LangGraph")
    goals = rich_goals_prompt("Blog Goals")
    target_audience = rich_text_prompt("Target Audience", default="developers")
    tone = rich_select("Tone", ["friendly", "professional", "humorous", "technical"], default="friendly")
    length = rich_select("Length", ["short", "medium", "long"], default="medium")
    include_code = rich_confirm("Include code examples?", default=True)
    include_diagrams = rich_confirm("Include diagrams?", default=False)

    backend_choice = rich_backend_select()
    use_ollama = backend_choice == "ollama"
    use_lm_studio = backend_choice == "lm-studio"

    custom_instructions = rich_text_prompt("Custom instructions (optional)", default="")
    output_file = rich_text_prompt("Output filename (optional, leave blank for auto)", default="")

    show_config_summary({
        "topic": topic,
        "goals": goals,
        "audience": target_audience,
        "tone": tone,
        "length": length,
        "code_examples": include_code,
        "diagrams": include_diagrams,
        "backend": backend_choice,
    }, blog_type="tech_blog")

    if not rich_confirm("Proceed with generation?", default=True):
        console.print("[yellow]Generation cancelled.[/yellow]")
        return

    session_data = {
        "blog_type": "tech_blog",
        "topic": topic,
        "goals": goals,
        "target_audience": target_audience,
        "tone": tone,
        "length": length,
        "include_code_examples": include_code,
        "include_diagrams": include_diagrams,
        "custom_instructions": custom_instructions or None,
        "output_file": output_file or None,
        "use_ollama": use_ollama,
        "use_lm_studio": use_lm_studio,
    }
    _save_session_file(session_data)

    asyncio.run(_generate_blog(
        blog_type="tech_blog",
        topic=topic,
        goals=goals,
        target_audience=target_audience,
        tone=tone,
        length=length,
        include_code_examples=include_code,
        include_diagrams=include_diagrams,
        custom_instructions=custom_instructions or None,
        output_file=output_file or None,
        use_ollama=use_ollama,
        use_lm_studio=use_lm_studio,
    ))


def _interactive_tutorial():
    """Full interactive flow for tutorial generation."""
    topic = rich_text_prompt("Tutorial Topic", hint="e.g. Getting Started with Docker for Beginners")
    goals = rich_goals_prompt("Learning Goals")
    difficulty = rich_select("Difficulty Level", ["beginner", "intermediate", "advanced"], default="intermediate")
    target_audience = rich_text_prompt("Target Audience", default="developers")
    tone = rich_select("Tone", ["friendly", "professional", "humorous", "technical"], default="friendly")
    length = rich_select("Length", ["short", "medium", "long"], default="medium")
    include_code = rich_confirm("Include code examples?", default=True)

    backend_choice = rich_backend_select()
    use_ollama = backend_choice == "ollama"
    use_lm_studio = backend_choice == "lm-studio"

    ollama_base_url = None
    ollama_model = None
    lm_studio_base_url = None
    lm_studio_model = None

    if use_ollama:
        ollama_model = _prompt_ollama_model(ollama_base_url)
    elif use_lm_studio:
        lm_studio_model = rich_text_prompt("LM Studio model name", default="local-model")

    streaming = rich_confirm("Enable streaming output?", default=True)
    stream_mode = "updates"
    if streaming:
        stream_mode = rich_select("Streaming mode", ["updates", "messages", "tokens", "all"], default="updates")

    custom_instructions = rich_text_prompt("Custom instructions (optional)", default="")
    output_file = rich_text_prompt("Output filename (optional, leave blank for auto)", default="")

    show_config_summary({
        "topic": topic,
        "goals": goals,
        "difficulty": difficulty,
        "audience": target_audience,
        "tone": tone,
        "length": length,
        "code_examples": include_code,
        "backend": backend_choice,
        "streaming": streaming,
        "stream_mode": stream_mode,
    }, blog_type="tutorial")

    if not rich_confirm("Proceed with generation?", default=True):
        console.print("[yellow]Generation cancelled.[/yellow]")
        return

    session_data = {
        "blog_type": "tutorial",
        "topic": topic,
        "goals": goals,
        "difficulty": difficulty,
        "target_audience": target_audience,
        "tone": tone,
        "length": length,
        "include_code_examples": include_code,
        "include_diagrams": False,
        "custom_instructions": custom_instructions or None,
        "output_file": output_file or None,
        "use_ollama": use_ollama,
        "ollama_base_url": ollama_base_url,
        "ollama_model": ollama_model,
        "use_lm_studio": use_lm_studio,
        "lm_studio_base_url": lm_studio_base_url,
        "lm_studio_model": lm_studio_model,
        "streaming": streaming,
        "stream_mode": stream_mode,
    }
    _save_session_file(session_data)

    asyncio.run(_generate_blog(
        blog_type="tutorial",
        topic=topic,
        goals=goals,
        difficulty=difficulty,
        target_audience=target_audience,
        tone=tone,
        length=length,
        include_code_examples=include_code,
        include_diagrams=False,
        custom_instructions=custom_instructions or None,
        output_file=output_file or None,
        use_ollama=use_ollama,
        ollama_base_url=ollama_base_url,
        ollama_model=ollama_model,
        use_lm_studio=use_lm_studio,
        lm_studio_base_url=lm_studio_base_url,
        lm_studio_model=lm_studio_model,
        streaming=streaming,
        stream_mode=stream_mode,
    ))


def _interactive_comparison():
    """Full interactive flow for comparison blog generation."""
    topic = rich_text_prompt("Comparison Topic", hint="e.g. React vs Vue vs Svelte")

    console.print()
    console.print("  [bold yellow]Items to Compare[/bold yellow]")
    console.print("  [dim]Enter items one per line. Press Enter on an empty line to finish (min 2).[/dim]")
    items: list[str] = []
    idx = 1
    while True:
        from rich.prompt import Prompt
        item = Prompt.ask(f"  [cyan]Item {idx}[/cyan]", default="")
        item = item.strip()
        if not item:
            if len(items) < 2:
                console.print("  [red]At least two items are required.[/red]")
                continue
            break
        items.append(item)
        idx += 1

    goals = rich_goals_prompt("Comparison Goals")
    target_audience = rich_text_prompt("Target Audience", default="developers")
    tone = rich_select("Tone", ["friendly", "professional", "humorous", "technical"], default="friendly")
    length = rich_select("Length", ["short", "medium", "long"], default="medium")
    include_code = rich_confirm("Include code examples?", default=True)

    backend_choice = rich_backend_select()
    use_ollama = backend_choice == "ollama"
    use_lm_studio = backend_choice == "lm-studio"

    custom_instructions = rich_text_prompt("Custom instructions (optional)", default="")
    output_file = rich_text_prompt("Output filename (optional, leave blank for auto)", default="")

    show_config_summary({
        "topic": topic,
        "items": items,
        "goals": goals,
        "audience": target_audience,
        "tone": tone,
        "length": length,
        "code_examples": include_code,
        "backend": backend_choice,
    }, blog_type="comparison")

    if not rich_confirm("Proceed with generation?", default=True):
        console.print("[yellow]Generation cancelled.[/yellow]")
        return

    session_data = {
        "blog_type": "comparison",
        "topic": topic,
        "items": items,
        "goals": goals,
        "target_audience": target_audience,
        "tone": tone,
        "length": length,
        "include_code_examples": include_code,
        "include_diagrams": False,
        "custom_instructions": custom_instructions or None,
        "output_file": output_file or None,
        "use_ollama": use_ollama,
        "use_lm_studio": use_lm_studio,
    }
    _save_session_file(session_data)

    asyncio.run(_generate_blog(
        blog_type="comparison",
        topic=topic,
        items=items,
        goals=goals,
        target_audience=target_audience,
        tone=tone,
        length=length,
        include_code_examples=include_code,
        include_diagrams=False,
        custom_instructions=custom_instructions or None,
        output_file=output_file or None,
        use_ollama=use_ollama,
        use_lm_studio=use_lm_studio,
    ))


def _prompt_ollama_model(ollama_base_url: Optional[str] = None) -> str:
    """Fetch available Ollama models and prompt user to select one."""
    try:
        import httpx
        response = httpx.get(f"{ollama_base_url or 'http://localhost:11434'}/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                model_names = [model["name"] for model in models]
                return rich_select("Ollama Model", model_names, default=model_names[0])
    except Exception:
        pass
    return rich_text_prompt("Ollama model name", hint="e.g. llama2, codellama")


@app.command()
def generate_tech_blog(
    topic: Optional[str] = typer.Option(None, "--topic", "-t", help="Main topic of the blog post (will prompt if not provided)"),
    goals: List[str] = typer.Option([], "--goal", "-g", help="Goals to achieve (can specify multiple, will prompt if not provided)"),
    target_audience: str = typer.Option("developers", "--audience", "-a", help="Target audience"),
    tone: str = typer.Option("friendly", "--tone", help="Tone of the blog"),
    length: str = typer.Option("medium", "--length", "-l", help="Length of the blog"),
    include_code: bool = typer.Option(True, "--code/--no-code", help="Include code examples"),
    include_diagrams: bool = typer.Option(False, "--diagrams/--no-diagrams", help="Include diagrams"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output filename"),
    custom_instructions: Optional[str] = typer.Option(None, "--instructions", help="Custom instructions"),
    backend: Optional[str] = typer.Option(None, "--backend", help="LLM backend: openai, lm-studio, or ollama", case_sensitive=False),
    resume: Optional[str] = typer.Option(None, "--resume", "-r", help="Resume from a session file")
):
    """Generate a tech blog post with interactive prompts for missing parameters."""
    
    # Check if resuming from a session
    if resume:
        try:
            session_path = Path(resume)
            if not session_path.exists():
                console.print(f"[red]❌ Session file '{resume}' not found.[/red]")
                return
            
            # Load session parameters
            import json
            with open(session_path, 'r') as f:
                session_data = json.load(f)
            
            console.print(Panel(
                f"[bold blue]🔄 Resuming Tech Blog Generation[/bold blue]\n"
                f"📁 Session: {session_path.name}\n"
                f"📝 Topic: {session_data.get('topic', 'N/A')}\n"
                f"🎯 Goals: {', '.join(session_data.get('goals', []))}",
                title="[bold green]Resume Session[/bold green]",
                border_style="green"
            ))
            
            # Resume the generation
            asyncio.run(_generate_blog_from_session(session_data, False))
            return
            
        except Exception as e:
            console.print(f"[red]❌ Error resuming generation: {e}[/red]")
            return
    
    # Interactive prompts for missing parameters using Rich UI
    if not topic:
        topic = rich_text_prompt("Blog Topic", hint="What topic would you like to create a tech blog about?")

    if not goals:
        goals = rich_goals_prompt("Blog Goals")

    show_config_summary({
        "topic": topic,
        "goals": goals,
        "audience": target_audience,
        "tone": tone,
        "length": length,
        "code_examples": include_code,
        "diagrams": include_diagrams,
    }, blog_type="tech_blog")

    # Resolve backend selection
    use_ollama = False
    use_lm_studio = False
    if backend:
        backend_lc = backend.lower()
        if backend_lc not in ["openai", "lm-studio", "ollama"]:
            console.print("[red]Invalid --backend. Use: openai, lm-studio, or ollama[/red]")
            raise typer.Exit(code=1)
        if backend_lc == "lm-studio":
            use_lm_studio = True
        elif backend_lc == "ollama":
            use_ollama = True

    # Store session parameters
    session_data = {
        "blog_type": "tech_blog",
        "topic": topic,
        "goals": goals,
        "target_audience": target_audience,
        "tone": tone,
        "length": length,
        "include_code_examples": include_code,
        "include_diagrams": include_diagrams,
        "custom_instructions": custom_instructions,
        "output_file": output_file,
        "use_ollama": use_ollama,
        "use_lm_studio": use_lm_studio,
        "timestamp": None
    }
    
    # Save session file
    _save_session_file(session_data)
    
    asyncio.run(_generate_blog(
        blog_type="tech_blog",
        topic=topic,
        goals=goals,
        target_audience=target_audience,
        tone=tone,
        length=length,
        include_code_examples=include_code,
        include_diagrams=include_diagrams,
        custom_instructions=custom_instructions,
        output_file=output_file,
        use_ollama=use_ollama,
        use_lm_studio=use_lm_studio
    ))


@app.command()
def generate_tutorial(
    topic: str = typer.Option(None, "--topic", "-t", help="Main topic of the tutorial (will prompt if not provided)"),
    goals: List[str] = typer.Option([], "--goal", "-g", help="Learning goals (can specify multiple, will prompt if not provided)"),
    difficulty: str = typer.Option(None, "--difficulty", "-d", help="Difficulty level (will prompt if not provided)"),
    target_audience: str = typer.Option(None, "--audience", "-a", help="Target audience (will prompt if not provided)"),
    tone: str = typer.Option(None, "--tone", help="Tone of the tutorial (will prompt if not provided)"),
    length: str = typer.Option(None, "--length", "-l", help="Length of the tutorial (will prompt if not provided)"),
    include_code: bool = typer.Option(None, "--code/--no-code", help="Include code examples (will prompt if not provided)"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output filename"),
    custom_instructions: Optional[str] = typer.Option(None, "--instructions", help="Custom instructions"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    backend: Optional[str] = typer.Option(None, "--backend", help="LLM backend: openai, lm-studio, or ollama", case_sensitive=False),
    use_ollama: bool = typer.Option(None, "--ollama", help="Use Ollama for local testing (will prompt if not provided)"),
    ollama_base_url: Optional[str] = typer.Option(None, "--ollama-url", help="Ollama base URL (default: http://localhost:11434)"),
    ollama_model: Optional[str] = typer.Option(None, "--ollama-model", help="Ollama model to use (will prompt if not provided)"),
    use_lm_studio: bool = typer.Option(None, "--lm-studio", help="Use LM Studio for local testing (will prompt if not provided)"),
    lm_studio_base_url: Optional[str] = typer.Option(None, "--lm-studio-url", help="LM Studio base URL (default: http://localhost:1234)"),
    lm_studio_model: Optional[str] = typer.Option(None, "--lm-studio-model", help="LM Studio model to use (will prompt if not provided)"),
    streaming: bool = typer.Option(True, "--streaming/--no-streaming", help="Enable streaming output for real-time agent thinking and LLM responses"),
    stream_mode: str = typer.Option("updates", "--stream-mode", help="Streaming mode: updates, messages, tokens, or all"),
    resume: Optional[str] = typer.Option(None, "--resume", "-r", help="Resume from a session file")
):
    """Generate a tutorial blog post with interactive prompts for missing parameters."""
    
    # Check if resuming from a session
    if resume:
        try:
            session_path = Path(resume)
            if not session_path.exists():
                console.print(f"[red]❌ Session file '{resume}' not found.[/red]")
                return
            
            # Load session parameters
            import json
            with open(session_path, 'r') as f:
                session_data = json.load(f)
            
            console.print(Panel(
                f"[bold blue]🔄 Resuming Tutorial Generation[/bold blue]\n"
                f"📁 Session: {session_path.name}\n"
                f"📝 Topic: {session_data.get('topic', 'N/A')}\n"
                f"🎯 Goals: {', '.join(session_data.get('goals', []))}",
                title="[bold green]Resume Session[/bold green]",
                border_style="green"
            ))
            
            # Resume the generation
            asyncio.run(_generate_blog_from_session(session_data, verbose))
            return
            
        except Exception as e:
            console.print(f"[red]❌ Error resuming generation: {e}[/red]")
            return
    
    # Interactive prompts for missing parameters using Rich UI
    if not topic:
        topic = rich_text_prompt("Tutorial Topic", hint="What topic would you like to create a tutorial about?")

    if not goals:
        goals = rich_goals_prompt("Learning Goals")

    if not difficulty:
        difficulty = rich_select("Difficulty Level", ["beginner", "intermediate", "advanced"], default="intermediate")

    if not target_audience:
        target_audience = rich_text_prompt("Target Audience", default="developers")

    if not tone:
        tone = rich_select("Tone", ["friendly", "professional", "humorous", "technical"], default="friendly")

    if not length:
        length = rich_select("Length", ["short", "medium", "long"], default="medium")

    if include_code is None:
        include_code = rich_confirm("Include code examples?", default=True)
    
    # Backend override (openai, lm-studio, ollama)
    if backend:
        backend_lc = backend.lower()
        if backend_lc not in ["openai", "lm-studio", "ollama"]:
            console.print("[red]Invalid --backend. Use: openai, lm-studio, or ollama[/red]")
            raise typer.Exit(code=1)
        if backend_lc == "openai":
            use_ollama = False
            use_lm_studio = False
        elif backend_lc == "lm-studio":
            use_lm_studio = True
            use_ollama = False
        elif backend_lc == "ollama":
            use_ollama = True
            use_lm_studio = False

    # Handle local model selection logic when no backend provided
    if use_ollama is None and use_lm_studio is None and not backend:
        backend_choice = rich_backend_select()
        use_ollama = backend_choice == "ollama"
        use_lm_studio = backend_choice == "lm-studio"
    elif use_ollama is None and use_lm_studio:
        # LM Studio specified, set Ollama to False
        use_ollama = False
    elif use_ollama and use_lm_studio is None:
        # Ollama specified, set LM Studio to False
        use_lm_studio = False
    
    # Ensure only one local model is selected
    if use_ollama and use_lm_studio:
        console.print("[red]⚠️ Warning: Both Ollama and LM Studio selected. Using Ollama as default.[/red]")
        use_lm_studio = False
    
    if use_ollama and not ollama_model:
        ollama_model = _prompt_ollama_model(ollama_base_url)

    if use_lm_studio and not lm_studio_model:
        lm_studio_model = rich_text_prompt("LM Studio model name", default="local-model")
    
    # Store session parameters
    session_data = {
        "blog_type": "tutorial",
        "topic": topic,
        "goals": goals,
        "difficulty": difficulty,
        "target_audience": target_audience,
        "tone": tone,
        "length": length,
        "include_code_examples": include_code,
        "include_diagrams": False,
        "custom_instructions": custom_instructions,
        "output_file": output_file,
        "verbose": verbose,
        "use_ollama": use_ollama,
        "ollama_base_url": ollama_base_url,
        "ollama_model": ollama_model,
        "use_lm_studio": use_lm_studio,
        "lm_studio_base_url": lm_studio_base_url,
        "lm_studio_model": lm_studio_model,
        "streaming": streaming,
        "stream_mode": stream_mode,
        "timestamp": None
    }
    
    # Save session file
    _save_session_file(session_data)
    
    # Display configuration
    backend_name = "lm-studio" if use_lm_studio else ("ollama" if use_ollama else "openai")
    show_config_summary({
        "topic": topic,
        "goals": goals,
        "difficulty": difficulty,
        "audience": target_audience,
        "tone": tone,
        "length": length,
        "code_examples": include_code,
        "backend": backend_name,
        "streaming": streaming,
        "stream_mode": stream_mode,
    }, blog_type="tutorial")
    
    if streaming and verbose:
        console.print(Panel(
            f"[bold green]📡 Streaming Mode Enabled[/bold green]\n"
            f"[cyan]You'll see real-time agent thinking and LLM responses![/cyan]\n"
            f"[yellow]Mode:[/yellow] {stream_mode}",
            title="[bold green]Streaming Output[/bold green]",
            border_style="green"
        ))
    
    # Generate the tutorial
    asyncio.run(_generate_blog(
        blog_type="tutorial",
        topic=topic,
        goals=goals,
        difficulty=difficulty,
        target_audience=target_audience,
        tone=tone,
        length=length,
        include_code_examples=include_code,
        include_diagrams=False,
        custom_instructions=custom_instructions,
        output_file=output_file,
        verbose=verbose,
        use_ollama=use_ollama,
        ollama_base_url=ollama_base_url,
        ollama_model=ollama_model,
        use_lm_studio=use_lm_studio,
        lm_studio_base_url=lm_studio_base_url,
        lm_studio_model=lm_studio_model,
        streaming=streaming,
        stream_mode=stream_mode
    ))


@app.command()
def generate_comparison(
    topic: str = typer.Argument(..., help="Main topic of the comparison"),
    items: List[str] = typer.Option([], "--item", "-i", help="Items to compare (can specify multiple)"),
    goals: List[str] = typer.Option([], "--goal", "-g", help="Goals to achieve (can specify multiple)"),
    target_audience: str = typer.Option("developers", "--audience", "-a", help="Target audience"),
    tone: str = typer.Option("friendly", "--tone", help="Tone of the blog"),
    length: str = typer.Option("medium", "--length", "-l", help="Length of the blog"),
    include_code: bool = typer.Option(True, "--code/--no-code", help="Include code examples"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output filename"),
    custom_instructions: Optional[str] = typer.Option(None, "--instructions", help="Custom instructions"),
    backend: Optional[str] = typer.Option(None, "--backend", help="LLM backend: openai, lm-studio, or ollama", case_sensitive=False),
    resume: Optional[str] = typer.Option(None, "--resume", "-r", help="Resume from a session file")
):
    """Generate a comparison blog post."""
    
    # Check if resuming from a session
    if resume:
        try:
            session_path = Path(resume)
            if not session_path.exists():
                console.print(f"[red]❌ Session file '{resume}' not found.[/red]")
                return
            
            # Load session parameters
            import json
            with open(session_path, 'r') as f:
                session_data = json.load(f)
            
            console.print(Panel(
                f"[bold blue]🔄 Resuming Comparison Generation[/bold blue]\n"
                f"📁 Session: {session_path.name}\n"
                f"📝 Topic: {session_data.get('topic', 'N/A')}\n"
                f"🎯 Goals: {', '.join(session_data.get('goals', []))}",
                title="[bold green]Resume Session[/bold green]",
                border_style="green"
            ))
            
            # Resume the generation
            asyncio.run(_generate_blog_from_session(session_data, False))
            return
            
        except Exception as e:
            console.print(f"[red]❌ Error resuming generation: {e}[/red]")
            return
    
    if not items:
        console.print("[red]Error: At least two items must be specified with --item[/red]")
        sys.exit(1)
    
    if len(items) < 2:
        console.print("[red]Error: At least two items are required for comparison[/red]")
        sys.exit(1)
    
    if not goals:
        console.print("[red]Error: At least one goal must be specified with --goal[/red]")
        sys.exit(1)
    
    # Resolve backend selection
    use_ollama = False
    use_lm_studio = False
    if backend:
        backend_lc = backend.lower()
        if backend_lc not in ["openai", "lm-studio", "ollama"]:
            console.print("[red]Invalid --backend. Use: openai, lm-studio, or ollama[/red]")
            raise typer.Exit(code=1)
        if backend_lc == "lm-studio":
            use_lm_studio = True
        elif backend_lc == "ollama":
            use_ollama = True

    # Store session parameters
    session_data = {
        "blog_type": "comparison",
        "topic": topic,
        "items": items,
        "goals": goals,
        "target_audience": target_audience,
        "tone": tone,
        "length": length,
        "include_code_examples": include_code,
        "include_diagrams": False,
        "custom_instructions": custom_instructions,
        "output_file": output_file,
        "use_ollama": use_ollama,
        "use_lm_studio": use_lm_studio,
        "timestamp": None
    }
    
    # Save session file
    _save_session_file(session_data)
    
    backend_name = "lm-studio" if use_lm_studio else ("ollama" if use_ollama else "openai")
    show_config_summary({
        "topic": topic,
        "items": items,
        "goals": goals,
        "audience": target_audience,
        "tone": tone,
        "length": length,
        "code_examples": include_code,
        "backend": backend_name,
    }, blog_type="comparison")
    
    asyncio.run(_generate_blog(
        blog_type="comparison",
        topic=topic,
        items=items,
        goals=goals,
        target_audience=target_audience,
        tone=tone,
        length=length,
        include_code_examples=include_code,
        include_diagrams=False,
        custom_instructions=custom_instructions,
        output_file=output_file,
        use_ollama=use_ollama,
        use_lm_studio=use_lm_studio
    ))


@app.command()
def list_blogs():
    """List all generated blog posts."""
    try:
        generator = BlogGenerator()
        blogs = generator.list_generated_blogs()
        
        if not blogs:
            console.print("[yellow]No generated blogs found.[/yellow]")
            return
        
        table = Table(title="Generated Blog Posts")
        table.add_column("Filename", style="cyan")
        table.add_column("Size", style="green")
        table.add_column("Created", style="yellow")
        
        for blog in blogs:
            file_path = Path(generator.get_status()["output_directory"]) / blog
            if file_path.exists():
                stat = file_path.stat()
                size = f"{stat.st_size / 1024:.1f} KB"
                created = f"{stat.st_ctime:.0f}"
                table.add_row(blog, size, created)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error listing blogs: {e}[/red]")


@app.command()
def show_blog(
    filename: str = typer.Argument(..., help="Name of the blog file to display")
):
    """Show the content of a generated blog post."""
    try:
        generator = BlogGenerator()
        content = generator.get_blog_content(filename)
        
        if content is None:
            console.print(f"[red]Blog file '{filename}' not found.[/red]")
            return
        
        console.print(Panel(content, title=f"Blog: {filename}", expand=False))
        
    except Exception as e:
        console.print(f"[red]Error showing blog: {e}[/red]")


@app.command()
def status():
    """Show the current status of the blog generator."""
    try:
        generator = BlogGenerator()
        status_info = generator.get_status()
        
        console.print(Panel("[bold blue]I'm Poster Blog Generator Status[/bold blue]"))
        
        # Agent status
        agent_table = Table(title="Agent Status")
        agent_table.add_column("Agent", style="cyan")
        agent_table.add_column("Status", style="green")
        
        for agent_name in status_info["orchestrator_status"]["agents"].values():
            agent_table.add_row(agent_name, "✅ Active")
        
        console.print(agent_table)
        
        # Configuration
        config_table = Table(title="Configuration")
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="green")
        
        config_table.add_row("Output Directory", status_info["output_directory"])
        config_table.add_row("Template Directory", status_info["template_directory"])
        config_table.add_row("ChromaDB Host", status_info["chroma_host"])
        config_table.add_row("Default Model", status_info["default_model"])
        
        console.print(config_table)
        
    except Exception as e:
        console.print(f"[red]Error getting status: {e}[/red]")


@app.command()
def resume_generation(
    session_file: str = typer.Argument(..., help="Path to the session file to resume from"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    backend: Optional[str] = typer.Option(None, "--backend", help="LLM backend: openai, lm-studio, or ollama", case_sensitive=False),
    openai: bool = typer.Option(False, "--openai", help="Force OpenAI backend (disables LM Studio and Ollama)"),
    lm_studio: Optional[bool] = typer.Option(None, "--lm-studio/--no-lm-studio", help="Enable or disable LM Studio for this resume"),
    ollama: Optional[bool] = typer.Option(None, "--ollama/--no-ollama", help="Enable or disable Ollama for this resume"),
    streaming: Optional[bool] = typer.Option(None, "--streaming/--no-streaming", help="Enable or disable streaming for this resume"),
    stream_mode: Optional[str] = typer.Option(None, "--stream-mode", help="Streaming mode: updates, messages, tokens, or all")
):
    """Resume a blog generation from a saved session file."""
    try:
        session_path = Path(session_file)
        if not session_path.exists():
            console.print(f"[red]❌ Session file '{session_file}' not found.[/red]")
            return
        
        # Load session parameters
        import json
        with open(session_path, 'r') as f:
            session_data = json.load(f)
        
        console.print(Panel(
            f"[bold blue]🔄 Resuming Blog Generation[/bold blue]\n"
            f"📁 Session: {session_path.name}\n"
            f"📝 Topic: {session_data.get('topic', 'N/A')}\n"
            f"🎯 Goals: {', '.join(session_data.get('goals', []))}\n"
            f"📊 Type: {session_data.get('blog_type', 'N/A')}",
            title="[bold green]Resume Session[/bold green]",
            border_style="green"
        ))
        # Allow backend and streaming overrides at resume time
        if backend:
            backend_lc = backend.lower()
            if backend_lc not in ["openai", "lm-studio", "ollama"]:
                console.print("[red]Invalid --backend. Use: openai, lm-studio, or ollama[/red]")
                raise typer.Exit(code=1)
            if backend_lc == "openai":
                session_data["use_lm_studio"] = False
                session_data["use_ollama"] = False
            elif backend_lc == "lm-studio":
                session_data["use_lm_studio"] = True
                session_data["use_ollama"] = False
            elif backend_lc == "ollama":
                session_data["use_ollama"] = True
                session_data["use_lm_studio"] = False
        if openai:
            session_data["use_lm_studio"] = False
            session_data["use_ollama"] = False
        if lm_studio is not None:
            session_data["use_lm_studio"] = lm_studio
            if lm_studio:
                session_data["use_ollama"] = False
        if ollama is not None:
            session_data["use_ollama"] = ollama
            if ollama:
                session_data["use_lm_studio"] = False
        if streaming is not None:
            session_data["streaming"] = streaming
        if stream_mode is not None:
            session_data["stream_mode"] = stream_mode

        # Show a quick summary of effective config when verbose
        if verbose:
            backend = (
                "LM Studio" if session_data.get("use_lm_studio") else
                ("Ollama" if session_data.get("use_ollama") else "OpenAI")
            )
            console.print(Panel(
                f"[bold blue]⚙️ Effective Resume Config[/bold blue]\n"
                f"Backend: {backend}\n"
                f"Streaming: {'On' if session_data.get('streaming', True) else 'Off'}"
                + (f" (Mode: {session_data.get('stream_mode', 'updates')})" if session_data.get('streaming', True) else ""),
                title="[bold green]Resume Overrides[/bold green]",
                border_style="blue"
            ))

        # Resume the generation
        asyncio.run(_generate_blog_from_session(session_data, verbose))
        
    except Exception as e:
        console.print(f"[red]❌ Error resuming generation: {e}[/red]")
        sys.exit(1)


@app.command()
def list_sessions():
    """List all available session files for resuming blog generation."""
    try:
        sessions_dir = Path("blogs/works")
        if not sessions_dir.exists():
            console.print("[yellow]No sessions directory found.[/yellow]")
            return
        
        session_files = list(sessions_dir.glob("*.json"))
        if not session_files:
            console.print("[yellow]No session files found.[/yellow]")
            return
        
        table = Table(title="Available Session Files")
        table.add_column("Session File", style="cyan")
        table.add_column("Topic", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Created", style="blue")
        table.add_column("Size", style="magenta")
        
        for session_file in sorted(session_files, key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                topic = session_data.get('topic', 'N/A')
                blog_type = session_data.get('blog_type', 'N/A')
                created = f"{session_file.stat().st_mtime:.0f}"
                size = f"{session_file.stat().st_size / 1024:.1f} KB"
                
                table.add_row(session_file.name, topic, blog_type, created, size)
            except Exception as e:
                table.add_row(session_file.name, "Error", "Error", "Error", "Error")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error listing sessions: {e}[/red]")


@app.command()
def delete_session(
    session_file: str = typer.Argument(..., help="Name of the session file to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Force deletion without confirmation")
):
    """Delete a session file."""
    try:
        session_path = Path("blogs/works") / session_file
        if not session_path.exists():
            console.print(f"[red]❌ Session file '{session_file}' not found.[/red]")
            return
        
        if not force:
            if not typer.confirm(f"Are you sure you want to delete '{session_file}'?"):
                console.print("[yellow]Deletion cancelled.[/yellow]")
                return
        
        session_path.unlink()
        console.print(f"[green]✅ Session file '{session_file}' deleted successfully.[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Error deleting session: {e}[/red]")


def _save_session_file(session_data: Dict[str, Any]) -> str:
    """Save session parameters to a JSON file in the blogs/works directory."""
    try:
        # Create blogs/works directory if it doesn't exist
        works_dir = Path("blogs/works")
        works_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename based on topic and timestamp
        topic_slug = session_data.get("topic", "untitled").lower().replace(" ", "_").replace("-", "_")[:30]
        import time
        timestamp = session_data.get("timestamp") or time.time()
        
        filename = f"{topic_slug}_{int(timestamp)}.json"
        filepath = works_dir / filename
        
        # Save session data
        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)
        
        console.print(f"[dim]💾 Session saved to: {filepath}[/dim]")
        return str(filepath)
        
    except Exception as e:
        console.print(f"[yellow]⚠️ Warning: Could not save session file: {e}[/yellow]")
        return ""


async def _generate_blog_from_session(session_data: Dict[str, Any], verbose: bool = False):
    """Generate a blog post from session data."""
    try:
        blog_type = session_data.get("blog_type")
        
        if blog_type == "tech_blog":
            result = await _generate_blog(
                blog_type="tech_blog",
                topic=session_data.get("topic"),
                goals=session_data.get("goals", []),
                target_audience=session_data.get("target_audience", "developers"),
                tone=session_data.get("tone", "friendly"),
                length=session_data.get("length", "medium"),
                include_code_examples=session_data.get("include_code_examples", True),
                include_diagrams=session_data.get("include_diagrams", False),
                custom_instructions=session_data.get("custom_instructions"),
                output_file=session_data.get("output_file"),
                verbose=verbose
            )
        elif blog_type == "tutorial":
            result = await _generate_blog(
                blog_type="tutorial",
                topic=session_data.get("topic"),
                goals=session_data.get("goals", []),
                difficulty=session_data.get("difficulty", "intermediate"),
                target_audience=session_data.get("target_audience", "developers"),
                tone=session_data.get("tone", "friendly"),
                length=session_data.get("length", "medium"),
                include_code_examples=session_data.get("include_code_examples", True),
                include_diagrams=False,
                custom_instructions=session_data.get("custom_instructions"),
                output_file=session_data.get("output_file"),
                verbose=verbose,
                use_ollama=session_data.get("use_ollama", False),
                ollama_base_url=session_data.get("ollama_base_url"),
                ollama_model=session_data.get("ollama_model"),
                use_lm_studio=session_data.get("use_lm_studio", False),
                lm_studio_base_url=session_data.get("lm_studio_base_url"),
                lm_studio_model=session_data.get("lm_studio_model"),
                streaming=session_data.get("streaming", True),
                stream_mode=session_data.get("stream_mode", "updates")
            )
        elif blog_type == "comparison":
            result = await _generate_blog(
                blog_type="comparison",
                topic=session_data.get("topic"),
                items=session_data.get("items", []),
                goals=session_data.get("goals", []),
                target_audience=session_data.get("target_audience", "developers"),
                tone=session_data.get("tone", "friendly"),
                length=session_data.get("length", "medium"),
                include_code_examples=session_data.get("include_code_examples", True),
                include_diagrams=False,
                custom_instructions=session_data.get("custom_instructions"),
                output_file=session_data.get("output_file"),
                verbose=verbose
            )
        else:
            raise ValueError(f"Unknown blog type: {blog_type}")
            
    except Exception as e:
        console.print(f"[red]❌ Error generating blog from session: {e}[/red]")
        raise


async def _generate_blog(
    blog_type: str,
    topic: str,
    goals: List[str],
    target_audience: str = "developers",
    tone: str = "friendly",
    length: str = "medium",
    include_code_examples: bool = True,
    include_diagrams: bool = False,
    custom_instructions: Optional[str] = None,
    output_file: Optional[str] = None,
    difficulty: Optional[str] = None,
    items: Optional[List[str]] = None,
    verbose: bool = False,
    use_ollama: bool = False,
    ollama_base_url: Optional[str] = None,
    ollama_model: Optional[str] = None,
    use_lm_studio: bool = False,
    lm_studio_base_url: Optional[str] = None,
    lm_studio_model: Optional[str] = None,
    streaming: bool = True,
    stream_mode: str = "updates"
):
    """Internal function to generate a blog post."""
    try:
        if verbose:
            print("🚀 Initializing blog generator with verbose mode...")
        
        generator = BlogGenerator(
            verbose=verbose,
            use_ollama=use_ollama,
            ollama_base_url=ollama_base_url,
            ollama_model=ollama_model,
            use_lm_studio=use_lm_studio,
            lm_studio_base_url=lm_studio_base_url,
            lm_studio_model=lm_studio_model,
            streaming=streaming,
            stream_mode=stream_mode
        )
        
        if verbose:
            print("✅ Blog generator initialized, starting generation...")
        
        # Show generation start message
        if verbose:
            console.print(Panel(
                "[bold blue]🚀 Starting blog generation...[/bold blue]\n"
                "[cyan]You'll see real-time streaming output from each agent below[/cyan]",
                title="[bold green]Generation Started[/bold green]",
                border_style="blue"
            ))
        
        # Generate the blog post (streaming will be handled by the agents)
        if blog_type == "tech_blog":
            result = await generator.generate_tech_blog(
                topic=topic,
                goals=goals,
                target_audience=target_audience,
                tone=tone,
                length=length,
                include_code_examples=include_code_examples,
                include_diagrams=include_diagrams,
                custom_instructions=custom_instructions
            )
        elif blog_type == "tutorial":
            result = await generator.generate_tutorial_blog(
                topic=topic,
                goals=goals,
                difficulty=difficulty or "intermediate",
                target_audience=target_audience,
                tone=tone,
                length=length,
                include_code_examples=include_code_examples,
                custom_instructions=custom_instructions
            )
        elif blog_type == "comparison":
            result = await generator.generate_comparison_blog(
                topic=topic,
                items=items or [],
                goals=goals,
                target_audience=target_audience,
                tone=tone,
                length=length,
                include_code_examples=include_code_examples,
                custom_instructions=custom_instructions
            )
        else:
            raise ValueError(f"Unknown blog type: {blog_type}")
            
        if result.success and result.blog_post:
                # Save the blog post using Integrated MCP file service
                if verbose:
                    console.print("🔧 Using Integrated MCP file service for enhanced file operations...")
                
                try:
                    saved_file = await generator.save_blog_to_file_mcp(result.blog_post, output_file)
                    console.print("✅ Blog saved using Integrated MCP file service")
                except Exception as e:
                    if verbose:
                        console.print(f"⚠️ Integrated MCP save failed, falling back to standard method: {e}")
                    saved_file = generator.save_blog_to_file(result.blog_post, output_file)
                
                # Display results
                console.print(f"\n[green]✅ Blog generated successfully![/green]")
                console.print(f"📁 Saved to: {saved_file}")
                console.print(f"⏱️  Generation time: {result.generation_time:.2f} seconds")
                console.print(f"📊 Quality score: {result.blog_post.generation_metadata.get('quality_score', 'N/A')}/10")
                
                # Show blog summary
                console.print(f"\n[bold]Blog Summary:[/bold]")
                console.print(f"Title: {result.blog_post.title}")
                console.print(f"Type: {result.blog_post.blog_type.value}")
                console.print(f"Sections: {len(result.blog_post.sections)}")
                console.print(f"Code Examples: {sum(len(s.code_examples) for s in result.blog_post.sections)}")
                console.print(f"Estimated Read Time: {result.blog_post.estimated_read_time} minutes")
                
                # Show completion message
                console.print(Panel(
                    "[bold green]🎉 Blog generation completed successfully![/bold green]\n"
                    f"[cyan]Total generation time: {result.generation_time:.2f} seconds[/cyan]",
                    title="[bold green]Generation Complete[/bold green]",
                    border_style="green"
                ))
                
        else:
                console.print(f"\n[red]❌ Blog generation failed![/red]")
                console.print(f"Error: {result.error_message}")
                sys.exit(1)
                
    except Exception as e:
        console.print(f"\n[red]❌ Unexpected error: {e}[/red]")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
