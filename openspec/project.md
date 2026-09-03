# MeshCFO

Cubiczan product: the auditable multi-agent CFO. Finance, Strategy, and Compliance
agents collaborate on a shared context engine; every session is wrapped in CHP.

## Capabilities touched in-repo

- **cfo-os** — `CFOOperatingSystem` + `cfo-os` CLI (forecast, investment_case, board_output, lock)
- **audit-ledger** — HMAC-SHA256 append-only JSONL ledger
- **meshcfo-mcp** — stdio MCP pipe over the existing CFO OS (this change)

Do not generate specs for the whole existing codebase. Add specs as capabilities are touched.
