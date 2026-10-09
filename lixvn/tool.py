"""Tool abstraction, schema extraction, and execution wrapper for the Lixvn SDK."""

import inspect
import re
import types
from typing import Any, Callable, Dict, List, Optional, Union, get_args, get_origin
from lixvn.errors import ToolExecutionError


def _map_py_type_to_json_schema(annotation: Any) -> Dict[str, Any]:
    """Maps Python typing annotations to JSON Schema definitions."""
    if annotation is inspect.Parameter.empty or annotation is Any:
        return {"type": "string"}

    origin = get_origin(annotation)
    if origin in (Union, getattr(types, "UnionType", Union)):
        # Handle Optional[T] / Union[T, NoneType] / T | None
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if len(args) == 1:
            return _map_py_type_to_json_schema(args[0])
        return {"type": "string"}

    if annotation is str:
        return {"type": "string"}
    elif annotation is int:
        return {"type": "integer"}
    elif annotation is float:
        return {"type": "number"}
    elif annotation is bool:
        return {"type": "boolean"}
    elif annotation is dict or origin is dict:
        return {"type": "object"}
    elif annotation is list or origin is list:
        return {"type": "array"}

    return {"type": "string"}


def _parse_docstring_param_descriptions(docstring: str) -> Dict[str, str]:
    """Parses standard Sphinx or Google style parameter descriptions from docstrings."""
    descriptions: Dict[str, str] = {}
    if not docstring:
        return descriptions

    # Match Sphinx style: :param <name>: <desc>
    sphinx_matches = re.findall(r":param\s+([a-zA-Z0-9_]+):\s*(.+)", docstring)
    for name, desc in sphinx_matches:
        descriptions[name] = desc.strip()

    # Match Google style: <name> (<type>): <desc> or <name>: <desc>
    google_matches = re.findall(r"^\s*([a-zA-Z0-9_]+)(?:\s*\([^)]*\))?:\s*(.+)$", docstring, flags=re.MULTILINE)
    for name, desc in google_matches:
        if name not in descriptions:
            descriptions[name] = desc.strip()

    return descriptions


class Tool:
    """Represents a callable tool with inspectable Anthropic-compatible JSON schema."""

    def __init__(
        self,
        func: Callable[..., Any],
        name: Optional[str] = None,
        description: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not callable(func):
            raise TypeError("Tool must be initialized with a callable function.")

        self.func = func
        self.name: str = name or func.__name__
        self.raw_docstring: str = inspect.getdoc(func) or ""
        self.description: str = description or (self.raw_docstring.split("\n\n")[0].strip() if self.raw_docstring else f"Executes {self.name}")
        self.input_schema: Dict[str, Any] = schema or self._generate_schema()

    def _generate_schema(self) -> Dict[str, Any]:
        """Infers Anthropic-compliant JSON Schema from the callable signature and docstring."""
        sig = inspect.signature(self.func)
        param_docs = _parse_docstring_param_descriptions(self.raw_docstring)
        properties: Dict[str, Any] = {}
        required: List[str] = []

        for param_name, param in sig.parameters.items():
            if param_name in {"self", "cls"}:
                continue
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue

            param_schema = _map_py_type_to_json_schema(param.annotation)
            if param_name in param_docs:
                param_schema["description"] = param_docs[param_name]
            else:
                param_schema["description"] = f"Parameter '{param_name}'"

            properties[param_name] = param_schema

            if param.default is inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }

    def execute(self, **kwargs: Any) -> Any:
        """Executes the wrapped function with provided keyword arguments, capturing errors."""
        try:
            return self.func(**kwargs)
        except Exception as e:
            raise ToolExecutionError(tool_name=self.name, message=str(e), original_error=e) from e

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Enables direct invocation of the tool instance."""
        try:
            return self.func(*args, **kwargs)
        except Exception as e:
            raise ToolExecutionError(tool_name=self.name, message=str(e), original_error=e) from e

    def to_anthropic_spec(self) -> Dict[str, Any]:
        """Returns the Anthropic tool definition dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }

    def __repr__(self) -> str:
        return f"<Tool name={self.name!r} params={list(self.input_schema.get('properties', {}).keys())}>"


def tool(
    func_or_name: Union[Callable[..., Any], str, None] = None,
    description: Optional[str] = None,
    schema: Optional[Dict[str, Any]] = None,
    name: Optional[str] = None,
) -> Any:
    """Decorator to convert a standard Python function into an inspectable Tool instance."""
    resolved_name = name or (func_or_name if isinstance(func_or_name, str) else None)

    if callable(func_or_name):
        return Tool(func=func_or_name, name=resolved_name, description=description, schema=schema)

    def decorator(fn: Callable[..., Any]) -> Tool:
        return Tool(func=fn, name=resolved_name, description=description, schema=schema)

    return decorator
