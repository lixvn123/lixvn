"""Lixvn: High-performance autonomous agent swarm runtime engineered for Anthropic Claude 3.5 Sonnet."""

from lixvn.agent import Agent
from lixvn.database import SafeDatabase
from lixvn.errors import (
    AgentExecutionError,
    ConfigurationError,
    ContextLimitExceededError,
    DatabaseQueryError,
    LixvnError,
    ToolExecutionError,
)
from lixvn.runtime import DispatchResult, SwarmRuntime
from lixvn.telemetry import SpanContext, TelemetryTracker
from lixvn.tool import Tool, tool
from lixvn.trajectory import TrajectoryCompactor

__version__ = "0.4.2"
__author__ = "Lixvn Authors"
__license__ = "Apache-2.0"

__all__ = [
    "Agent",
    "AgentExecutionError",
    "ConfigurationError",
    "ContextLimitExceededError",
    "DatabaseQueryError",
    "DispatchResult",
    "LixvnError",
    "SafeDatabase",
    "SpanContext",
    "SwarmRuntime",
    "TelemetryTracker",
    "Tool",
    "ToolExecutionError",
    "TrajectoryCompactor",
    "__version__",
    "tool",
]
