# Change: Add a stdio MCP server for MeshCFO

## Why

Cursor and Claude Code should call MeshCFO without cloning the repo and
pip-installing by hand each session. Published Cubiczan MCPs (`@cubiczan/chp-mcp`,
`@cubiczan/agent-conductor`, `@cubiczan/codesentinel-mcp`) already follow
"CHP is the lock; MCP is the pipe." MeshCFO needs the same pipe.

## What Changes

- Python stdio MCP server using the official MCP SDK that **imports**
  `CFOOperatingSystem` and the existing CLI briefs / lock / ledger — no new
  orchestrator, no new protocol.
- Tools: `forecast`, `investment_case`, `board_output`, `lock`, `verify_audit`.
- Packaging: `pip install -e ".[mcp]"` entry point `meshcfo-mcp` / `python -m cme.mcp`.
- Thin npm wrapper `@cubiczan/meshcfo-mcp` that honestly `exec`s that Python server.
- Tests: `tools/list` plus one happy-path forecast or investment case against the
  real library (offline demo agents, no invented credentials).
- README install JSON for Cursor and a `claude mcp add` one-liner.

## Impact

- New optional extra `mcp` (official `mcp` SDK).
- New `src/cme/mcp/` package and `tests/test_mcp.py`.
- Root `package.json` + `bin/meshcfo-mcp.js` prepared for later npm publish
  (do not publish from this environment).
- README gains an MCP section. Brand remains **Cubiczan**.
