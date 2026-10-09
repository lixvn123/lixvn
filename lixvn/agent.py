"""Agent definition, role specifications, and memory management for the Lixvn SDK."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class Agent(BaseModel):
    """Represents an autonomous worker agent within a multi-agent swarm."""

    name: str = Field(..., description="Unique name of the agent")
    role: str = Field(..., description="Primary functional role or operational focus")
    system_prompt: Optional[str] = Field(
        default=None,
        description="Custom system prompt guidelines specifically for this agent",
    )
    memory: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="In-memory conversational trajectory and observation history",
    )
    tools: List[str] = Field(
        default_factory=list,
        description="List of tool names accessible to this agent (empty allows all runtime tools)",
    )

    @field_validator("name", "role")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        """Ensures agent name and role are non-empty strings."""
        if not value or not value.strip():
            raise ValueError("Agent 'name' and 'role' must be non-empty strings.")
        return value.strip()

    def format_system_prompt(self) -> str:
        """Constructs the comprehensive system prompt for the agent."""
        base_lines = [
            f"You are {self.name}.",
            f"Role: {self.role}.",
        ]
        if self.system_prompt and self.system_prompt.strip():
            base_lines.append(self.system_prompt.strip())
        return "\n".join(base_lines)

    def add_memory(self, role: str, content: str, **kwargs: Any) -> None:
        """Appends an interaction or observation turn to the agent's memory."""
        if not role or not role.strip():
            raise ValueError("Memory role cannot be empty.")
        entry: Dict[str, Any] = {
            "role": role.strip(),
            "content": content,
            **kwargs,
        }
        self.memory.append(entry)

    def clear_memory(self) -> None:
        """Clears all historical interactions from memory."""
        self.memory.clear()

    def __repr__(self) -> str:
        return f"<Agent name={self.name!r} role={self.role!r} memory_items={len(self.memory)}>"
