"""Policy engine tests for the Agent Runtime Policy Demo."""

from policy import (
    ALLOW_SAFE_READ,
    ALLOW_SAFE_SUMMARY,
    BLOCK_EXTERNAL_WEBHOOK,
    BLOCK_SECRET_ACCESS,
    BLOCK_SECRET_LIKE_PAYLOAD,
    evaluate_policy,
)


def test_allows_read_github_issue():
    decision = evaluate_policy("read_github_issue", {"issue_id": "123"})

    assert decision.allowed is True
    assert decision.decision == "allow"
    assert decision.reason
    assert decision.rule_id == ALLOW_SAFE_READ


def test_allows_summarize_issue():
    decision = evaluate_policy("summarize_issue", {"body": "A safe issue body."})

    assert decision.allowed is True
    assert decision.decision == "allow"
    assert decision.reason
    assert decision.rule_id == ALLOW_SAFE_SUMMARY


def test_blocks_repo_secret_access():
    decision = evaluate_policy("read_repo_secret", {"name": "DEPLOY_KEY"})

    assert decision.allowed is False
    assert decision.decision == "block"
    assert decision.reason
    assert decision.rule_id == BLOCK_SECRET_ACCESS


def test_blocks_send_webhook():
    decision = evaluate_policy("send_webhook", {"url": "https://example.test/hook"})

    assert decision.allowed is False
    assert decision.decision == "block"
    assert decision.reason
    assert decision.rule_id == BLOCK_EXTERNAL_WEBHOOK


def test_blocks_secret_like_api_key_payload():
    decision = evaluate_policy("summarize_issue", {"body": "API_KEY=demo-value"})

    assert decision.allowed is False
    assert decision.decision == "block"
    assert decision.reason
    assert decision.rule_id == BLOCK_SECRET_LIKE_PAYLOAD


def test_blocks_secret_like_token_payload():
    decision = evaluate_policy("summarize_issue", {"body": "TOKEN=demo-value"})

    assert decision.allowed is False
    assert decision.decision == "block"
    assert decision.reason
    assert decision.rule_id == BLOCK_SECRET_LIKE_PAYLOAD


def test_blocks_secret_like_sk_payload():
    decision = evaluate_policy("summarize_issue", {"body": "sk-demo-fake-key"})

    assert decision.allowed is False
    assert decision.decision == "block"
    assert decision.reason
    assert decision.rule_id == BLOCK_SECRET_LIKE_PAYLOAD


def test_blocks_secret_like_password_payload():
    decision = evaluate_policy("summarize_issue", {"body": "password=demo-value"})

    assert decision.allowed is False
    assert decision.decision == "block"
    assert decision.reason
    assert decision.rule_id == BLOCK_SECRET_LIKE_PAYLOAD


def test_returns_clear_reason_for_blocked_call():
    decision = evaluate_policy("send_webhook", {"url": "https://example.test/hook"})

    assert decision.allowed is False
    assert decision.decision == "block"
    assert isinstance(decision.reason, str)
    assert len(decision.reason.strip()) > 10
    assert "webhook" in decision.reason.lower()


def test_policy_decision_has_stable_rule_id():
    decision = evaluate_policy("read_repo_secret", {"name": "SECRET"})

    assert decision.allowed is False
    assert decision.decision == "block"
    assert decision.reason
    assert decision.rule_id == BLOCK_SECRET_ACCESS
