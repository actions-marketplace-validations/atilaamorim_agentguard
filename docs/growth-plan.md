# Growth and impact plan

AgentGuard is optimized for durable open-source adoption, not artificial GitHub metrics.

## Primary objective

Turn the project into a small, trusted CI primitive for auditing AI-agent and MCP configuration before execution.

## Evidence that matters

Track these signals publicly over time:

- PyPI monthly downloads
- Dependent repositories and packages
- Unique external contributors with merged PRs
- Merged pull requests by the maintainer into other projects
- OpenSSF criticality when the project has enough ecosystem usage
- GitHub stars as a secondary discovery signal

These metrics align with the current Claude for Open Source eligibility routes, but no metric should be manufactured.

## Release sequence

### v0.1.0

- Publish agentconfigguard
- Keep the agentguard CLI stable
- Verify wheel installation and CLI behavior after publication
- Pin downstream GitHub Action users to v0.1.0
- Collect the first real issue reports and pull requests

### v0.2.x

Prioritize features that increase adoption and trust:

- More high-signal provider-specific configuration checks
- MCP registry/server metadata checks
- Larger sanitized regression corpus
- Better false-positive controls
- Clear migration and suppression guidance

### Community milestone

Target 20+ distinct external contributors with merged pull requests over a 12-month window.

The preferred mechanism is a contributor funnel based on real maintenance work: reproducible bug reports, new safe/risky fixtures, provider adapters, documentation fixes, and focused rule improvements.

## Distribution milestone

After PyPI publication, measure real package usage before setting a target. A long-term objective is to approach the current maintainer/library threshold of 200,000 combined monthly downloads, 100 dependent packages, or 500 dependent repositories.

Do not optimize for downloads alone. The stronger signal is repeated usage in real repositories.

## Public launch principle

Every launch message should lead with the same distinction:

> Static security and policy audit for AI-agent and MCP configuration, designed for CI.

AgentGuard is local and read-only during scanning. It does not connect to configured MCP servers or execute repository commands during an audit.

## What not to do

- Never buy or exchange stars.
- Never create fake accounts or automated star activity.
- Never fabricate downloads, dependencies, contributors, or benchmark results.
- Never submit fabricated security findings to gain attention.

The goal is for the repository to become useful enough that the ecosystem creates the evidence organically.