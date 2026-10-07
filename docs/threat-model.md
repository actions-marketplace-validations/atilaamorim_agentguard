# AgentGuard threat model

AgentGuard is a **static configuration auditor**. It reads project files and produces findings; it does not connect to an agent, invoke an MCP tool, or execute the configured agent commands during a scan.

## In scope

AgentGuard is designed to surface configuration-level risks such as:

- credentials embedded in tracked files;
- command-execution capabilities;
- broad filesystem/workspace access;
- MCP trust/confirmation bypass;
- cleartext remote MCP endpoints;
- dangerous combinations of untrusted input, private data access, and outbound actions;
- prompt-injection patterns in instruction files;
- oversized agent context.

## Out of scope

A clean result does not prove that an agent or MCP server is safe. The scanner does not attempt to:

- execute tools or commands;
- connect to remote MCP servers;
- prove that a server is trustworthy;
- understand the full runtime authorization model of a provider;
- detect every prompt-injection or tool-poisoning technique;
- replace code review, dependency review, secret scanning, or runtime monitoring.

## False positives and false negatives

Rules are intentionally heuristic. A legitimate configuration may trigger a finding, and a sophisticated attack may evade detection.

For this reason, AgentGuard should be used as an additional CI security signal rather than as a sole security control.

## Design goal

The project favors **high-signal findings and explainable remediation** over opaque risk scores. New rules should document their rationale and add both positive and negative regression fixtures when practical.
