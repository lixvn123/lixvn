"""Verification tests executing verbatim snippets from README.md and index.html."""

import sys
import types

# Ensure anthropic can be imported even if the optional external package is not installed in CI
if "anthropic" not in sys.modules:
    mock_anthropic = types.ModuleType("anthropic")

    class Anthropic:  # type: ignore
        def __init__(self, api_key: str = "", **kwargs):
            self.api_key = api_key
            self.messages = types.SimpleNamespace()

        def __repr__(self):
            return f"<Anthropic api_key={self.api_key!r}>"

    mock_anthropic.Anthropic = Anthropic
    sys.modules["anthropic"] = mock_anthropic


def test_readme_code_snippet_execution():
    """Verifies the exact quickstart snippet published in README.md."""
    from anthropic import Anthropic
    from lixvn import Agent, SwarmRuntime

    client = Anthropic(api_key="your-api-key")
    runtime = SwarmRuntime(model="claude-3-5-sonnet-latest", engine=client)

    @runtime.tool
    def get_system_metrics() -> dict:
        """Fetches real-time server cluster telemetry."""
        return {"status": "healthy", "cpu_pct": 24.2, "latency_ms": 12}

    analyst = Agent(name="DevOps Analyst", role="Investigate health status")
    result = runtime.dispatch("Check cluster state and report anomalies", agents=[analyst])

    assert result.summary is not None
    assert len(result.summary) > 0
    assert "DevOps Analyst" in result.summary
    assert "healthy" in result.summary
    assert result.status_code == 200
    assert result.total_tokens > 0


def test_landing_page_code_snippet_execution():
    """Verifies the exact interactive code preview published in index.html."""
    from anthropic import Anthropic
    from lixvn import Agent, SwarmRuntime, Tool

    client = Anthropic(api_key="your-claude-api-key")
    runtime = SwarmRuntime(model="claude-3-5-sonnet-latest", engine=client)

    @runtime.tool
    def execute_sql_query(query: str) -> dict:
        """Executes verified read queries against primary data warehouse"""
        return runtime.db.safe_execute(query)

    planner = Agent(name="Lead Architect", role="Context breakdown & planning")
    auditor = Agent(name="Security Auditor", role="SQL injection check & schema safety")

    result = runtime.dispatch(
        goal="Analyze customer churn pattern and report anomalies",
        agents=[planner, auditor],
    )

    assert result.status_code == 200
    assert result.total_tokens > 0
    assert "Lead Architect" in result.summary or "Security Auditor" in result.summary
    assert len(result.tool_calls) > 0
    assert result.tool_calls[0]["tool"] == "execute_sql_query"
    assert isinstance(execute_sql_query, Tool)


def test_snippets_without_external_engine():
    """Verifies that both snippets execute cleanly in offline simulation mode without engine passed."""
    from lixvn import Agent, SwarmRuntime, Tool

    # README pattern offline
    runtime1 = SwarmRuntime(model="claude-3-5-sonnet-latest")

    @runtime1.tool
    def get_system_metrics() -> dict:
        """Fetches real-time server cluster telemetry."""
        return {"status": "healthy", "cpu_pct": 24.2, "latency_ms": 12}

    analyst = Agent(name="DevOps Analyst", role="Investigate health status")
    res1 = runtime1.dispatch("Check cluster state and report anomalies", agents=[analyst])
    assert res1.summary is not None

    # Landing page pattern offline
    runtime2 = SwarmRuntime(model="claude-3-5-sonnet-latest")

    @runtime2.tool
    def execute_sql_query(query: str) -> dict:
        """Executes verified read queries against primary data warehouse"""
        return runtime2.db.safe_execute(query)

    planner = Agent(name="Lead Architect", role="Context breakdown & planning")
    auditor = Agent(name="Security Auditor", role="SQL injection check & schema safety")
    res2 = runtime2.dispatch(goal="Analyze customer churn pattern and report anomalies", agents=[planner, auditor])
    assert res2.total_tokens > 0
    assert isinstance(execute_sql_query, Tool)
