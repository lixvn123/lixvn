"""Telemetry tracking and observability module for the Lixvn SDK runtime."""

import time
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional


class SpanContext:
    """Represents an active or completed telemetry timing span."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.start_time: float = time.perf_counter()
        self.end_time: Optional[float] = None
        self.duration_ms: float = 0.0

    def finish(self) -> float:
        """Stops the span timer and calculates elapsed milliseconds."""
        self.end_time = time.perf_counter()
        self.duration_ms = (self.end_time - self.start_time) * 1000.0
        return self.duration_ms

    def to_dict(self) -> Dict[str, Any]:
        """Serializes span data to a dictionary."""
        return {
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": round(self.duration_ms, 3),
        }


class TelemetryTracker:
    """Collects and aggregates performance, token consumption, and trace metrics."""

    def __init__(self) -> None:
        self.tokens_in: int = 0
        self.tokens_out: int = 0
        self.cached_tokens: int = 0
        self.status_code: int = 200
        self.spans: List[SpanContext] = []
        self.traces: List[Dict[str, Any]] = []
        self.tool_metrics: Dict[str, Dict[str, Any]] = {}
        self._created_at: float = time.perf_counter()

    @property
    def total_tokens(self) -> int:
        """Returns cumulative tokens consumed (input + output)."""
        return self.tokens_in + self.tokens_out

    @property
    def total_latency_ms(self) -> float:
        """Calculates total elapsed latency across all recorded spans or lifecycle."""
        if self.spans:
            return sum(span.duration_ms for span in self.spans)
        return (time.perf_counter() - self._created_at) * 1000.0

    @contextmanager
    def start_span(self, name: str) -> Generator[SpanContext, None, None]:
        """Context manager to measure and record execution latency of a named block."""
        span = SpanContext(name=name)
        try:
            yield span
        finally:
            span.finish()
            self.spans.append(span)

    def record_tokens(
        self,
        input_tokens: Optional[int] = 0,
        output_tokens: Optional[int] = 0,
        cached_tokens: Optional[int] = 0,
    ) -> None:
        """Records token usage for an LLM interaction or simulation turn."""
        in_tok = 0 if input_tokens is None else input_tokens
        out_tok = 0 if output_tokens is None else output_tokens
        cache_tok = 0 if cached_tokens is None else cached_tokens

        if in_tok < 0 or out_tok < 0 or cache_tok < 0:
            raise ValueError("Token counts cannot be negative.")
        self.tokens_in += in_tok
        self.tokens_out += out_tok
        self.cached_tokens += cache_tok

    def record_tool_call(
        self,
        tool_name: str,
        duration_ms: float,
        success: bool,
        error: Optional[str] = None,
    ) -> None:
        """Records execution statistics for a tool call."""
        if tool_name not in self.tool_metrics:
            self.tool_metrics[tool_name] = {
                "calls": 0,
                "successes": 0,
                "failures": 0,
                "total_duration_ms": 0.0,
                "last_error": None,
            }
        metrics = self.tool_metrics[tool_name]
        metrics["calls"] += 1
        if success:
            metrics["successes"] += 1
        else:
            metrics["failures"] += 1
            metrics["last_error"] = error
        metrics["total_duration_ms"] += max(0.0, duration_ms)

        self.traces.append({
            "type": "tool_call",
            "tool_name": tool_name,
            "duration_ms": round(duration_ms, 3),
            "success": success,
            "error": error,
            "timestamp": time.time(),
        })

    def record_step(
        self,
        agent_name: str,
        step_type: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Appends an agent workflow step trace entry."""
        self.traces.append({
            "type": "agent_step",
            "agent_name": agent_name,
            "step_type": step_type,
            "details": details or {},
            "timestamp": time.time(),
        })

    def set_status_code(self, code: int) -> None:
        """Updates the HTTP-style outcome status code."""
        self.status_code = code

    def reset(self) -> None:
        """Resets all tracked metrics to their initial state."""
        self.tokens_in = 0
        self.tokens_out = 0
        self.cached_tokens = 0
        self.status_code = 200
        self.spans.clear()
        self.traces.clear()
        self.tool_metrics.clear()
        self._created_at = time.perf_counter()

    def summary(self) -> Dict[str, Any]:
        """Produces a structured dictionary summarizing all telemetry metrics."""
        return {
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "cached_tokens": self.cached_tokens,
            "total_tokens": self.total_tokens,
            "total_latency_ms": round(self.total_latency_ms, 3),
            "status_code": self.status_code,
            "spans_count": len(self.spans),
            "traces_count": len(self.traces),
            "tool_metrics": self.tool_metrics,
        }
