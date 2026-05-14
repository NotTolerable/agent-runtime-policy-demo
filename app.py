"""Streamlit UI for the Agent Runtime Policy Demo."""

from pathlib import Path
from typing import Any

import streamlit as st

from agent import USER_TASK, run_attack_scenario

SAMPLE_ATTACK_PATH = Path(__file__).with_name("sample_attack.md")

POLICY_RULES = [
    "Allow reading GitHub issues",
    "Allow summarizing issues",
    "Block repo secret access",
    "Block external webhook calls",
    "Block secret-like payloads such as API_KEY, SECRET, TOKEN, sk-, or password",
]


def main() -> None:
    """Render the Streamlit demo."""
    st.set_page_config(
        page_title="Agent Runtime Policy Demo",
        page_icon="🛡️",
        layout="wide",
    )

    st.title("Agent Runtime Policy Demo")
    st.markdown(
        "A mock DevOps agent reads a GitHub issue with prompt injection, then a "
        "lightweight policy layer blocks risky tool calls."
    )

    st.divider()
    _render_user_task()
    _render_mock_issue()
    _render_policy_rules()

    st.divider()
    st.subheader("Run scenario")
    st.markdown(
        "Click the button to run the scripted agent flow. No real GitHub, secret, "
        "LLM, webhook, or network integration is used."
    )

    if st.button("Run agent scenario", type="primary"):
        result = run_attack_scenario()
        _render_timeline(result["trace_events"])
        _render_final_verdict(result)


def _render_user_task() -> None:
    st.subheader("User task")
    st.info(f'"{USER_TASK}"')


def _render_mock_issue() -> None:
    st.subheader("Mock GitHub issue")
    st.markdown(
        "This local mock issue contains normal visible bug-report content plus a "
        "hidden injected instruction attempting to make the agent access secrets "
        "and send them externally. It contains no real secrets."
    )
    st.code(SAMPLE_ATTACK_PATH.read_text(encoding="utf-8"), language="markdown")


def _render_policy_rules() -> None:
    st.subheader("Policy rules")
    for rule in POLICY_RULES:
        st.markdown(f"- {rule}")


def _render_timeline(trace_events: list[dict[str, Any]]) -> None:
    st.subheader("Agent/tool-call timeline")
    allowed_count = sum(1 for event in trace_events if event["allowed"])
    blocked_count = sum(1 for event in trace_events if event["blocked"])

    allowed_col, blocked_col = st.columns(2)
    allowed_col.metric("Allowed tool calls", allowed_count)
    blocked_col.metric("Blocked tool calls", blocked_count)

    for event in trace_events:
        label = "ALLOWED" if event["allowed"] else "BLOCKED"
        title = f"Step {event['step']}: {event['tool_name']} — {label}"
        with st.expander(title, expanded=True):
            if event["allowed"]:
                st.success("ALLOWED")
            else:
                st.error("BLOCKED")

            st.markdown(f"**Reason:** {event['reason']}")
            st.markdown(f"**Rule ID:** `{event['rule_id']}`")
            st.markdown("**Arguments**")
            st.json(event["args"])

            if event["allowed"]:
                st.markdown("**Output**")
                st.code(event["output"] or "", language="text")
            else:
                st.warning("Execution was blocked before the tool could run.")


def _render_final_verdict(result: dict[str, Any]) -> None:
    st.subheader("Final verdict")
    st.success(
        "The agent completed the safe issue-summary task while the policy layer "
        "blocked secret access and external exfiltration attempts."
    )
    st.markdown(result["final_summary"])


if __name__ == "__main__":
    main()
