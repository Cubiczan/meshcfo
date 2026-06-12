# Ghost Integration — Multi-Agent CFO Operating System

This document describes how [Ghost](https://ghost.build) — the Postgres database built for AI agents — can serve as the persistence and experimentation layer for your CFO OS.

---

## Overview

Ghost provides unlimited Postgres databases you can create, fork, and discard freely. For the CFO OS, this means:

- **Persistent state** — replace in-memory dataclasses + SpacetimeDB with real Postgres
- **Forkable experiments** — clone an entire CFO session to test different assumptions
- **MCP tool access** — agents can create/fork/query databases during orchestration

**Key Ghost commands:**
```bash
brew install timescale/tap/ghost       # Install
ghost init                               # Configure (login, MCP, completions)
ghost create cfo-session-2026-q3         # Create a DB per session
ghost fork cfo-session-2026-q3 experiment-high-growth  # Fork to test scenarios
ghost sql cfo-session-2026-q3 "SELECT * FROM decision_cases"  # Query
ghost mcp start                          # MCP server for agent tools
```

---

## Integration Points

### 1. Replace SpacetimeDB with Ghost Postgres

The SpacetimeDB module (`spacetime/spacetimedb/src/lib.rs`) defines 6 tables: `Brief`, `AgentTurnRecord`, `SharedContextEntity`, `DecisionCase`, `AuditEntry`, `FinalArtifact`. These map directly to Ghost Postgres tables.

**Schema setup:**
```bash
ghost create cfo-os-prod
ghost sql cfo-os-prod < src/schema/setup.sql
```

```sql
-- src/schema/setup.sql
CREATE TABLE briefs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brief_type TEXT NOT NULL,              -- 'forecast', 'investment', 'board'
    company TEXT,
    parameters JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE decision_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID,
    status TEXT DEFAULT 'EXPLORING',       -- CHP state machine
    dossier JSONB,
    foundation JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE agent_turns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID,
    agent_name TEXT,
    turn_number INT,
    expansion TEXT,
    synthesis JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE audit_trail (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID,
    agent_name TEXT,
    claim TEXT,
    provenance JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE final_artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID,
    artifact_type TEXT,
    content JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

### 2. Fork-Based Scenario Testing

The killer Ghost feature for CFO OS: **fork the database to test scenarios.**

```bash
# Production session
ghost create cfo-q3-2026
ghost sql cfo-q3-2026 --seed initial_data.sql

# Fork for "what if" scenarios
ghost fork cfo-q3-2026 cfo-q3-high-growth
ghost fork cfo-q3-2026 cfo-q3-cost-cutting
ghost fork cfo-q3-2026 cfo-q3-acquisition

# Run the CFO OS against each fork independently
cfo-os --db cfo-q3-high-growth   --scenario "revenue +30%"
cfo-os --db cfo-q3-cost-cutting   --scenario "opex -15%"
cfo-os --db cfo-q3-acquisition    --scenario "acquire for $50M"

# Compare results
ghost sql cfo-q3-high-growth  "SELECT * FROM final_artifacts"
ghost sql cfo-q3-cost-cutting "SELECT * FROM final_artifacts"

# Keep the winner, delete the rest
ghost delete cfo-q3-high-growth
ghost delete cfo-q3-cost-cutting
```

### 3. MCP Integration for Agent Database Access

Install the Ghost MCP server so your agents can manage databases directly:

```bash
ghost mcp install claude-code   # or cursor, codex, windsurf
```

Once installed, the CFO OS agents have these MCP tools available:
- `ghost_create` — spin up a DB for a new CFO session
- `ghost_fork` — clone an existing session for scenario testing
- `ghost_sql` — run queries against any database
- `ghost_schema` — inspect the table structure
- `ghost_share` — share a session with a colleague
- `ghost_delete` — clean up after done

**Example agent prompt via MCP:**
> Create a new Ghost database for Q3 2026. Seed it with the CFO schema. Then fork it into three scenarios: high growth, cost cutting, and acquisition. I'll run the CFO OS against each fork.

### 4. CLI Integration

Add a `--ghost` flag to the existing CLI:

```python
# In src/cme/cli.py — Ghost integration
def add_ghost_args(parser):
    parser.add_argument("--ghost-db", help="Ghost database name or ID")
    parser.add_argument("--ghost-create", action="store_true",
                       help="Create a new Ghost DB for this session")
    parser.add_argument("--ghost-fork", help="Fork an existing Ghost DB")
```

### 5. ContextEngine Persistence

The `ContextEngine` (`src/cme/context.py`) stores entities, events, and tasks in-memory. A Ghost backend would:

```python
# Ghost-backed ContextEngine
class GhostContextEngine(ContextEngine):
    def __init__(self, ghost_db: str):
        self.db = ghost_db
        
    async def upsert_entity(self, entity_id, kind, properties):
        ghost_sql(self.db, """
            INSERT INTO context_entities (id, kind, properties)
            VALUES ($1, $2, $3)
            ON CONFLICT (id) DO UPDATE SET properties = $3
        """, [entity_id, kind, json.dumps(properties)])
```

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│                    Ghost Postgres                       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────────┐│
│  │  briefs  │ │decision_│ │agent_   │ │final_        ││
│  │          │ │cases    │ │turns    │ │artifacts     ││
│  └─────────┘ └─────────┘ └─────────┘ └──────────────┘│
│                                                        │
│  Ghost MCP Server (ghost mcp start)                    │
│  Tools: create / fork / sql / schema / share / delete │
└──────────────────────┬─────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────┐
│              Multi-Agent CFO OS                        │
│  CLI  →  CFOOperatingSystem  →  agents  →  CHP  →  audit│
│                  ▲                         ▲            │
│          Ghost-backed                Ghost-backed       │
│          ContextEngine               CHP Registry       │
└────────────────────────────────────────────────────────┘
```

---

## Getting Started

1. **Install Ghost:**
   ```bash
   brew install timescale/tap/ghost
   ghost init
   ```
2. **Create a database:**
   ```bash
   ghost create cfo-os-dev
   ```
3. **Run schema:**
   ```bash
   ghost sql cfo-os-dev < src/schema/setup.sql
   ```
4. **Install the MCP server:**
   ```bash
   ghost mcp install claude-code
   ```
5. **Run the CFO OS with Ghost backend:**
   ```bash
   cfo-os --ghost-db cfo-os-dev --problem "Optimize working capital"
   ```

---

## Resources
- [Ghost Documentation](https://ghost.build/docs)
- [Ghost MCP Tools](https://ghost.build/docs/#mcp-integration)
- [Ghost API Reference](https://ghost.build/docs/#api-reference)
- [Ghost Tutorial](https://ghost.build/tutorials/learn-the-basics)
