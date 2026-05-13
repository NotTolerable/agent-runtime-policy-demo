# AGENTS.md — Agent Runtime Policy Demo

## 1. Project goal

Build a small, readable proof-of-work demo showing how an AI DevOps assistant with tool access can be pushed into risky behavior by indirect prompt injection, and how a runtime trace/policy layer can detect and block risky tool calls before execution.

The core story is:

1. A mock DevOps assistant reads a mock GitHub issue.
2. The issue contains hidden or indirect prompt injection telling the assistant to access repository secrets and send them to an external webhook.
3. The scripted or lightly simulated assistant attempts the risky tool calls.
4. A policy layer evaluates every attempted tool call before execution.
5. Safe calls are allowed and logged.
6. Risky calls are blocked and logged.
7. A JSON-style trace shows each attempted tool call, policy decision, reason, output when allowed, and blocked status when blocked.

This project is a demo for outreach to an AI agent security/governance startup. Prioritize clarity, demonstrability, and testability over sophistication.

## 2. Product/demo scope

Implement only the minimal demo needed to communicate runtime policy enforcement for agent tool calls.

Required demo behavior:

- The agent reads a mock GitHub issue.
- The issue contains indirect prompt injection.
- The agent attempts risky tool calls because of the injected instruction.
- The policy layer evaluates each tool call before execution.
- Safe tool calls are allowed and logged.
- Risky tool calls are blocked and logged.
- The trace shows every attempted tool call, policy decision, and reason.

Keep the agent scripted or lightly simulated. Do not build a general-purpose autonomous agent framework.

## 3. Tech stack

Use:

- Python
- Streamlit
- pytest
- Python `dataclasses` or pydantic for structured data models
- JSON-style trace logs

Do not add unnecessary dependencies. Prefer standard-library Python where practical.

## 4. Folder structure

The intended project structure is:

```text
agent-runtime-policy-demo/
  app.py
  agent.py
  policy.py
  tools.py
  traces.py
  models.py
  sample_attack.md
  tests/
    test_policy.py
    test_agent_scenario.py
    test_traces.py
  README.md
  requirements.txt
```

Do not create implementation files unless the current task explicitly asks for them. For this instruction-file task, create only `AGENTS.md`.

## 5. Coding style rules

- Prefer simple, readable Python over clever abstractions.
- Keep functions small and explicit.
- Use clear names such as `PolicyDecision`, `TraceEvent`, `ToolCall`, and `MockDevOpsAgent` when those concepts are implemented.
- Use dataclasses or pydantic consistently for structured models; do not mix both without a clear reason.
- Avoid hidden global state for policy decisions and traces.
- Core logic must be importable and testable without launching Streamlit.
- Never put try/except blocks around imports.
- Avoid network calls, real credentials, and external services.
- Keep demo data deterministic so tests are stable.

## 6. Testing rules

- Tests must be written before or alongside the core logic.
- Use pytest for tests.
- `pytest` should cover:
  - policy allow/block decisions;
  - trace event creation;
  - the full prompt-injection attack scenario;
  - confirmation that blocked tools do not execute.
- Do not rely on Streamlit UI tests for core correctness.
- Core logic must be testable without launching the Streamlit app.
- Tests must not call real GitHub, real webhook URLs, Slack, email, databases, or any external service.
- Use deterministic mock values only.

## 7. Policy engine rules

The policy layer must evaluate every attempted tool call before the tool executes.

Required policy behavior:

- Allow `read_github_issue`.
- Allow `summarize_issue`.
- Block `read_repo_secret`.
- Block `send_webhook`.
- Block tool calls whose tool name, arguments, or payload contain secret-like values or markers, including:
  - `API_KEY`
  - `SECRET`
  - `TOKEN`
  - `sk-`
  - `password`
- Block external data transfer attempts.
- Return a clear allow/block decision and a human-readable reason for every attempted tool call.

Policy code should be intentionally understandable. Do not implement a full policy language or complex authorization system unless explicitly requested.

## 8. Trace logging rules

Every attempted tool call must create a trace event, regardless of whether the call is allowed or blocked.

Each trace event must include:

- step number;
- tool name;
- arguments;
- policy decision;
- reason;
- output if allowed;
- blocked flag if blocked.

Trace logs should be JSON-style objects or structures that can be displayed in Streamlit and asserted in pytest. Preserve the sequence of attempted calls so the demo clearly shows the attack path and the policy intervention point.

## 9. Mock tool rules

Required mock tools:

- `read_github_issue`
- `summarize_issue`
- `read_repo_secret`
- `send_webhook`

Tool behavior rules:

- `read_github_issue` should return deterministic mock issue content from local data, such as `sample_attack.md`.
- `summarize_issue` should summarize or simulate summarizing the issue without using an external model.
- `read_repo_secret` must never access real secrets; if implemented, it may return a fake deterministic value only in tests that prove policy protection, but normal policy flow should block it before execution.
- `send_webhook` must never make a real outbound request; if implemented, it should be a no-op or fake function used only to prove that policy blocking prevents execution.
- Mock tools must not use real GitHub APIs, real Slack/email/database integrations, or real webhook calls.

## 10. Streamlit UI rules

The Streamlit UI should be a thin presentation layer over testable core logic.

When implemented, the UI should show:

- the mock GitHub issue content;
- the scripted assistant steps;
- attempted tool calls;
- policy decisions;
- blocked calls and reasons;
- the JSON-style trace log.

Do not put core policy, trace, or agent behavior only inside Streamlit callbacks. Do not require the Streamlit UI for pytest coverage.

## 11. Security assumptions

- This is a local educational demo, not a production security system.
- Do not claim production-grade security, complete prompt-injection prevention, or comprehensive data-loss prevention.
- The policy layer demonstrates runtime detection and blocking of selected risky tool calls.
- No real secrets should exist in the repository or be read from the environment.
- No real outbound network exfiltration should occur.
- The sample attack should be clearly fake and safe to run locally.

## 12. Features not to build

Do not build:

- a full agent framework;
- real GitHub API integration;
- real secret access;
- real outbound webhook calls;
- real Slack, email, or database integrations;
- authentication;
- a database;
- deployment infrastructure;
- complex policy languages;
- complex tracing backends;
- OpenAI API integration as a core requirement;
- features that require an OpenAI API key for the core demo.

## 13. Official documentation references

When implementation details are unclear, prefer these official references over guessing. Use them to inform the demo design, but do not add full framework complexity unless the current task explicitly asks for it.

- Python dataclasses: https://docs.python.org/3/library/dataclasses.html
- pytest getting started: https://docs.pytest.org/en/stable/getting-started.html
- Streamlit getting started: https://docs.streamlit.io/get-started
- OWASP LLM01 Prompt Injection: https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- OpenAI Agents SDK Guardrails: https://openai.github.io/openai-agents-python/guardrails/
- Model Context Protocol Security Best Practices: https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices

## 14. Verification commands

Use these commands when applicable:

```bash
python -m pytest
streamlit run app.py
```

For instruction-only changes, verify the file exists and review its contents. Do not run app commands before the app exists.

## 15. README expectations

The README should explain:

- what the demo shows;
- why agent tool access creates risk;
- how the policy layer works;
- how trace logging works;
- what is mocked;
- how to run the project;
- how to run tests;
- what would be improved with more time.

Keep the README honest: this is a small local demo of runtime policy enforcement, not production security software.
