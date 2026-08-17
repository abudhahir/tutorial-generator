"""
Rich UI interactive prompts for the I'm Poster CLI.

Provides styled, user-friendly prompts using Rich components
when CLI parameters are not provided via command-line arguments.
"""

from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.rule import Rule

console = Console()


def show_welcome_banner() -> None:
    """Display the welcome banner for interactive mode."""
    console.print()
    console.print(Panel(
        "[bold cyan]I'm Poster[/bold cyan] - Multi-Agent AI Blog Generator\n\n"
        "[dim]No arguments provided. Launching interactive mode...[/dim]",
        title="[bold green]Welcome[/bold green]",
        border_style="cyan",
        padding=(1, 2),
    ))
    console.print()


def rich_select(
    label: str,
    choices: List[str],
    descriptions: Optional[List[str]] = None,
    default: Optional[str] = None,
) -> str:
    """Display a numbered selection list with Rich styling.

    Args:
        label: Prompt label shown above the choices.
        choices: List of valid choice values.
        descriptions: Optional human-friendly descriptions for each choice.
        default: Default value (must be in choices).

    Returns:
        The selected choice value.
    """
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Num", style="bold cyan", width=4)
    table.add_column("Choice", style="bold white")
    if descriptions:
        table.add_column("Description", style="dim")

    for idx, choice in enumerate(choices, 1):
        default_marker = " [green](default)[/green]" if choice == default else ""
        if descriptions:
            table.add_row(f"[{idx}]", f"{choice}{default_marker}", descriptions[idx - 1])
        else:
            table.add_row(f"[{idx}]", f"{choice}{default_marker}")

    console.print()
    console.print(f"  [bold yellow]{label}[/bold yellow]")
    console.print(table)

    while True:
        raw = Prompt.ask(
            "  [cyan]Enter number or value[/cyan]",
            default=default or "",
        )
        raw = raw.strip()

        # Accept by number
        if raw.isdigit():
            num = int(raw)
            if 1 <= num <= len(choices):
                selected = choices[num - 1]
                console.print(f"  [green]Selected:[/green] {selected}")
                return selected

        # Accept by value (case-insensitive)
        lower = raw.lower()
        for choice in choices:
            if choice.lower() == lower:
                console.print(f"  [green]Selected:[/green] {choice}")
                return choice

        console.print(f"  [red]Invalid selection. Choose 1-{len(choices)} or type a value.[/red]")


def rich_text_prompt(
    label: str,
    default: Optional[str] = None,
    hint: Optional[str] = None,
) -> str:
    """Styled text prompt with optional hint.

    Args:
        label: Prompt label.
        default: Default value.
        hint: Hint text shown below the label.

    Returns:
        User-entered text.
    """
    console.print()
    if hint:
        console.print(f"  [dim]{hint}[/dim]")
    value = Prompt.ask(f"  [bold yellow]{label}[/bold yellow]", default=default or "")
    return value.strip()


def rich_goals_prompt(label: str = "Blog Goals") -> List[str]:
    """Prompt for multiple goals interactively.

    The user can enter goals one at a time. An empty entry finishes input.

    Args:
        label: Prompt label.

    Returns:
        List of goal strings.
    """
    console.print()
    console.print(f"  [bold yellow]{label}[/bold yellow]")
    console.print("  [dim]Enter goals one per line. Press Enter on an empty line to finish.[/dim]")

    goals: List[str] = []
    idx = 1
    while True:
        goal = Prompt.ask(f"  [cyan]Goal {idx}[/cyan]", default="")
        goal = goal.strip()
        if not goal:
            if not goals:
                console.print("  [red]At least one goal is required.[/red]")
                continue
            break
        goals.append(goal)
        idx += 1

    console.print(f"  [green]{len(goals)} goal(s) added.[/green]")
    return goals


