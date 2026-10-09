"""Unit tests for lixvn.telemetry and lixvn.trajectory context compaction."""

import time
import pytest
from lixvn.telemetry import TelemetryTracker
from lixvn.trajectory import TrajectoryCompactor


def test_telemetry_token_tracking():
    """Verifies that TelemetryTracker correctly accumulates token metrics."""
    tracker = TelemetryTracker()
    assert tracker.total_tokens == 0
    assert tracker.status_code == 200

    tracker.record_tokens(input_tokens=500, output_tokens=150, cached_tokens=200)
    assert tracker.tokens_in == 500
    assert tracker.tokens_out == 150
    assert tracker.cached_tokens == 200
    assert tracker.total_tokens == 650

    tracker.record_tokens(input_tokens=100, output_tokens=50)
    assert tracker.total_tokens == 800


def test_telemetry_negative_tokens_raises():
    """Ensures recording negative tokens raises ValueError."""
    tracker = TelemetryTracker()
    with pytest.raises(ValueError):
        tracker.record_tokens(-10, 50)


def test_telemetry_span_measurement():
    """Tests span latency measurement and span collection."""
    tracker = TelemetryTracker()

    with tracker.start_span("db_query") as span:
        time.sleep(0.01)  # 10ms
        assert span.name == "db_query"

    assert len(tracker.spans) == 1
    recorded_span = tracker.spans[0]
    assert recorded_span.name == "db_query"
    assert recorded_span.duration_ms >= 5.0
    assert tracker.total_latency_ms >= 5.0


def test_telemetry_tool_call_recording():
    """Tests tool call metrics aggregation for success and failure."""
    tracker = TelemetryTracker()

    tracker.record_tool_call("fetch_data", duration_ms=12.5, success=True)
    tracker.record_tool_call("fetch_data", duration_ms=18.0, success=True)
    tracker.record_tool_call("fetch_data", duration_ms=5.0, success=False, error="Timeout")

    metrics = tracker.tool_metrics["fetch_data"]
    assert metrics["calls"] == 3
    assert metrics["successes"] == 2
    assert metrics["failures"] == 1
    assert metrics["last_error"] == "Timeout"
    assert metrics["total_duration_ms"] == 35.5
    assert len(tracker.traces) == 3


def test_telemetry_summary_and_reset():
    """Tests summary serialization and state reset."""
    tracker = TelemetryTracker()
    tracker.record_tokens(100, 20)
    tracker.set_status_code(201)

    summary = tracker.summary()
    assert summary["tokens_in"] == 100
    assert summary["tokens_out"] == 20
    assert summary["status_code"] == 201

    tracker.reset()
    assert tracker.total_tokens == 0
    assert tracker.status_code == 200
    assert len(tracker.traces) == 0


def test_trajectory_compactor_and_caching():
    """Tests TrajectoryCompactor token estimation, caching tags, and compaction."""
    compactor = TrajectoryCompactor(max_context_tokens=1000)

    compactor.add_turn(role="user", content="Initial task goal", cache_control=True)
    compactor.add_turn(role="assistant", content="Analyzing requirements...")
    compactor.add_turn(role="tool", content={"rows": ["data" * 50]})
    compactor.add_turn(role="assistant", content="Final answer")

    messages = compactor.get_messages(apply_caching=True)
    assert len(messages) == 4
    # First turn has ephemeral prompt caching enabled
    assert isinstance(messages[0]["content"], list)
    assert messages[0]["content"][0]["cache_control"] == {"type": "ephemeral"}

    # Test compaction with small target tokens
    compacted = compactor.compact(target_tokens=50, preserve_recent=2)
    assert len(compacted) <= 4


def test_span_context_to_dict():
    """Verifies that SpanContext to_dict returns formatted dictionary."""
    from lixvn.telemetry import SpanContext

    span = SpanContext(name="test_span")
    time.sleep(0.005)
    span.finish()
    d = span.to_dict()
    assert d["name"] == "test_span"
    assert d["duration_ms"] >= 1.0
    assert d["end_time"] is not None


def test_trajectory_hard_context_limit():
    """Verifies ContextLimitExceededError when turns exceed hard window."""
    from lixvn.errors import ContextLimitExceededError

    compactor = TrajectoryCompactor(max_context_tokens=20)
    compactor.add_turn(role="user", content="A" * 200)
    compactor.add_turn(role="assistant", content="B" * 200)

    with pytest.raises(ContextLimitExceededError):
        compactor.compact(target_tokens=5)

