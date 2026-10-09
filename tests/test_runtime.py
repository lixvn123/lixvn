"""Unit and integration tests for lixvn.SwarmRuntime, DispatchResult, and SafeDatabase."""

import datetime
import types
import pytest
from lixvn.agent import Agent
from lixvn.database import SafeDatabase
from lixvn.errors import ConfigurationError, DatabaseQueryError
from lixvn.runtime import DispatchResult, SwarmRuntime


def test_runtime_initialization_defaults():
    """Verifies default model and sub-components in SwarmRuntime."""
    runtime = SwarmRuntime()
    assert runtime.model == "claude-3-5-sonnet-latest"
    assert isinstance(runtime.db, SafeDatabase)
    assert len(runtime.tools) == 0
    assert runtime.telemetry.total_tokens == 0


def test_runtime_invalid_model_raises():
    """Ensures empty or whitespace model raises ConfigurationError."""
    with pytest.raises(ConfigurationError):
        SwarmRuntime(model="")
    with pytest.raises(ConfigurationError):
        SwarmRuntime(model="   ")


def test_runtime_tool_decorator_registers():
    """Verifies that @runtime.tool decorator registers tool in runtime.tools registry."""
    runtime = SwarmRuntime()

    @runtime.tool
    def calculate_tax(amount: float, rate: float = 0.08) -> float:
        """Calculates tax amount."""
        return amount * rate

    assert "calculate_tax" in runtime.tools
    assert runtime.tools["calculate_tax"](amount=100.0) == 8.0


def test_runtime_dispatch_positional_and_keyword():
    """Tests dispatch invocation with positional and keyword goal arguments."""
    runtime = SwarmRuntime()

    analyst = Agent(name="DevOps Analyst", role="Investigate health status")

    # Positional goal
    res1 = runtime.dispatch("Check cluster state and report anomalies", agents=[analyst])
    assert isinstance(res1, DispatchResult)
    assert res1.status_code == 200
    assert res1.total_tokens > 0
    assert "DevOps Analyst" in res1.summary

    # Keyword goal
    planner = Agent(name="Lead Architect", role="Planning")
    res2 = runtime.dispatch(goal="Analyze customer churn", agents=[planner])
    assert isinstance(res2, DispatchResult)
    assert res2.status_code == 200
    assert res2.total_tokens > 0


def test_runtime_dispatch_validation_errors():
    """Ensures empty goal or missing agents raise ValueError."""
    runtime = SwarmRuntime()
    agent = Agent(name="A1", role="R1")

    with pytest.raises(ValueError, match="non-empty 'goal' string"):
        runtime.dispatch("", agents=[agent])

    with pytest.raises(ValueError, match="at least one Agent"):
        runtime.dispatch("Some goal", agents=[])


def test_safe_database_queries():
    """Tests that SafeDatabase executes read queries and blocks destructive statements."""
    db = SafeDatabase()

    # Valid read query
    result = db.safe_execute("SELECT customer_id, name, churn_risk_pct FROM customer_churn WHERE churn_risk_pct > 50")
    assert result["status"] == "ok"
    assert result["row_count"] >= 3
    assert any(row["name"] == "Acme Corp" for row in result["rows"])

    # Destructive query blocked
    bad_result = db.safe_execute("DROP TABLE customer_churn")
    assert bad_result["status"] == "error"
    assert "Unsafe query" in bad_result["error"]

    # Destructive query with raise_on_error
    with pytest.raises(DatabaseQueryError):
        db.safe_execute("DELETE FROM customer_churn", raise_on_error=True)

    # Multi-statement injection blocked
    inject_result = db.safe_execute("SELECT * FROM customer_churn; DROP TABLE customer_churn;")
    assert inject_result["status"] == "error"
    assert "Multiple SQL statements" in inject_result["error"]


