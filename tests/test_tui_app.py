import pytest

from src.tui.events import EventKind, WorkflowEvent


textual = pytest.importorskip("textual")
from src.tui.app import WorkflowTui


@pytest.mark.asyncio
async def test_tui_starts_with_preconfiguration_form_and_shared_graph():
    app = WorkflowTui()

    async with app.run_test() as pilot:
        assert app.query_one("#runtime").value == "langchain"
        assert app.query_one("#topic")
        assert app.query_one("#run").disabled is False
        assert "research" in app.query_one("#graph").render().plain
        await pilot.press("tab")


@pytest.mark.asyncio
async def test_tui_routes_node_events_to_graph_and_output():
    app = WorkflowTui()

    async with app.run_test() as pilot:
        app.post_message(app.WorkflowEventMessage(WorkflowEvent(
            kind=EventKind.NODE_STARTED,
            run_id="run-1",
            runtime="anthropic",
            node="content",
        )))
        app.post_message(app.WorkflowEventMessage(WorkflowEvent(
            kind=EventKind.NODE_OUTPUT,
            run_id="run-1",
            runtime="anthropic",
            node="content",
            text="streamed text",
        )))
        await pilot.pause()

        assert "content" in app.query_one("#details").render().plain
        assert any("streamed text" in str(line) for line in app.query_one("#output").lines)
