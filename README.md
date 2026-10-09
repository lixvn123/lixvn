<div align="center">

# ⚡ Lixvn

**The Open Runtime for Autonomous LLM Agents & Multi-Agent Swarms**

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Anthropic Claude](https://img.shields.io/badge/Anthropic-Claude%203.5%20Sonnet-amber.svg)](https://docs.anthropic.com/en/docs/about-claude/models)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)

*Deterministic tool invocation, structured agent delegation, and end-to-end trace observability powered by Claude Console APIs.*

[Landing Page](https://lixvn.dev) • [Documentation](#quickstart) • [Claude Integration](#anthropic-claude-integration) • [Architecture](#architecture)

</div>

---

## 🌟 Overview

Lixvn provides modular execution infrastructure for production AI agents. Designed specifically to run on Anthropic's state-of-the-art Claude 3.5 Sonnet and Haiku models, Lixvn solves core challenges in agent deployment:

- **200K Context Trajectory Management**: Automatically compacts and prunes agent scratchpads while retaining long-context fidelity.
- **Deterministic Tool Calling**: Validates arguments against Pydantic schemas before invocation, preventing runtime errors.
- **Self-Healing Tool Dispatch**: Automatically catches and feeds tool exceptions back to Claude with diagnostic prompts for self-repair.
- **OpenTelemetry Tracing**: Real-time visualization of agent decision trees, tool latency, and token consumption.

---

## 🚀 Quickstart

```bash
pip install agentpulse-runtime anthropic
```

```python
from agentpulse import SwarmRuntime, Agent
from anthropic import Anthropic

client = Anthropic(api_key="your-api-key")
runtime = SwarmRuntime(model="claude-3-5-sonnet-latest", engine=client)

@runtime.tool
def get_system_metrics() -> dict:
    """Fetches real-time server cluster telemetry."""
    return {"status": "healthy", "cpu_pct": 24.2, "latency_ms": 12}

analyst = Agent(name="DevOps Analyst", role="Investigate health status")
result = runtime.dispatch("Check cluster state and report anomalies", agents=[analyst])
print(result.summary)
```

---

## 🏗️ Architecture

```
User Goal ➔ Planner Agent (Claude 3.5 Sonnet) ➔ Subagent Swarms ➔ Tool Sandbox ➔ Telemetry
                         │                                 │
                         └─────── Prompt Caching Cache ────┘
```

---

## 📄 License

Distributed under the Apache-2.0 License. See `LICENSE` for details.
