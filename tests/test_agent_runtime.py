"""Tests for selecting a single agent runtime across the workflow."""

import pytest

from src.agents.runtime import AgentRuntime
from src.agents.base_agent import BaseAgent


def test_runtime_names_are_stable_for_cli_and_sessions():
    assert AgentRuntime.LANGCHAIN.value == "langchain"
    assert AgentRuntime.OPENAI.value == "openai"
    assert AgentRuntime.ANTHROPIC.value == "anthropic"


@pytest.mark.parametrize("value", ["LANGCHAIN", "openai", "Anthropic"])
def test_runtime_parses_case_insensitively(value):
    assert AgentRuntime.parse(value) in {
        AgentRuntime.LANGCHAIN,
        AgentRuntime.OPENAI,
        AgentRuntime.ANTHROPIC,
    }


def test_runtime_rejects_unknown_values():
    with pytest.raises(ValueError, match="Unsupported agent runtime"):
        AgentRuntime.parse("unknown")


class StubAgent(BaseAgent):
    def _init_llm(self):
        self.llm = None

    async def process(self, input_data, context=None):
        return input_data


def test_base_agent_accepts_the_selected_runtime():
    agent = StubAgent(
        name="Stub",
        description="test agent",
        agent_runtime=AgentRuntime.OPENAI,
    )

    assert agent.agent_runtime is AgentRuntime.OPENAI


@pytest.mark.asyncio
async def test_openai_runtime_streams_text_deltas_from_runner(monkeypatch):
    from agents import Runner

    class Event:
        type = "raw_response_event"

        def __init__(self, delta):
            self.data = type("Data", (), {"type": "output_text_delta", "delta": delta})()

    class Stream:
        async def stream_events(self):
            for delta in ("hello", " world"):
                yield Event(delta)

    monkeypatch.setattr(Runner, "run_streamed", lambda agent, prompt: Stream())
    agent = StubAgent(
        name="Stub",
        description="test agent",
        agent_runtime=AgentRuntime.OPENAI,
    )

    chunks = [
        chunk
        async for chunk in agent.generate_response_streaming("Say hello")
    ]

    assert chunks == ["hello", " world"]
