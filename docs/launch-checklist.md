# AgentConfigGuard release checklist

## Current release

- Distribution: `agentconfigguard`
- CLI: `agentguard`
- Current published release: `0.2.1`
- GitHub repository: `atilaamorim/agentguard`

## Verified for 0.2.1

- [x] PyPI Trusted Publisher is configured for this repository, workflow, and `pypi` environment.
- [x] Version is aligned across project metadata and citation metadata.
- [x] MCP provenance rule has positive and negative regression coverage.
- [x] Demo command has human-readable and JSON regression coverage.
- [x] GitHub Actions tests pass on Python 3.9-3.13 for the release changes.
- [x] Package build workflow passes.
- [x] Security audit workflow passes.
- [x] `v0.2.1` GitHub release is published.
- [x] `agentconfigguard 0.2.1` is published on PyPI.
- [x] Installed package smoke test passes.
- [x] `agentguard demo` runs without network access or file writes.

## Next release

Before the next release:

- [ ] Update the project version consistently.
- [ ] Add or update regression coverage for every behavior change.
- [ ] Run tests, package build, and security audit to completion.
- [ ] Review the README and changelog for stale examples.
- [ ] Create the next version tag only after final CI checks are green.
- [ ] Verify the corresponding PyPI version after publication.

## Public launch

Use the same positioning everywhere:

> Static security and policy audit for AI-agent and MCP configuration, designed for CI.

Lead with the built-in demo, a reproducible risky/safe benchmark, and the fact that the scanner is local and read-only.

Do not ask users to manufacture stars or manipulate GitHub metrics. The goal is genuine adoption, contributors, and downstream dependents.
