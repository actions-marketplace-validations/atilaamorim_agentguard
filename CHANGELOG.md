# Changelog

All notable changes to AgentGuard are documented here.

## Unreleased

- hardened bounded file scanning so inaccessible files do not abort directory audits;
- added regression coverage for inaccessible files and rule metadata completeness.



## 0.2.1

- added the built-in `agentguard demo` command for a deterministic local product demonstration;
- added JSON output for the demo command;
- added regression coverage for the demo path;
- aligned README and release metadata with the 0.2.1 public release.

## 0.2.0

- added MCP remote-server provenance metadata check (`AG-MCP-003`);
- added positive and negative regression coverage for provenance metadata;
- added sanitized fixture coverage for remote MCP provenance;
- updated README, rule reference, and release documentation for the public 0.2.0 workflow.

## 0.1.0

Initial public MVP with:

- static security scanning for AI-agent instructions and MCP configuration;
- secret, command, filesystem, prompt-injection, context, and MCP policy checks;
- structured MCP trust and cleartext HTTP detection;
- dangerous capability-chain detection;
- Gemini CLI persistent approval detection;
- JSON, SARIF, and HTML reports with remediation guidance;
- baselines and configurable severity thresholds;
- versioned YAML policy-as-code;
- reusable GitHub Action;
- deterministic risky/safe regression fixtures;
- package-build and installation smoke tests;
- `agentconfigguard` distribution metadata with the `agentguard` CLI preserved;
- provider-specific policy checks for Gemini CLI and Codex.

The project remains heuristic and should be used as an additional security signal, not a sole security control.
