"""Agent runtime selection shared by the workflow and CLI."""

from enum import Enum


class AgentRuntime(str, Enum):
    """The SDK/runtime used by every agent in one workflow execution."""

    LANGCHAIN = "langchain"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

    @classmethod
    def parse(cls, value: str) -> "AgentRuntime":
        """Parse a user-facing runtime name."""
        normalized = value.strip().lower()
        try:
            return cls(normalized)
        except ValueError as exc:
            supported = ", ".join(item.value for item in cls)
            raise ValueError(
                f"Unsupported agent runtime '{value}'. Supported runtimes: {supported}"
            ) from exc
