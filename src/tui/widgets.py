"""Small presentational widgets for the workflow TUI."""

from textual.widgets import Static


NODES = ("research", "content", "code", "formatting", "review")


class WorkflowGraph(Static):
    """Render the fixed shared LangGraph workflow and node statuses."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.statuses = {node: "pending" for node in NODES}

    def set_status(self, node: str, status: str) -> None:
        if node in self.statuses:
            self.statuses[node] = status
        self.update(self.render_graph())

    def render_graph(self) -> str:
        symbols = {"pending": "○", "running": "●", "completed": "✓", "failed": "✗"}
        rows = []
        for index, node in enumerate(NODES):
            status = self.statuses[node]
            rows.append(f"{symbols.get(status, '•')} {node:<10} {status}")
            if index < len(NODES) - 1:
                rows.append("      │")
        return "\n".join(rows)

