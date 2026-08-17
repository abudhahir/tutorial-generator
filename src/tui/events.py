"""Serializable events shared by the workflow and Textual UI."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict


class EventKind(str, Enum):
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    NODE_STARTED = "node_started"
    NODE_OUTPUT = "node_output"
    NODE_COMPLETED = "node_completed"
    NODE_FAILED = "node_failed"


@dataclass(frozen=True)
class WorkflowEvent:
    """A UI-safe update emitted while one workflow run is executing."""

    kind: EventKind
    run_id: str
    runtime: str
    node: str = ""
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    text: str = ""
    error: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-friendly representation for logs and adapters."""
        return {
            "kind": self.kind.value,
            "run_id": self.run_id,
            "runtime": self.runtime,
            "node": self.node,
            "timestamp": self.timestamp.isoformat(),
            "text": self.text,
            "error": self.error,
            "details": self.details,
        }
