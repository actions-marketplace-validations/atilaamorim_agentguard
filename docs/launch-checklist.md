# AgentConfigGuard release checklist

## Current target release

- Distribution: `agentconfigguard`
- CLI: `agentguard`
- Target version: `0.2.1`
- Previous release: `0.2.0`
- GitHub repository: `atilaamorim/agentguard`

## Pre-release

- [x] PyPI Trusted Publisher is configured for this repository, workflow, and `pypi` environment.
- [x] Version is aligned across project metadata and citation metadata.
- [x] MCP provenance rule has positive and negative regression coverage.
- [x] Demo command has human-readable and JSON regression coverage.
- [x] GitHub Actions tests pass on Python 3.9-3.13 for the current feature work.
- [x] Package build workflow passes.
- [x] Security audit workflow passes.
- [ ] Create the `v0.2.1` GitHub release after the final CI checks are green.
- [ ] Verify `agentconfigguard 0.2.1` on PyPI after publication.

## Release

Create the `v0.2.1` tag only after the final pre-release checks are green. The release workflow builds the distributions, verifies the tag matches the project version, and publishes to PyPI through Trusted Publishing.

After publication, verify:

```bash
python -m pip install --upgrade agentconfigguard
agentguard --version
agentguard demo
agentguard scan .
```

## GitHub Action

After `v0.2.1` exists, recommend pinning downstream users to `v0.2.1`.

## Public launch

Use the same positioning everywhere:

> Static security and policy audit for AI-agent and MCP configuration, designed for CI.

Lead with the built-in demo, a reproducible risky/safe benchmark, and the fact that the scanner is local and read-only.

Do not ask users to manufacture stars or manipulate GitHub metrics. The goal is genuine adoption, contributors, and downstream dependents.
