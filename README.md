# 🛡️ AgentGuard

**Security and context auditor for AI agents and MCP servers.**

> **Audit your AI agents before they audit your code.**

AgentGuard is an open-source CLI that scans agent instructions, MCP configuration, and project text for common security risks and produces machine-readable reports for CI.

## What it checks

| Rule | What it looks for | Severity |
| --- | --- | --- |
| `AG-SEC-001` | API keys, tokens, passwords and private-key material | High |
| `AG-EXEC-001` | Shell, terminal and command-execution capabilities | High |
| `AG-FS-001` | Broad filesystem/workspace access in config | High |
| `AG-MCP-001` | MCP servers configured with `trust=true` | High |
| `AG-MCP-002` | MCP servers using unencrypted `http://` endpoints | Medium |
| `AG-POLICY-001` | Dangerous combination of untrusted input, private data access and outbound actions | Critical |
| `AG-PROMPT-001` | Common prompt-injection instruction patterns | Medium |
| `AG-CONTEXT-001` | Oversized agent instruction files | Low |
| `AG-CONTEXT-002` | Agent context above a configured token budget | Medium |

The scanner also understands common agent instruction files such as `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `CODEX.md`, and `CURSOR.md`.

## Quick start

```bash
git clone https://github.com/atilaamorim/agentguard.git
cd agentguard
python -m pip install -e .
agentguard scan .
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

HTTPS endpoints are not flagged by the HTTP transport check.

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

### GitHub Actions annotations

When running in GitHub Actions, emit inline warnings and errors for findings:

```bash
agentguard scan . --github-annotations
```

The reusable GitHub Action enables annotations by default. Disable them when desired:

```yaml
      - uses: atilaamorim/agentguard@main
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
      - uses: actions/checkout@v4
      - uses: atilaamorim/agentguard@main
        with:
          path: .
```

You can also enforce the context budget through the action:

```yaml
      - uses: atilaamorim/agentguard@main
        with:
          max-context-tokens: "12000"
          fail-on-findings: "true"
```

To make findings fail the job:

```yaml
      - uses: atilaamorim/agentguard@main
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

## Why AgentGuard?

AI agents increasingly receive access to terminals, files, credentials, MCP tools, and large instruction files. A configuration that looks harmless to a human can create meaningful security or privacy risk.

AgentGuard aims to make that risk visible **before an agent runs**.

## Project status

AgentGuard is an early MVP. Detection is heuristic and can produce false positives or miss sophisticated attacks. It is an auditing aid, not a guarantee that an agent, MCP server, repository, or deployment is secure.

## Roadmap

- [x] Local filesystem scanner
- [x] JSON/YAML MCP config inspection
- [x] Secret detection
- [x] Prompt-injection heuristics
- [x] Permission-risk heuristics
- [x] MCP trust-bypass detection
- [x] MCP insecure-HTTP detection
- [x] Dangerous capability-chain detection
- [x] Security score
- [x] JSON output
- [x] SARIF output
- [x] Reusable GitHub Action
- [x] Context bloat detection
- [x] GitHub Action annotations
- [x] Ecosystem detection for Claude Code, Codex, Cursor, Gemini CLI and OpenCode
- [ ] MCP registry / server metadata checks
- [x] Context-cost estimation
- [x] Configurable context-token CI gate
- [x] HTML report
- [x] Baseline mode for CI
- [ ] Package releases for easy installation

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

Security issues should follow [SECURITY.md](SECURITY.md).

## License

MIT
