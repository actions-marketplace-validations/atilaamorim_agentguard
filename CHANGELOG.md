# Changelog

All notable changes to AgentGuard are documented here.

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
- package-build and installation smoke tests.

The project remains heuristic and should be used as an additional security signal, not a sole security control.