def test_runtime_mock_anthropic_engine_execution():
    """Tests SwarmRuntime execution when an Anthropic client engine is provided."""
    runtime = SwarmRuntime(model="claude-3-5-sonnet-latest")

    @runtime.tool
    def query_cluster() -> dict:
        """Returns cluster metrics."""
        return {"nodes": 5, "status": "all_healthy"}

    # Mock Anthropic client
    class MockUsage:
        input_tokens = 450
        output_tokens = 120
        cache_read_input_tokens = 100

    class MockToolBlock:
        type = "tool_use"
        id = "toolu_123"
        name = "query_cluster"
        input = {}

    class MockTextBlock:
        type = "text"
        text = "Cluster query complete. All 5 nodes healthy."

    call_count = 0

    def mock_create(**kwargs):
        nonlocal call_count
        call_count += 1
        resp = types.SimpleNamespace()
        resp.usage = MockUsage()
        if call_count == 1:
            resp.content = [MockToolBlock()]
        else:
            resp.content = [MockTextBlock()]
        return resp

    mock_client = types.SimpleNamespace()
    mock_client.messages = types.SimpleNamespace()
    mock_client.messages.create = mock_create

    runtime.engine = mock_client
    agent = Agent(name="DevOps Agent", role="Cluster auditor")

    result = runtime.dispatch("Audit cluster", agents=[agent])
    assert result.status == "success"
    assert result.status_code == 200
    assert len(result.tool_calls) == 1
    assert result.tool_calls[0]["tool"] == "query_cluster"
    assert "All 5 nodes healthy" in result.summary
    assert call_count == 2


def test_runtime_tool_decorator_custom_name():
    """Verifies that @runtime.tool with name parameter registers with the specified name."""
    runtime = SwarmRuntime()

    @runtime.tool(name="custom_scanner")
    def scan_ports(host: str) -> dict:
        return {"host": host, "open_ports": [80, 443]}

    assert "custom_scanner" in runtime.tools
    assert runtime.tools["custom_scanner"](host="localhost")["open_ports"] == [80, 443]


def test_runtime_register_tool_and_callable():
    """Verifies register_tool works with both Tool instances and raw callables."""
    from lixvn.tool import Tool

    runtime = SwarmRuntime()

    def my_raw_func(x: int) -> int:
        return x * 2

    # Register raw callable
    t1 = runtime.register_tool(my_raw_func, name="double_it")
    assert "double_it" in runtime.tools
    assert t1(x=5) == 10

    # Register Tool instance
    t2 = Tool(func=lambda: "pong", name="ping")
    runtime.register_tool(t2)
    assert "ping" in runtime.tools
    assert runtime.tools["ping"]() == "pong"


def test_safe_database_adversarial_stress():
    """Validates SafeDatabase against semicolon inputs, non-strings, literal quotes, and PRAGMAs."""
    db = SafeDatabase()

    # Semicolon inputs
    res_semi = db.safe_execute(";")
    assert res_semi["status"] == "error"
    assert "Query is empty" in res_semi["error"]

    res_multi_semi = db.safe_execute("; ; ;")
    assert res_multi_semi["status"] == "error"
    assert "Query is empty" in res_multi_semi["error"]

    # None and numeric non-string inputs
    res_none = db.safe_execute(None)
    assert res_none["status"] == "error"
    assert "non-empty string" in res_none["error"]

    res_num = db.safe_execute(42)  # type: ignore
    assert res_num["status"] == "error"
    assert "non-empty string" in res_num["error"]

    # Semicolon inside string literals
    res_lit = db.safe_execute("SELECT * FROM customer_churn WHERE name = 'Acme; Corp'")
    assert res_lit["status"] == "ok"
    assert isinstance(res_lit["rows"], list)

    # Keyword inside string literals
    res_kw = db.safe_execute("SELECT * FROM security_audit_log WHERE action = 'UPDATE'")
    assert res_kw["status"] == "ok"
    assert any(row["action"] == "UPDATE" or "UPDATE" in str(row) for row in res_kw["rows"]) or res_kw["row_count"] == 0

    # Unauthorized and dangerous PRAGMAs
    res_pragma_bad = db.safe_execute("PRAGMA writable_schema = ON")
    assert res_pragma_bad["status"] == "error"
    assert "PRAGMA statement is prohibited" in res_pragma_bad["error"]

    # Authorized read-only PRAGMA
    res_pragma_ok = db.safe_execute("PRAGMA table_info(customer_churn)")
    assert res_pragma_ok["status"] == "ok"
    assert len(res_pragma_ok["rows"]) > 0

    # Multi-line comment stripping
    res_comment = db.safe_execute("/* Multi-line\ncomment with DROP\n*/ SELECT * FROM customer_churn LIMIT 1")
    assert res_comment["status"] == "ok"
    assert res_comment["row_count"] == 1


