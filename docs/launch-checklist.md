# AgentConfigGuard release checklist

## Current release

- Distribution: `agentpolicyshield`
- CLI: `agentguard`
- Target version: `0.1.0`
- GitHub repository: `atilaamorim/agentguard`

## Pre-release

- [x] Python package builds successfully in CI.
- [x] Installed CLI smoke test passes.
- [x] Tests pass on Python 3.9-3.13.
- [x] Security audit passes.
- [x] Package metadata contains project URLs and classifiers.
- [x] Release workflow uses PyPI Trusted Publishing/OIDC.
- [ ] Verify `agentpolicyshield` is available for first registration on PyPI immediately before release.
- [ ] Configure the PyPI Trusted Publisher for this GitHub repository, workflow, and `pypi` environment.

## First release

Create the `v0.1.0` tag only after the PyPI Trusted Publisher is configured. The release workflow then builds and publishes the distribution.

After publication, verify:

```bash
python -m pip install agentpolicyshield
agentguard --version
agentguard scan .
```

## GitHub Action

After `v0.1.0` exists, recommend pinning downstream users to the release tag instead of `main`:

```yaml
- uses: atilaamorim/agentguard@v0.1.0
```

## Public launch

Use the same positioning everywhere:

> Static security and policy audit for AI-agent and MCP configuration, designed for CI.

Lead with a reproducible example, the risky/safe benchmark, and the fact that the scanner is local and read-only.

Do not ask users to manufacture stars or manipulate GitHub metrics. The goal is genuine adoption, contributors, and downstream dependents.
