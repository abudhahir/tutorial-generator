"""Textual application for configuring and observing blog generation."""

from __future__ import annotations

from typing import Any, Dict

from textual.app import App, ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Input, Label, RichLog, Select, Static, TextArea

from ..agents.runtime import AgentRuntime
from ..tui.events import EventKind, WorkflowEvent
from .widgets import WorkflowGraph


class WorkflowTui(App[None]):
    """Pre-run configuration form and live workflow monitor."""

    CSS = """
    Screen { layout: vertical; }
    #body { height: 1fr; }
    #config { width: 35%; min-width: 32; border: round $accent; padding: 1; }
    #monitor { width: 65%; padding: 0 1; }
    .section { height: auto; margin: 0 0 1 0; }
    .section-title { text-style: bold; color: $accent; }
    #graph { height: 12; border: round $surface; padding: 1; }
    #details { height: 7; border: round $surface; padding: 1; }
    #output { height: 1fr; border: round $surface; }
    #run { width: 1fr; }
    #status { height: 1; color: $text-muted; }
    """

    BINDINGS = [("q", "quit", "Quit")]
    runtime = reactive("langchain")

    class WorkflowEventMessage(Message):
        def __init__(self, event: WorkflowEvent) -> None:
            super().__init__()
            self.event = event

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="body"):
            with ScrollableContainer(id="config"):
                yield Label("Configuration", classes="section-title")
                yield Label("Agent runtime")
                yield Select(
                    [("LangChain agents", "langchain"), ("OpenAI SDK agents", "openai"), ("Anthropic SDK agents", "anthropic")],
                    value="langchain",
                    id="runtime",
                )
                yield Label("Backend")
                yield Select(
                    [("OpenAI", "openai"), ("Anthropic", "anthropic"), ("DeepSeek", "deepseek"), ("Ollama", "ollama"), ("LM Studio", "lm-studio")],
                    value="openai",
                    id="backend",
                )
                yield Label("Topic")
                yield Input(placeholder="What should the blog cover?", id="topic")
                yield Label("Goals (one per line)")
                yield TextArea(id="goals")
                yield Label("Audience")
                yield Input(value="developers", id="audience")
                yield Label("Tone")
                yield Select([(value, value) for value in ("friendly", "professional", "humorous", "technical")], value="friendly", id="tone")
                yield Label("Length")
                yield Select([(value, value) for value in ("short", "medium", "long")], value="medium", id="length")
                yield Label("Output path (optional)")
                yield Input(placeholder="Auto-save in blogs/", id="output-path")
                yield Button("Run workflow", id="run", variant="primary")
            with Vertical(id="monitor"):
                yield Label("Workflow Graph", classes="section-title")
                yield WorkflowGraph(id="graph")
                yield Label("Node Details", classes="section-title")
                yield Static("No node selected", id="details")
                yield Label("Live Output", classes="section-title")
                yield RichLog(id="output", highlight=True, markup=False)
                yield Static("Ready to configure a run", id="status")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#graph", WorkflowGraph).update(self.query_one("#graph", WorkflowGraph).render_graph())

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "runtime" and event.value is not Select.BLANK:
            self.runtime = str(event.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "run":
            self._start_run()

    def _start_run(self) -> None:
        topic = self.query_one("#topic", Input).value.strip()
        if not topic:
            self.query_one("#status", Static).update("Enter a topic before running")
            return
        self.query_one("#run", Button).disabled = True
        self._set_form_enabled(False)
        self.query_one("#status", Static).update(f"Starting {self.runtime} workflow...")
        self.run_worker(self._run_workflow(self._request_values()), exclusive=True, group="workflow")

    def _set_form_enabled(self, enabled: bool) -> None:
        for widget_id in ("runtime", "backend", "topic", "goals", "audience", "tone", "length", "output-path"):
            self.query_one(f"#{widget_id}").disabled = not enabled

    def _request_values(self) -> Dict[str, Any]:
        goals = [line.strip() for line in self.query_one("#goals", TextArea).text.splitlines() if line.strip()]
        return {
            "runtime": self.runtime,
            "backend": str(self.query_one("#backend", Select).value),
            "topic": self.query_one("#topic", Input).value.strip(),
            "goals": goals or ["Explain the topic clearly"],
            "audience": self.query_one("#audience", Input).value.strip() or "developers",
            "tone": str(self.query_one("#tone", Select).value),
            "length": str(self.query_one("#length", Select).value),
            "output_path": self.query_one("#output-path", Input).value.strip() or None,
        }

    def _publish_from_worker(self, event: WorkflowEvent) -> None:
        self.post_message(self.WorkflowEventMessage(event))

    async def _run_workflow(self, values: Dict[str, Any]) -> None:
        from ..core.blog_generator import BlogGenerator
        from ..core.models import BlogRequest, BlogType

        request = BlogRequest(
            topic=values["topic"],
            blog_type=BlogType.TECH_BLOG,
            goals=values["goals"],
            target_audience=values["audience"],
            tone=values["tone"],
            length=values["length"],
        )
        generator = BlogGenerator(
            verbose=False,
            streaming=True,
            agent_runtime=AgentRuntime.parse(values["runtime"]),
            use_ollama=values["backend"] == "ollama",
            use_lm_studio=values["backend"] == "lm-studio",
            use_deepseek=values["backend"] == "deepseek",
            event_sink=self._publish_from_worker,
        )
        result = await generator.generate_blog_from_request(request)
        if not result.success:
            self.post_message(self.WorkflowEventMessage(WorkflowEvent(
                kind=EventKind.WORKFLOW_FAILED,
                run_id="",
                runtime=values["runtime"],
                error=result.error_message or "Workflow failed",
            )))

    def on_workflow_tui_workflow_event_message(self, message: WorkflowEventMessage) -> None:
        event = message.event
        graph = self.query_one("#graph", WorkflowGraph)
        if event.kind is EventKind.NODE_STARTED:
            graph.set_status(event.node, "running")
            self.query_one("#details", Static).update(f"{event.node}\nStatus: running\nRuntime: {event.runtime}")
        elif event.kind is EventKind.NODE_COMPLETED:
            graph.set_status(event.node, "completed")
            self.query_one("#details", Static).update(f"{event.node}\nStatus: completed\nDetails: {event.details}")
        elif event.kind is EventKind.NODE_FAILED:
            graph.set_status(event.node, "failed")
            self.query_one("#details", Static).update(f"{event.node}\nStatus: failed\n{event.error}")
        elif event.kind is EventKind.NODE_OUTPUT:
            self.query_one("#output", RichLog).write(event.text)
        elif event.kind is EventKind.WORKFLOW_STARTED:
            self.query_one("#status", Static).update(f"Running {event.runtime} workflow")
        elif event.kind is EventKind.WORKFLOW_COMPLETED:
            self.query_one("#status", Static).update("Workflow completed")
            self.query_one("#run", Button).disabled = False
            self._set_form_enabled(True)
        elif event.kind is EventKind.WORKFLOW_FAILED:
            self.query_one("#status", Static).update(f"Workflow failed: {event.error}")
            self.query_one("#run", Button).disabled = False
            self._set_form_enabled(True)


def run_tui() -> None:
    """Launch the Textual workflow application."""
    WorkflowTui().run()
