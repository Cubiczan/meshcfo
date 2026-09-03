# Design: MeshCFO stdio MCP

## Pattern

Match published Cubiczan MCPs: host config is `mcpServers.meshcfo` with
`command` + `args`, plus `claude mcp add meshcfo -- …`.

MeshCFO is Python and not on PyPI. The source of truth is a Python MCP that
imports `cme.cfo_os.CFOOperatingSystem`. The npm package is a spawn wrapper
only — it must fail with install instructions if `python3 -m cme.mcp` is not
importable. It does not vendor a second orchestrator.

## Tools (existing product surface)

| Tool | Existing API |
|------|----------------|
| `forecast` | `CFOOperatingSystem.run(ForecastBrief)` |
| `investment_case` | `CFOOperatingSystem.run(InvestmentBrief)` |
| `board_output` | `CFOOperatingSystem.run(BoardBrief)` |
| `lock` | `CFOOperatingSystem.lock` (third-party validation) |
| `verify_audit` | `AuditLedger.verify` (HMAC-SHA256 chain) |

JSON keys for a session match the CLI `--json` report (`task`, `decision_id`,
`lock_state`, `artifact_markdown`, `audit_entries`, …).

## Offline demo

Default Finance / Strategy / Compliance agents are deterministic and need no
API key. Ledger signing uses `AUDIT_LEDGER_KEY` or the existing test default.

## Non-goals

- Rebuilding `EnterpriseOrchestrator` / CHP.
- Inventing a new wire protocol.
- `npm publish` / `twine upload`.
- Named SEC filers or pipeline accounts in README.
