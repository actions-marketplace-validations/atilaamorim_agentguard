# 🛡️ AgentGuard

**Security and context auditor for AI agents and MCP servers.**

AgentGuard scans AI-agent configuration and project files for risky permissions, exposed secrets, prompt-injection patterns, and context bloat.

> **Audit your AI agents before they audit your code.**

## What it checks
- 🔐 Hard-coded secrets and private-key material
- ⚠️ Dangerous shell / command execution permissions
- 📁 Broad filesystem access
- 🧠 Prompt-injection patterns in agent instructions
- 📦 MCP server configurations
- 📉 Oversized agent context files
- 📊 A simple security score and actionable findings

## Quick start

```bash
git clone https://github.com/atilaamorim/agentguard.git
cd agentguard
python -m agentguard scan .
```

Or install the package:

```bash
pip install -e .
agentguard scan .
```

## Example

```text
🛡️ AgentGuard 0.1.0

Scanning: .

Security score: 71/100
Findings: 3

HIGH   AG-SEC-001  Potential secret detected
HIGH   AG-EXEC-001 Dangerous command execution capability
MED    AG-PROMPT-001 Prompt-injection pattern detected

Summary: 1 high · 1 medium · 1 low
```

## Why AgentGuard?

AI agents increasingly have access to terminals, files, credentials, MCP tools, and large instruction files. A configuration that looks harmless to a human can create a meaningful security or privacy risk.

AgentGuard is designed to make that risk visible before an agent runs.

## Roadmap
- [x] Local filesystem scanner
- [x] JSON/YAML MCP config inspection
- [x] Secret detection
- [x] Prompt-injection heuristics
- [x] Permission-risk heuristics
- [x] Security score
- [ ] HTML report
- [ ] GitHub Action annotations
- [ ] SARIF output
- [ ] Config adapters for Claude Code, Codex, Cursor, Gemini CLI and OpenCode
- [ ] MCP registry / server metadata checks
- [ ] Context-cost estimation
- [ ] Baseline mode for CI

## Contributing

AgentGuard is intentionally built to be easy to extend. New checks are small Python rules with an ID, severity, message and evidence.

Contributions are welcome.

## License

MIT