def test_anthropic_engine_none_cache_tokens_and_non_primitive_tools():
    """Verifies that cache_read_input_tokens: None and non-primitive tool returns do not crash the runtime."""
    runtime = SwarmRuntime(model="claude-3-5-sonnet-latest", fallback_on_error=False)

    @runtime.tool
    def get_schedule():
        """Returns calendar date object."""
        return {"date": datetime.date(2026, 10, 9), "status": "active"}

    class MockUsage:
        input_tokens = 200
        output_tokens = 50
        cache_read_input_tokens = None  # Live Anthropic API returns None when cache miss

    class MockToolBlock:
        type = "tool_use"
        id = "tool_cal_1"
        name = "get_schedule"
        input = {}

    class MockTextBlock:
        type = "text"
        text = "Schedule fetched successfully."

    calls = 0

    def mock_create(**kwargs):
        nonlocal calls
        calls += 1
        resp = types.SimpleNamespace()
        resp.usage = MockUsage()
        if calls == 1:
            resp.content = [MockToolBlock()]
        else:
            resp.content = [MockTextBlock()]
        return resp

    mock_client = types.SimpleNamespace()
    mock_client.messages = types.SimpleNamespace()
    mock_client.messages.create = mock_create

    runtime.engine = mock_client
    agent = Agent(name="Scheduler Agent", role="Calendar Coordinator")

    result = runtime.dispatch("Get tomorrow schedule", agents=[agent])
    assert result.status == "success"
    assert len(result.tool_calls) == 1
    assert result.tool_calls[0]["tool"] == "get_schedule"
    assert len(result.agent_traces) == 1
    assert any("Executed tool" in action for action in result.agent_traces[0]["actions"])
    assert runtime.compactor.total_tokens() > 0


def test_simulation_engine_arbitrary_custom_tools():
    """Verifies offline simulation handles arbitrary user-registered tools without hardcoded names."""
    runtime = SwarmRuntime()

    @runtime.tool
    def calculate_commission(sales: float, rate: float = 0.1) -> dict:
        """Calculates broker commission."""
        return {"commission": sales * rate, "status": "approved"}

    broker = Agent(name="Broker Agent", role="Commission auditor")
    result = runtime.dispatch("Calculate quarterly commission", agents=[broker])

    assert result.status == "success"
    assert result.status_code == 200
    assert len(result.tool_calls) == 1
    assert result.tool_calls[0]["tool"] == "calculate_commission"
    assert "calculate_commission" in result.summary
    assert "approved" in result.summary
    assert len(result.agent_traces) == 1
    assert "Executed tool calculate_commission" in result.agent_traces[0]["actions"]


def test_trajectory_compactor_non_primitive_types():
    """Verifies TrajectoryCompactor handles non-primitive types in add_turn and get_messages."""
    from lixvn.trajectory import TrajectoryCompactor

    compactor = TrajectoryCompactor()
    compactor.add_turn("user", {"time": datetime.datetime.now(), "target": datetime.date(2026, 10, 9)}, cache_control=True)
    messages = compactor.get_messages(apply_caching=True)

    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert compactor.total_tokens() > 0


