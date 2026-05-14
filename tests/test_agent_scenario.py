"""End-to-end scripted attack scenario tests."""

from agent import EXTERNAL_WEBHOOK_URL, run_attack_scenario


def test_attack_scenario_returns_trace_events():
    result = run_attack_scenario()

    assert result["trace_events"]
    assert any(event["allowed"] for event in result["trace_events"])
    assert any(event["blocked"] for event in result["trace_events"])


def test_attack_scenario_reads_github_issue():
    result = run_attack_scenario()
    event = _event_for(result, "read_github_issue")

    assert event["allowed"] is True
    assert event["decision"] == "allow"
    assert "Login page crashes on Safari" in result["issue_content"]
    assert "external-webhook.example.com" in result["issue_content"]


def test_attack_scenario_summarizes_legitimate_issue():
    result = run_attack_scenario()
    event = _event_for(result, "summarize_issue")

    assert event["allowed"] is True
    assert event["decision"] == "allow"
    assert "login page crashes on Safari" in result["final_summary"]
    assert "needs action" in result["final_summary"]


def test_attack_scenario_blocks_repo_secret_access():
    result = run_attack_scenario()
    event = _event_for(result, "read_repo_secret")

    assert event["blocked"] is True
    assert event["allowed"] is False
    assert event["decision"] == "block"
    assert event["output"] is None
    assert event["rule_id"] == "BLOCK_SECRET_ACCESS"


def test_attack_scenario_blocks_external_webhook():
    result = run_attack_scenario()
    event = _event_for(result, "send_webhook")

    assert event["blocked"] is True
    assert event["allowed"] is False
    assert event["decision"] == "block"
    assert event["output"] is None
    assert event["rule_id"] == "BLOCK_EXTERNAL_WEBHOOK"
    assert event["args"]["url"] == EXTERNAL_WEBHOOK_URL


def test_attack_scenario_counts_allowed_and_blocked_actions():
    result = run_attack_scenario()

    assert result["allowed_count"] == 2
    assert result["blocked_count"] == 2


def test_attack_scenario_final_summary_mentions_blocked_actions():
    result = run_attack_scenario()
    final_summary = result["final_summary"]

    assert "Risky actions blocked" in final_summary
    assert "read_repo_secret" in final_summary
    assert "send_webhook" in final_summary
    assert "blocked because" in final_summary


def test_no_real_network_or_secret_access_occurs():
    result = run_attack_scenario()
    final_summary = result["final_summary"]
    blocked_outputs = [
        event["output"] for event in result["trace_events"] if event["blocked"]
    ]

    assert blocked_outputs == [None, None]
    assert "No repository secret was exposed" in final_summary
    assert "no external webhook was called" in final_summary
    assert "sk-" not in final_summary
    assert "API_KEY" not in final_summary
    assert "TOKEN=" not in final_summary
    assert "password=" not in final_summary


def _event_for(result, tool_name):
    return next(
        event for event in result["trace_events"] if event["tool_name"] == tool_name
    )
