# 🛡️ AgentGuard

![Tests](https://github.com/atilaamorim/agentguard/actions/workflows/test.yml/badge.svg) [![PyPI](https://img.shields.io/pypi/v/agentconfigguard.svg)](https://pypi.org/project/agentconfigguard/) [![PyPI downloads](https://img.shields.io/pypi/dm/agentconfigguard.svg)](https://pypi.org/project/agentconfigguard/) ![License](https://img.shields.io/github/license/atilaamorim/agentguard)

**Security and context auditor for AI agents and MCP servers.**

> **Audit your AI agents before they audit your code.**

AgentGuard is an open-source CLI that scans agent instructions, MCP configuration, and project text for common security risks and produces machine-readable reports for CI.

**Static and local by design:** the scanner analyzes files without connecting to agents or invoking MCP tools during the audit.

## What it checks

| Rule | What it looks for | Severity |
| --- | --- | --- |
| `AG-SEC-001` | API keys, tokens, passwords and private-key material | High |
| `AG-EXEC-001` | Shell, terminal and command-execution capabilities | High |
| `AG-FS-001` | Broad filesystem/workspace access in config | High |
| `AG-MCP-001` | MCP servers configured with `trust=true` | High |
| `AG-MCP-002` | MCP servers using unencrypted `http://` endpoints | Medium |
| `AG-MCP-003` | Remote MCP servers without declared provenance metadata | Low |
| `AG-POLICY-001` | Dangerous combination of untrusted input, private data access and outbound actions | Critical |
| `AG-GEMINI-001` | Gemini CLI persistent approval default | Medium |
| `AG-CODEX-001` | Codex full-access approval combination | High |
| `AG-PROMPT-001` | Common prompt-injection instruction patterns | Medium |
| `AG-CONTEXT-001` | Oversized agent instruction files | Low |
| `AG-CONTEXT-002` | Agent context above a configured token budget | Medium |

The scanner also understands common agent instruction files such as `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `CODEX.md`, and `CURSOR.md`.

## Quick start

Install the latest public release from PyPI:

```bash
python -m pip install agentconfigguard
agentguard --version
agentguard scan .
```

The PyPI distribution is named `agentconfigguard`; the CLI command remains `agentguard`.

For development or unreleased code:

```bash
git clone https://github.com/atilaamorim/agentguard.git
cd agentguard
python -m pip install -e .
agentguard scan .
```

For a development install directly from GitHub:

```bash
python -m pip install git+https://github.com/atilaamorim/agentguard.git
agentguard --version
```

You can also run:

```bash
python -m agentguard scan .
```

### JSON output

```bash
agentguard scan . --json
```

### SARIF output

SARIF works well with GitHub code-scanning workflows:

```bash
agentguard scan . --sarif agentguard-results.sarif
```

### HTML report

```bash
agentguard scan . --html agentguard-report.html
```

### MCP security checks

AgentGuard parses common `mcpServers` / MCP server configuration structures and checks for high-signal hazards:

- `trust: true` — flags configurations that can bypass normal tool-call confirmation.
- `url: http://...` (and equivalent endpoint keys) — flags unencrypted remote MCP transport.
- Capability-chain analysis — flags a server that combines untrusted input, private-data access, and outbound actions.

HTTPS endpoints are not flagged by the HTTP transport check. Remote MCP servers without declared provenance metadata also receive a low-severity transparency warning.

### Ecosystem detection

See which AI-agent ecosystems are present in a project:

```bash
agentguard scan . --adapters
```

AgentGuard currently recognizes Claude, Codex, Cursor, Gemini, OpenCode, and MCP configuration markers.

### Context cost estimate

See which agent instruction files consume the most context:

```bash
agentguard scan . --context
```

Token counts are estimates based on character length, not provider-specific billing.

### Context budget gate

Enforce a project-level context budget in CI:

```bash
agentguard scan . --max-context-tokens 12000
```

AgentGuard reports `AG-CONTEXT-002` when a supported instruction file exceeds the configured budget. Token counts are estimates based on character length, not provider-specific billing.

### Pre-commit

Run AgentGuard before each commit:

```yaml
repos:
  - repo: https://github.com/atilaamorim/agentguard
    rev: main
    hooks:
      - id: agentguard
```

The hook blocks commits on `high` and `critical` findings by default.

### Policy as code

Add `.agentguard.yml` to the project root to keep CI policy with the repository:

```yaml
version: 1
fail_on_severity: high
max_context_tokens: 12000
ignore:
  - rule: AG-MCP-002
    paths:
      - "configs/local/*"
```

The file is discovered automatically. Use `--policy PATH` to select another file or `--no-policy` to disable automatic discovery.

CLI flags take precedence over policy values.

### CI severity threshold

Keep lower-severity findings visible without failing the build:

```bash
agentguard scan . --fail-on-severity high
```

With this setting, `high` and `critical` findings fail CI while `medium` and `low` findings remain visible in reports.

The reusable GitHub Action exposes the same control:

```yaml
      - uses: atilaamorim/agentguard@v0.1.0
        with:
          fail-on-severity: "high"
```

### GitHub Actions annotations

When running in GitHub Actions, emit inline warnings and errors for findings:

```bash
agentguard scan . --github-annotations
```

The reusable GitHub Action enables annotations by default. Disable them when desired:

```yaml
      - uses: atilaamorim/agentguard@v0.1.0
        with:
          github-annotations: "false"
```

### Baseline mode

For existing projects, create a baseline and then fail CI only when new findings appear:

```bash
agentguard scan . --write-baseline agentguard-baseline.json
agentguard scan . --baseline agentguard-baseline.json
```

Baseline matching uses the rule, file path, and detected evidence. Review the baseline periodically as the project changes.

## GitHub Action

Use AgentGuard directly in another repository:

```yaml
name: AgentGuard

on:
  push:
  pull_request:

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: atilaamorim/agentguard@v0.1.0
        with:
          path: .
```

You can also enforce the context budget through the action:

```yaml
      - uses: atilaamorim/agentguard@v0.1.0
        with:
          max-context-tokens: "12000"
          fail-on-findings: "true"
```

The action automatically discovers `.agentguard.yml` in the target repository. To select a different policy file:

```yaml
      - uses: atilaamorim/agentguard@v0.1.0
        with:
          policy: "config/agentguard.yml"
```


To make findings fail the job:

```yaml
      - uses: atilaamorim/agentguard@v0.1.0
        with:
          fail-on-findings: "true"
```

## Example

```text
🛡️ AgentGuard 0.1.0

Scanning: .

Security score: 71/100
Findings: 3

HIGH     AG-SEC-001      Potential secret detected — .env:4
HIGH     AG-EXEC-001     Potential command execution capability — AGENTS.md:12
MEDIUM   AG-PROMPT-001   Prompt-injection pattern detected — CLAUDE.md:8
```

A non-clean scan exits with status code `1`, which makes AgentGuard suitable for CI gates.

## Architecture

See [docs/architecture.md](docs/architecture.md) for the scanner flow, safety boundaries, and extension model.

## Threat model

See [docs/threat-model.md](docs/threat-model.md) for scope, limitations, and false-positive guidance.

## Rule reference

See [docs/rules.md](docs/rules.md) for the current rule catalog, severity, rationale, and remediation guidance.

## Security regression benchmark

AgentGuard ships with small, deterministic MCP fixtures under `tests/fixtures/`.

Run the full regression suite with:

```bash
pytest -q
```

The benchmark intentionally includes both dangerous and safe configurations. The goal is not only to detect risky capability combinations, but also to protect against future false positives as new rules are added.

## Why AgentGuard?

AI agents increasingly receive access to terminals, files, credentials, MCP tools, and large instruction files. A configuration that looks harmless to a human can create meaningful security or privacy risk.

AgentGuard aims to make that risk visible **before an agent runs**.

## Project status

AgentGuard is an early public MVP. Detection is heuristic and can produce false positives or miss sophisticated attacks. It is an auditing aid, not a guarantee that an agent, MCP server, repository, or deployment is secure.

## Roadmap

- [x] Local filesystem scanner
- [x] JSON/YAML MCP config inspection
- [x] Secret detection
- [x] Prompt-injection heuristics
- [x] Permission-risk heuristics
- [x] MCP trust-bypass detection
- [x] MCP insecure-HTTP detection
- [x] Dangerous capability-chain detection
- [x] Gemini CLI persistent approval detection
- [x] Codex full-access approval detection
- [x] Security score
- [x] JSON output
- [x] SARIF output
- [x] Reusable GitHub Action
- [x] Context bloat detection
- [x] GitHub Action annotations
- [x] Ecosystem detection for Claude Code, Codex, Cursor, Gemini CLI and OpenCode
- [x] Sanitized provider configuration fixtures for supported ecosystems
- [x] MCP registry / server metadata checks (provenance metadata on main; next release will package this)
- [x] Context-cost estimation
- [x] Configurable context-token CI gate
- [x] HTML report
- [x] Baseline mode for CI
- [x] Versioned policy-as-code configuration
- [x] PyPI package publication as `agentconfigguard`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

Security issues should follow [SECURITY.md](SECURITY.md).

## License

MIT
