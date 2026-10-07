# AgentGuard architecture

AgentGuard is intentionally a local, read-only static auditor.

## Flow

```text
repository
   |
   +--> discover agent ecosystems
   |
   +--> read bounded text/config files
   |
   +--> structured MCP/provider analysis
   |
   +--> heuristic rule engine
   |
   +--> policy filtering
   |
   +--> baseline filtering
   |
   +--> score + findings
   |
   +--> CLI / JSON / SARIF / HTML
   |
   +--> CI exit status + GitHub annotations
```

## Safety boundaries

AgentGuard does not execute commands found in repository files and does not connect to configured MCP endpoints during a scan. This keeps the audit deterministic and reduces the risk that the auditor itself crosses the trust boundary it is evaluating.

## Rule layers

### Text heuristics

Simple line-based rules catch credential-like values and prompt-injection patterns in supported text files.

### Structured configuration

JSON/YAML configuration is parsed as data. MCP server structures are inspected for explicit properties such as trust settings and remote endpoints.

Provider-specific checks are scoped to recognizable configuration paths so generic documentation does not accidentally trigger them.

### Policy combinations

Some risks emerge from combinations of capabilities rather than from one setting. The policy engine can therefore reason about combinations such as untrusted input, private-data access, and outbound actions.

## Outputs

- Human-readable terminal output for local development.
- JSON for automation and custom tooling.
- SARIF for GitHub code-scanning workflows.
- HTML for shareable audit reports.

## Extending AgentGuard

New rules should add:

1. Stable rule metadata and remediation guidance.
2. A positive regression case.
3. A safe/negative regression case when practical.
4. Documentation in `docs/rules.md`.

The benchmark under `tests/fixtures/` is deliberately deterministic so rule changes can be reviewed without network access or LLM calls.
