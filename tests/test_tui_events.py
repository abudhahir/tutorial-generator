from datetime import datetime, timezone

from src.tui.events import EventKind, WorkflowEvent


def test_workflow_event_defaults_are_serialization_safe():
    event = WorkflowEvent(
        kind=EventKind.NODE_STARTED,
        run_id="run-1",
        runtime="openai",
        node="content",
    )

    assert event.kind is EventKind.NODE_STARTED
    assert event.run_id == "run-1"
    assert event.runtime == "openai"
    assert event.node == "content"
    assert isinstance(event.timestamp, datetime)
    assert event.timestamp.tzinfo == timezone.utc
    assert event.text == ""
    assert event.details == {}


def test_workflow_event_to_dict_contains_only_json_friendly_values():
    event = WorkflowEvent(
        kind=EventKind.NODE_COMPLETED,
        run_id="run-2",
        runtime="anthropic",
        node="review",
        details={"duration_seconds": 1.5},
    )

    payload = event.to_dict()

    assert payload == {
        "kind": "node_completed",
        "run_id": "run-2",
        "runtime": "anthropic",
        "node": "review",
        "timestamp": event.timestamp.isoformat(),
        "text": "",
        "error": "",
        "details": {"duration_seconds": 1.5},
    }

