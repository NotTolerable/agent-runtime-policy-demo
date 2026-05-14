"""Simple JSON-style trace logging for policy-gated tool calls."""

from dataclasses import asdict
from typing import Any

from models import PolicyDecision, TraceEvent


class TraceLog:
    """In-memory trace log that records tool attempts in order."""

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    def record(
        self,
        tool_name: str,
        args: dict[str, Any],
        decision: PolicyDecision,
        output: str | None,
    ) -> dict[str, Any]:
        """Record one attempted tool call and return the JSON-style event."""
        event = TraceEvent(
            step=len(self._events) + 1,
            tool_name=tool_name,
            args=args,
            decision=decision.decision,
            allowed=decision.allowed,
            reason=decision.reason,
            output=output,
        )
        event_dict = asdict(event)
        event_dict["rule_id"] = decision.rule_id
        event_dict["blocked"] = not decision.allowed
        self._events.append(event_dict)
        return event_dict

    def events(self) -> list[dict[str, Any]]:
        """Return recorded trace events in order for display or tests."""
        return list(self._events)

    def allowed_count(self) -> int:
        """Return the number of allowed tool attempts."""
        return sum(1 for event in self._events if event["allowed"])

    def blocked_count(self) -> int:
        """Return the number of blocked tool attempts."""
        return sum(1 for event in self._events if event["blocked"])
