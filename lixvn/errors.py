"""Custom typed exceptions for the Lixvn SDK runtime."""

from typing import Optional


class LixvnError(Exception):
    """Base exception for all Lixvn SDK errors."""
    pass


class ConfigurationError(LixvnError):
    """Raised when runtime configuration, model selection, or initialization parameters are invalid."""
    pass


class ToolExecutionError(LixvnError):
    """Raised when a tool execution fails or encounters unhandled runtime exceptions."""

    def __init__(
        self,
        tool_name: str,
        message: str,
        original_error: Optional[Exception] = None,
    ) -> None:
        super().__init__(f"Tool '{tool_name}' execution failed: {message}")
        self.tool_name = tool_name
        self.message = message
        self.original_error = original_error


class AgentExecutionError(LixvnError):
    """Raised when an agent execution fails during swarm orchestration."""

    def __init__(
        self,
        agent_name: str,
        message: str,
        original_error: Optional[Exception] = None,
    ) -> None:
        super().__init__(f"Agent '{agent_name}' failed: {message}")
        self.agent_name = agent_name
        self.message = message
        self.original_error = original_error


class ContextLimitExceededError(LixvnError):
    """Raised when trajectory exceeds the maximum supported token window (e.g. 200K tokens)."""
    pass


class DatabaseQueryError(LixvnError):
    """Raised when a database query violates security policies or syntax rules."""

    def __init__(self, query: str, reason: str) -> None:
        super().__init__(f"Database query rejected: {reason} | Query: {query!r}")
        self.query = query
        self.reason = reason
