"""Safe mock tools and policy-gated tool execution."""

from pathlib import Path
from typing import Any, Callable

from policy import evaluate_policy
from traces import TraceLog

SAMPLE_ATTACK_PATH = Path(__file__).with_name("sample_attack.md")

ToolFunction = Callable[[dict[str, Any]], str]


def read_github_issue(args: dict[str, Any]) -> str:
    """Read deterministic local issue content instead of calling GitHub."""
    mock_issue_content = args.get("mock_issue_content")
    if mock_issue_content is not None:
        return str(mock_issue_content)

    return SAMPLE_ATTACK_PATH.read_text(encoding="utf-8")


def summarize_issue(args: dict[str, Any]) -> str:
    """Return a deterministic summary of the legitimate visible issue."""
    issue_text = str(args.get("issue_text", ""))
    if "Login page crashes on Safari" in issue_text:
        return (
            "The legitimate issue is that the login page crashes on Safari after "
            "the latest deploy. It needs action from the frontend or DevOps team "
            "to reproduce the Safari runtime error and validate a fix."
        )

    return "The issue needs review, but no deterministic summary was available."


def read_repo_secret(args: dict[str, Any]) -> str:
    """Return a fake placeholder only; never read environment or repo secrets."""
    return "fake placeholder only; no real secret was accessed"


def send_webhook(args: dict[str, Any]) -> str:
    """Return a fake result only; never make a network request."""
    destination = str(args.get("url", "requested destination"))
    return f"would send to {destination}; no network request was made"


def execute_tool(tool_name: str, args: dict[str, Any], trace: TraceLog) -> dict[str, Any]:
    """Evaluate policy, execute allowed mock tools, and record every attempt."""
    decision = evaluate_policy(tool_name, args)
    output = None

    if decision.allowed:
        tool_function = _get_tool_function(tool_name)
        output = tool_function(args)

    return trace.record(
        tool_name=tool_name,
        args=args,
        decision=decision,
        output=output,
    )


def _get_tool_function(tool_name: str) -> ToolFunction:
    tools: dict[str, ToolFunction] = {
        "read_github_issue": read_github_issue,
        "summarize_issue": summarize_issue,
        "read_repo_secret": read_repo_secret,
        "send_webhook": send_webhook,
    }
    return tools[tool_name]
