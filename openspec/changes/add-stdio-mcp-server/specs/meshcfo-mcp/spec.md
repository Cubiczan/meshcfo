# meshcfo-mcp Specification

## Purpose

Expose MeshCFO to MCP hosts over stdio without inventing a new CFO protocol.

## Requirements

### Tool catalog

- The server SHALL advertise exactly these tools: `forecast`, `investment_case`,
  `board_output`, `lock`, `verify_audit`.
- Each CFO task tool SHALL call `CFOOperatingSystem.run` with the matching
  existing brief type (`ForecastBrief`, `InvestmentBrief`, `BoardBrief`).
- `lock` SHALL call `CFOOperatingSystem.lock` (third-party validation) and
  persist the CHP registry.
- `verify_audit` SHALL call `AuditLedger.verify` on the HMAC-SHA256 append-only
  ledger and return whether the chain is intact.

### Transport and packaging

- The server SHALL speak MCP over stdio via the official Python MCP SDK.
- `python -m cme.mcp` and the `meshcfo-mcp` console script SHALL start that server.
- The npm package `@cubiczan/meshcfo-mcp` SHALL spawn the Python server when the
  `cme` package is importable, and SHALL exit with an install hint otherwise.

### Demo mode

- Default demo agents SHALL run without an API key.
- The server SHALL NOT invent or embed credentials.

### Brand

- Public docs SHALL spell the brand **Cubiczan**.
- Public docs SHALL NOT name SEC filers or pipeline accounts.
