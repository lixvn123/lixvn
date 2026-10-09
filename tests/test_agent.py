"""Unit tests for lixvn.Agent model and memory behaviors."""

import pytest
from pydantic import ValidationError
from lixvn.agent import Agent


def test_agent_initialization_valid():
    """Verifies that an Agent can be created with valid required and optional fields."""
    agent = Agent(
        name="Security Auditor",
        role="Vulnerability assessment and compliance",
        system_prompt="Focus on OWASP Top 10 vulnerabilities.",
        tools=["scan_headers", "check_permissions"],
    )
    assert agent.name == "Security Auditor"
    assert agent.role == "Vulnerability assessment and compliance"
    assert agent.system_prompt == "Focus on OWASP Top 10 vulnerabilities."
    assert agent.tools == ["scan_headers", "check_permissions"]
    assert len(agent.memory) == 0


def test_agent_validation_empty_name():
    """Ensures empty or whitespace name raises ValidationError."""
    with pytest.raises(ValidationError):
        Agent(name="   ", role="DevOps Engineer")


def test_agent_validation_empty_role():
    """Ensures empty or whitespace role raises ValidationError."""
    with pytest.raises(ValidationError):
        Agent(name="DevOps Engineer", role="")


def test_agent_format_system_prompt_with_custom():
    """Tests system prompt generation when custom prompt is provided."""
    agent = Agent(
        name="Data Architect",
        role="Database schema optimization",
        system_prompt="Strictly apply 3NF normalization rules.",
    )
    prompt = agent.format_system_prompt()
    assert "Data Architect" in prompt
    assert "Database schema optimization" in prompt
    assert "Strictly apply 3NF normalization rules." in prompt


def test_agent_format_system_prompt_without_custom():
    """Tests system prompt generation without custom prompt."""
    agent = Agent(name="Lead Architect", role="Context breakdown & planning")
    prompt = agent.format_system_prompt()
    assert "Lead Architect" in prompt
    assert "Context breakdown & planning" in prompt


def test_agent_memory_add_and_clear():
    """Tests memory append and clear operations."""
    agent = Agent(name="Researcher", role="Fact verification")
    agent.add_memory("user", "Verify Q4 projections")
    agent.add_memory("tool", '{"growth_pct": 14.2}')

    assert len(agent.memory) == 2
    assert agent.memory[0]["role"] == "user"
    assert agent.memory[0]["content"] == "Verify Q4 projections"
    assert agent.memory[1]["role"] == "tool"

    agent.clear_memory()
    assert len(agent.memory) == 0


def test_agent_memory_empty_role_raises():
    """Tests that adding memory with empty role raises ValueError."""
    agent = Agent(name="Researcher", role="Fact verification")
    with pytest.raises(ValueError, match="Memory role cannot be empty"):
        agent.add_memory("", "Some content")


def test_agent_repr():
    """Verifies that repr output contains agent identification."""
    agent = Agent(name="Planner", role="Task decomposition")
    rep = repr(agent)
    assert "Planner" in rep
    assert "Task decomposition" in rep
