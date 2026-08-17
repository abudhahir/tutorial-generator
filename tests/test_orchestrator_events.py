from src.agents.agent_orchestrator import AgentOrchestrator
from src.agents.base_agent import StreamingCallbackHandler
from src.agents.runtime import AgentRuntime
from src.tui.events import EventKind


def test_orchestrator_publishes_workflow_event_to_sink():
    received = []
    orchestrator = AgentOrchestrator.__new__(AgentOrchestrator)
    orchestrator.event_sink = received.append
    orchestrator.agent_runtime = AgentRuntime.OPENAI
    orchestrator.run_id = "run-1"

    orchestrator._publish_event(EventKind.NODE_STARTED, node="research")

    assert len(received) == 1
    assert received[0].kind is EventKind.NODE_STARTED
    assert received[0].node == "research"
    assert received[0].runtime == "openai"


def test_streaming_callback_publishes_text_without_requiring_rich_live():
    received = []
    callback = StreamingCallbackHandler(
        "Content Agent",
        console=None,
        verbose=False,
        event_sink=received.append,
        run_id="run-2",
        runtime="anthropic",
    )

    callback.on_llm_new_token("hello")

    assert received[0].kind is EventKind.NODE_OUTPUT
    assert received[0].node == "Content Agent"
    assert received[0].text == "hello"
