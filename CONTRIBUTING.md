# Contributing to AgentGuard

Thanks for helping make AI-agent and MCP security tooling better.

## Development

1. Fork the repository.
2. Create a focused branch.
3. Install the project with `pip install -e .`.
4. Run `pytest -q`.
5. Add tests for new detection rules or behavior.
6. Open a pull request explaining the security problem or use case.

## Detection rules

Rules live in `agentguard/rules.py`. Prefer:
- a stable rule ID;
- a clear severity;
- a concise user-facing message;
- a focused pattern;
- a regression test.

False positives matter. A rule should be conservative enough to be useful in real projects.

## Scope

AgentGuard is an auditing aid, not a guarantee that an agent, MCP server, repository, or deployment is secure.
