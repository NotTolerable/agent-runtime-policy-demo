"""Lightweight runtime policy engine for tool-call decisions."""

from typing import Any

from models import PolicyDecision

ALLOW_SAFE_READ = "ALLOW_SAFE_READ"
ALLOW_SAFE_SUMMARY = "ALLOW_SAFE_SUMMARY"
BLOCK_SECRET_ACCESS = "BLOCK_SECRET_ACCESS"
BLOCK_EXTERNAL_WEBHOOK = "BLOCK_EXTERNAL_WEBHOOK"
BLOCK_SECRET_LIKE_PAYLOAD = "BLOCK_SECRET_LIKE_PAYLOAD"
BLOCK_UNKNOWN_TOOL = "BLOCK_UNKNOWN_TOOL"

SAFE_TOOL_RULES = {
    "read_github_issue": ALLOW_SAFE_READ,
    "summarize_issue": ALLOW_SAFE_SUMMARY,
}

SECRET_LIKE_MARKERS = (
    "API_KEY",
    "SECRET",
    "TOKEN",
    "sk-",
    "password",
)

EXTERNAL_TRANSFER_MARKERS = (
    "http://",
    "https://",
    "webhook",
    "callback_url",
    "external_url",
)


def evaluate_policy(tool_name: str, args: dict[str, Any]) -> PolicyDecision:
    """Evaluate whether a tool call should be allowed before execution."""
    normalized_tool_name = tool_name.strip()

    if normalized_tool_name == "read_repo_secret":
        return _block(
            BLOCK_SECRET_ACCESS,
            "Blocked because reading repository secrets is not allowed in this demo.",
        )

    if normalized_tool_name == "send_webhook":
        return _block(
            BLOCK_EXTERNAL_WEBHOOK,
            "Blocked because sending data to an external webhook is not allowed.",
        )

    if _contains_secret_like_value(args):
        return _block(
            BLOCK_SECRET_LIKE_PAYLOAD,
            "Blocked because the tool arguments contain a secret-like value or marker.",
        )

    if _contains_external_transfer_attempt(args):
        return _block(
            BLOCK_EXTERNAL_WEBHOOK,
            "Blocked because the tool arguments appear to request external data transfer.",
        )

    if normalized_tool_name in SAFE_TOOL_RULES:
        rule_id = SAFE_TOOL_RULES[normalized_tool_name]
        reason = f"Allowed because {normalized_tool_name} is an approved safe demo tool."
        return PolicyDecision(
            decision="allow",
            allowed=True,
            reason=reason,
            rule_id=rule_id,
        )

    return _block(
        BLOCK_UNKNOWN_TOOL,
        f"Blocked because {normalized_tool_name} is not an approved demo tool.",
    )


def _block(rule_id: str, reason: str) -> PolicyDecision:
    return PolicyDecision(
        decision="block",
        allowed=False,
        reason=reason,
        rule_id=rule_id,
    )


def _contains_secret_like_value(value: Any) -> bool:
    return _contains_marker(value, SECRET_LIKE_MARKERS)


def _contains_external_transfer_attempt(value: Any) -> bool:
    return _contains_marker(value, EXTERNAL_TRANSFER_MARKERS)


def _contains_marker(value: Any, markers: tuple[str, ...]) -> bool:
    if isinstance(value, dict):
        return any(
            _contains_marker(key, markers) or _contains_marker(item, markers)
            for key, item in value.items()
        )

    if isinstance(value, (list, tuple, set)):
        return any(_contains_marker(item, markers) for item in value)

    if value is None:
        return False

    text = str(value).lower()
    return any(marker.lower() in text for marker in markers)
