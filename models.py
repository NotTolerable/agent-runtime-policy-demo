"""Core data models for the Agent Runtime Policy Demo."""

from dataclasses import dataclass
from typing import Any


@dataclass
class ToolCall:
    """A requested tool call before policy evaluation."""

    tool_name: str
    args: dict[str, Any]


@dataclass
class PolicyDecision:
    """The policy engine's decision for an attempted tool call."""

    decision: str
    allowed: bool
    reason: str
    rule_id: str | None


@dataclass
class TraceEvent:
    """A JSON-serializable record of an attempted tool call."""

    step: int
    tool_name: str
    args: dict[str, Any]
    decision: str
    allowed: bool
    reason: str
    output: str | None
