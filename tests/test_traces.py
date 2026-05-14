"""Trace logging and policy-gated tool execution tests."""

import tools
from traces import TraceLog
from tools import execute_tool


def test_trace_events_are_recorded_in_order():
    trace = TraceLog()

    first = execute_tool("read_github_issue", {"mock_issue_content": "Issue one"}, trace)
    second = execute_tool("summarize_issue", {"issue_text": "Issue two"}, trace)

    assert first["step"] == 1
    assert second["step"] == 2
    assert [event["step"] for event in trace.events()] == [1, 2]


def test_allowed_tool_calls_record_allowed_true():
    trace = TraceLog()

    event = execute_tool("read_github_issue", {"mock_issue_content": "Safe issue"}, trace)

    assert event["allowed"] is True
    assert event["blocked"] is False
    assert event["decision"] == "allow"
    assert event["output"] == "Safe issue"


def test_blocked_tool_calls_record_allowed_false():
    trace = TraceLog()

    event = execute_tool("read_repo_secret", {"secret_name": "DEPLOY_TOKEN"}, trace)

    assert event["allowed"] is False
    assert event["blocked"] is True
    assert event["decision"] == "block"
    assert event["output"] is None


def test_blocked_tool_calls_do_not_execute_underlying_risky_tool(monkeypatch):
    trace = TraceLog()
    executed = {"called": False}

    def fake_read_repo_secret(args):
        executed["called"] = True
        return "should not be returned"

    monkeypatch.setattr(tools, "read_repo_secret", fake_read_repo_secret)

    event = execute_tool("read_repo_secret", {"secret_name": "DEPLOY_TOKEN"}, trace)

    assert event["blocked"] is True
    assert executed["called"] is False


def test_trace_events_include_non_empty_reasons():
    trace = TraceLog()

    execute_tool("read_github_issue", {"mock_issue_content": "Safe issue"}, trace)
    execute_tool("send_webhook", {"url": "https://external-webhook.example.com"}, trace)

    assert all(event["reason"] for event in trace.events())


def test_no_real_network_call_occurs_for_send_webhook(monkeypatch):
    trace = TraceLog()
    network_attempt = {"called": False}

    def fake_send_webhook(args):
        network_attempt["called"] = True
        return "network would have been called"

    monkeypatch.setattr(tools, "send_webhook", fake_send_webhook)

    event = execute_tool(
        "send_webhook",
        {"url": "https://external-webhook.example.com", "payload": "demo"},
        trace,
    )

    assert event["blocked"] is True
    assert event["output"] is None
    assert network_attempt["called"] is False
