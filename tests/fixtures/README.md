# AgentGuard security fixtures

These fixtures are intentionally small regression cases for the MCP policy engine.

## risky-mcp.json

Expected findings:

- `AG-MCP-001`: trusted MCP execution can bypass confirmation.
- `AG-MCP-002`: cleartext HTTP transport.
- `AG-POLICY-001`: untrusted input + private data + outbound action.

## safe-mcp.json

This fixture represents a low-risk baseline:

- HTTPS is used for the remote endpoint.
- Explicit trust bypass is disabled.
- The server descriptions do not declare the dangerous capability chain.

The fixtures are not intended to model every provider's exact configuration schema. They are stable regression inputs for AgentGuard's policy engine.
