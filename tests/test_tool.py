"""Unit tests for lixvn.Tool abstraction, schema extraction, and execution."""

from typing import Dict, List, Optional
import pytest
from lixvn.errors import ToolExecutionError
from lixvn.tool import Tool, tool


def sample_calc(a: int, b: int, operation: str = "add") -> int:
    """Performs integer calculation.

    :param a: The first integer operand.
    :param b: The second integer operand.
    :param operation: The operation to perform ('add' or 'mul').
    """
    if operation == "add":
        return a + b
    elif operation == "mul":
        return a * b
    raise ValueError(f"Unknown operation: {operation}")


def test_tool_schema_extraction():
    """Verifies that Tool extracts parameter types, required fields, and descriptions."""
    t = Tool(sample_calc)
    assert t.name == "sample_calc"
    assert "Performs integer calculation" in t.description

    schema = t.input_schema
    assert schema["type"] == "object"
    props = schema["properties"]
    assert props["a"]["type"] == "integer"
    assert props["b"]["type"] == "integer"
    assert props["operation"]["type"] == "string"

    # 'a' and 'b' have no default, so they are required. 'operation' has a default.
    assert "a" in schema["required"]
    assert "b" in schema["required"]
    assert "operation" not in schema["required"]


def test_tool_execution_success():
    """Tests successful execution via execute() and direct __call__()."""
    t = Tool(sample_calc)
    assert t.execute(a=10, b=5, operation="add") == 15
    assert t(a=4, b=6, operation="mul") == 24
    assert t(a=7, b=3) == 10  # default operation 'add'


def test_tool_execution_error_handling():
    """Verifies that runtime exceptions inside the function raise ToolExecutionError."""
    t = Tool(sample_calc)
    with pytest.raises(ToolExecutionError) as exc_info:
        t.execute(a=1, b=2, operation="divide")

    err = exc_info.value
    assert err.tool_name == "sample_calc"
    assert "Unknown operation" in str(err)
    assert isinstance(err.original_error, ValueError)


def test_tool_decorator_bare():
    """Tests @tool decorator applied directly without arguments."""
    @tool
    def fetch_weather(city: str) -> dict:
        """Fetches weather metrics for a specified city."""
        return {"city": city, "temp_c": 22.5}

    assert isinstance(fetch_weather, Tool)
    assert fetch_weather.name == "fetch_weather"
    assert fetch_weather.execute(city="Singapore") == {"city": "Singapore", "temp_c": 22.5}


def test_tool_decorator_with_args():
    """Tests @tool decorator applied with custom name and description."""
    @tool(name="custom_weather", description="Custom weather retrieval service")
    def fetch_weather_v2(city: str) -> dict:
        return {"city": city, "condition": "Sunny"}

    assert isinstance(fetch_weather_v2, Tool)
    assert fetch_weather_v2.name == "custom_weather"
    assert fetch_weather_v2.description == "Custom weather retrieval service"
    assert fetch_weather_v2(city="Tokyo") == {"city": "Tokyo", "condition": "Sunny"}


def test_tool_to_anthropic_spec():
    """Ensures to_anthropic_spec matches Anthropic Messages API tool format."""
    def test_fn(query: str, limit: Optional[int] = 10) -> List[Dict[str, str]]:
        """Searches documents.

        :param query: Query string to match against document index.
        :param limit: Maximum number of results to return.
        """
        return []

    t = Tool(test_fn)
    spec = t.to_anthropic_spec()
    assert spec["name"] == "test_fn"
    assert "Searches documents" in spec["description"]
    assert spec["input_schema"]["type"] == "object"
    assert "query" in spec["input_schema"]["properties"]
    assert spec["input_schema"]["required"] == ["query"]


def test_tool_non_callable_raises():
    """Ensures initializing Tool with non-callable raises TypeError."""
    with pytest.raises(TypeError, match="must be initialized with a callable"):
        Tool("not_a_callable")  # type: ignore


def test_tool_schema_union_syntax():
    """Verifies that Python 3.10+ union syntax (T | None) maps to the underlying primitive type."""
    def query_service(item_id: int | None = None, tag: str | None = None):
        """Service query."""
        pass

    t = Tool(query_service)
    props = t.input_schema["properties"]
    assert props["item_id"]["type"] == "integer"
    assert props["tag"]["type"] == "string"
    assert "item_id" not in t.input_schema.get("required", [])


def test_tool_schema_varargs_and_kwargs_excluded():
    """Verifies that *args and **kwargs are excluded from schema properties and required fields."""
    def flexible_calc(base: float, *args, **kwargs):
        """Flexible calculator."""
        return base

    t = Tool(flexible_calc)
    props = t.input_schema["properties"]
    assert "base" in props
    assert props["base"]["type"] == "number"
    assert "args" not in props
    assert "kwargs" not in props
    assert t.input_schema["required"] == ["base"]