def rich_confirm(
    label: str,
    default: bool = True,
) -> bool:
    """Styled yes/no confirmation prompt.

    Args:
        label: Question text.
        default: Default value.

    Returns:
        Boolean answer.
    """
    console.print()
    return Confirm.ask(f"  [bold yellow]{label}[/bold yellow]", default=default)


def rich_blog_type_select() -> str:
    """Prompt user to select a blog type."""
    return rich_select(
        label="What type of blog would you like to generate?",
        choices=["tech_blog", "tutorial", "comparison"],
        descriptions=[
            "A technical blog post on a topic",
            "A step-by-step tutorial with examples",
            "A side-by-side comparison of technologies",
        ],
        default="tech_blog",
    )


def rich_backend_select() -> str:
    """Prompt user to select an LLM backend."""
    return rich_select(
        label="Which LLM backend would you like to use?",
        choices=["openai", "deepseek", "lm-studio", "ollama"],
        descriptions=[
            "OpenAI API (requires OPENAI_API_KEY)",
            "DeepSeek API through the LangChain track (requires DEEPSEEK_API_KEY)",
            "LM Studio local server",
            "Ollama local models",
        ],
        default="openai",
    )


def build_rerun_command(blog_type: str, config: dict) -> str:
    """Build the equivalent CLI command from collected config.

    Args:
        blog_type: One of tech_blog, tutorial, comparison.
        config: Configuration dictionary with collected parameters.

    Returns:
        A shell command string that reproduces this run.
    """
    type_to_subcommand = {
        "tech_blog": "generate-tech-blog",
        "tutorial": "generate-tutorial",
        "comparison": "generate-comparison",
    }
    subcommand = type_to_subcommand.get(blog_type, "generate-tech-blog")
    parts = [f"im-poster {subcommand}"]

    # Map config keys to CLI flags
    flag_map = {
        "topic": "--topic",
        "audience": "--audience",
        "target_audience": "--audience",
        "tone": "--tone",
        "length": "--length",
        "difficulty": "--difficulty",
        "backend": "--backend",
        "output_file": "--output",
        "custom_instructions": "--instructions",
        "stream_mode": "--stream-mode",
        "ollama_model": "--ollama-model",
        "ollama_base_url": "--ollama-url",
        "lm_studio_model": "--lm-studio-model",
        "lm_studio_base_url": "--lm-studio-url",
    }

    for key, value in config.items():
        if value is None or value == "" or value == []:
            continue

        if key == "goals":
            for goal in value:
                parts.append(f'    --goal "{goal}"')
        elif key == "items":
            for item in value:
                parts.append(f'    --item "{item}"')
        elif key == "code_examples" or key == "include_code_examples":
            parts.append("    --code" if value else "    --no-code")
        elif key == "diagrams" or key == "include_diagrams":
            if value:
                parts.append("    --diagrams")
        elif key == "streaming":
            if not value:
                parts.append("    --no-streaming")
        elif key in flag_map:
            parts.append(f'    {flag_map[key]} "{value}"')

    return " \\\n".join(parts)


def show_config_summary(config: dict, blog_type: str = "tech_blog") -> None:
    """Display a configuration summary panel and rerun command before generation."""
    lines = []
    for key, value in config.items():
        if value is None or value == "" or value == []:
            continue
        display_key = key.replace("_", " ").title()
        if isinstance(value, list):
            value = ", ".join(str(v) for v in value)
        elif isinstance(value, bool):
            value = "Yes" if value else "No"
        lines.append(f"[cyan]{display_key}:[/cyan] {value}")

    console.print()
    console.print(Panel(
        "\n".join(lines),
        title="[bold green]Configuration Summary[/bold green]",
        border_style="green",
        padding=(1, 2),
    ))

    # Show rerun command
    cmd = build_rerun_command(blog_type, config)
    console.print(Panel(
        f"[dim]{cmd}[/dim]",
        title="[bold yellow]Run again with[/bold yellow]",
        border_style="yellow",
        padding=(1, 2),
    ))
    console.print()
