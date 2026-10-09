"""Trajectory compaction and context management for large LLM context windows."""

import json
from typing import Any, Dict, List, Optional, Union
from lixvn.errors import ContextLimitExceededError


class TrajectoryCompactor:
    """Manages multi-agent conversation history, token estimation, and prompt caching tags."""

    DEFAULT_MAX_CONTEXT_TOKENS: int = 200_000  # Claude 3.5 Sonnet 200K window

    def __init__(self, max_context_tokens: int = DEFAULT_MAX_CONTEXT_TOKENS) -> None:
        if max_context_tokens <= 0:
            raise ValueError("max_context_tokens must be positive.")
        self.max_context_tokens = max_context_tokens
        self.turns: List[Dict[str, Any]] = []

    def add_turn(
        self,
        role: str,
        content: Union[str, List[Any], Dict[str, Any]],
        cache_control: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Appends a new conversation turn to the trajectory."""
        if not role or not role.strip():
            raise ValueError("Turn role must not be empty.")

        turn: Dict[str, Any] = {
            "role": role.strip(),
            "content": content,
            "cache_control": cache_control,
            "metadata": metadata or {},
        }
        self.turns.append(turn)
        return turn

    def estimate_tokens(self, item: Any = None) -> int:
        """Estimates token usage using standard 4-chars-per-token heuristic with message overhead."""
        if item is None:
            return self.total_tokens()

        if isinstance(item, str):
            # Baseline: ~4 characters per token + base token
            return max(1, len(item) // 4 + 1)
        elif isinstance(item, (dict, list)):
            serialized = json.dumps(item, default=str)
            return max(1, len(serialized) // 4 + 2)
        elif isinstance(item, (int, float, bool)):
            return 2
        return 4

    def total_tokens(self) -> int:
        """Calculates total estimated tokens across all turns in the current trajectory."""
        total = 0
        for turn in self.turns:
            total += self.estimate_tokens(turn.get("content"))
            total += 4  # Per-message structural token overhead
        return total

    def compact(
        self,
        target_tokens: int = 150_000,
        preserve_recent: int = 4,
    ) -> List[Dict[str, Any]]:
        """Compacts older trajectory turns and tool observations when approaching context limits."""
        if target_tokens <= 0:
            raise ValueError("target_tokens must be positive.")

        current_tokens = self.total_tokens()
        if current_tokens <= target_tokens:
            return list(self.turns)

        if len(self.turns) <= preserve_recent + 1:
            # If turns cannot be compacted further and exceeds hard window
            if current_tokens > self.max_context_tokens:
                raise ContextLimitExceededError(
                    f"Trajectory size ({current_tokens} tokens) exceeds maximum window ({self.max_context_tokens} tokens)."
                )
            return list(self.turns)

        # Preserve the initial turn (system/goal) and the most recent N turns
        initial_turns = self.turns[:1]
        recent_turns = self.turns[-preserve_recent:]
        middle_turns = self.turns[1:-preserve_recent]

        compacted_middle: List[Dict[str, Any]] = []
        condensed_notes: List[str] = []

        for turn in middle_turns:
            role = turn.get("role", "unknown")
            content = turn.get("content")

            # Check if this is a large tool output or intermediate thought
            if role == "tool" or (isinstance(content, str) and len(content) > 300):
                content_str = json.dumps(content, default=str) if isinstance(content, (dict, list)) else str(content)
                preview = content_str[:120].replace("\n", " ")
                condensed_notes.append(f"[{role} output excerpt: {preview}... ({len(content_str)} chars)]")
            else:
                compacted_middle.append(turn)

        if condensed_notes:
            summary_content = "Compact trajectory log of prior interactions:\n" + "\n".join(condensed_notes)
            compacted_middle.append({
                "role": "user",
                "content": summary_content,
                "cache_control": True,
                "metadata": {"compacted": True},
            })

        self.turns = initial_turns + compacted_middle + recent_turns

        # Check hard limit
        if self.total_tokens() > self.max_context_tokens:
            raise ContextLimitExceededError(
                f"Trajectory ({self.total_tokens()} tokens) exceeds hard limit {self.max_context_tokens} after compaction."
            )

        return list(self.turns)

    def get_messages(
        self,
        apply_caching: bool = True,
        max_cache_breakpoints: int = 4,
    ) -> List[Dict[str, Any]]:
        """Formats turns into Anthropic Messages API format with ephemeral prompt caching blocks."""
        formatted: List[Dict[str, Any]] = []
        cache_points_assigned = 0

        for turn in self.turns:
            role = turn["role"]
            content = turn["content"]
            use_cache = turn.get("cache_control", False) and apply_caching and (cache_points_assigned < max_cache_breakpoints)

            if use_cache:
                cache_points_assigned += 1
                if isinstance(content, str):
                    formatted_content = [
                        {
                            "type": "text",
                            "text": content,
                            "cache_control": {"type": "ephemeral"},
                        }
                    ]
                elif isinstance(content, list):
                    formatted_content = list(content)
                    if formatted_content and isinstance(formatted_content[-1], dict):
                        formatted_content[-1] = {
                            **formatted_content[-1],
                            "cache_control": {"type": "ephemeral"},
                        }
                else:
                    formatted_content = [
                        {
                            "type": "text",
                            "text": json.dumps(content, default=str),
                            "cache_control": {"type": "ephemeral"},
                        }
                    ]
                formatted.append({"role": role, "content": formatted_content})
            else:
                formatted.append({"role": role, "content": content})

        return formatted

    def clear(self) -> None:
        """Clears all conversation turns."""
        self.turns.clear()
