"""Tests for selecting a single agent runtime across the workflow."""

import pytest

from src.agents.runtime import AgentRuntime
from src.agents.base_agent import BaseAgent
from src.agents.agent_orchestrator import AgentOrchestrator
from src.core.config import settings
from src import cli_prompts


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


def test_interactive_backend_prompt_includes_deepseek(monkeypatch):
    captured = {}

    def fake_rich_select(**kwargs):
        captured.update(kwargs)
        return "deepseek"

    monkeypatch.setattr(cli_prompts, "rich_select", fake_rich_select)

    assert cli_prompts.rich_backend_select() == "deepseek"
    assert captured["choices"] == ["openai", "deepseek", "lm-studio", "ollama"]


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


def test_langchain_agent_can_select_deepseek_model():
    agent = StubAgent(
        name="Stub",
        description="test agent",
        use_deepseek=True,
    )

    assert agent.agent_runtime is AgentRuntime.LANGCHAIN
    assert agent.model_name == settings.default_deepseek_model


def test_langchain_deepseek_uses_openai_compatible_endpoint(monkeypatch):
    class ConfiguredAgent(BaseAgent):
        async def process(self, input_data, context=None):
            return input_data

    monkeypatch.setattr(settings, "deepseek_api_key", "dummy")
    agent = ConfiguredAgent(
        name="Stub",
        description="test agent",
        use_deepseek=True,
    )

    assert agent.llm.model_name == settings.default_deepseek_model
    assert agent.llm.openai_api_base == settings.deepseek_base_url


def test_orchestrator_assigns_deepseek_backend_to_every_langchain_node(monkeypatch):
    monkeypatch.setattr(settings, "deepseek_api_key", "dummy")
    orchestrator = AgentOrchestrator(use_deepseek=True, streaming=False)

    agents = (
        orchestrator.research_agent,
        orchestrator.content_agent,
        orchestrator.code_agent,
        orchestrator.formatting_agent,
        orchestrator.review_agent,
    )

    assert [agent.use_deepseek for agent in agents] == [True] * 5
    assert [agent.model_name for agent in agents] == [settings.default_deepseek_model] * 5


def test_orchestrator_assigns_anthropic_runtime_to_every_node_agent():
    orchestrator = AgentOrchestrator(
        agent_runtime=AgentRuntime.ANTHROPIC,
        streaming=False,
    )

    agents = (
        orchestrator.research_agent,
        orchestrator.content_agent,
        orchestrator.code_agent,
        orchestrator.formatting_agent,
        orchestrator.review_agent,
    )

    assert [agent.agent_runtime for agent in agents] == [AgentRuntime.ANTHROPIC] * 5


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


@pytest.mark.asyncio
async def test_anthropic_runtime_uses_messages_api():
    class Messages:
        def __init__(self):
            self.kwargs = None

        async def create(self, **kwargs):
            self.kwargs = kwargs
            return type(
                "Response",
                (),
                {"content": [type("Block", (), {"type": "text", "text": "reply"})()]},
            )()

    class Client:
        def __init__(self):
            self.messages = Messages()

    agent = StubAgent(
        name="Stub",
        description="test agent",
        agent_runtime=AgentRuntime.ANTHROPIC,
    )
    agent.llm = Client()

    result = await agent.generate_response("Say hello", {"topic": "testing"})

    assert result == "reply"
    assert agent.llm.messages.kwargs["model"] == agent.model_name
    assert agent.llm.messages.kwargs["system"] == agent.get_system_prompt()
    assert agent.llm.messages.kwargs["messages"] == [
        {
            "role": "user",
            "content": "Context:\ntopic: testing\n\nUser Input:\nSay hello",
        }
    ]


@pytest.mark.asyncio
async def test_anthropic_runtime_streams_text_from_messages_api():
    class Stream:
        text_stream = (chunk async for chunk in _text_chunks("hello", " world"))

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class Messages:
        def stream(self, **kwargs):
            return Stream()

    class Client:
        def __init__(self):
            self.messages = Messages()

    agent = StubAgent(
        name="Stub",
        description="test agent",
        agent_runtime=AgentRuntime.ANTHROPIC,
    )
    agent.llm = Client()

    chunks = [
        chunk
        async for chunk in agent.generate_response_streaming("Say hello")
    ]

    assert chunks == ["hello", " world"]


async def _text_chunks(*chunks):
    for chunk in chunks:
        yield chunk
