# Airbyte Agents Integration — Multi-Agent CFO OS

This document describes how [Airbyte Agents](https://docs.airbyte.com/ai-agents) can connect your Multi-Agent CFO OS to live financial data sources — CRM, ERP, billing, and analytics platforms — replacing hardcoded assumptions with real-time business data.

---

## Overview

Airbyte Agents is a data and context layer for AI agents. It gives your agents real-time access to business data through open-source, type-safe connectors, managed credentials, and low-latency search.

**Integration options:**
- **[MCP interface](https://docs.airbyte.com/ai-agents/interfaces/mcp)** — Remote Model Context Protocol server. No install. Connect Claude, ChatGPT, Cursor, or any MCP-compatible client to live business data.
- **[Python SDK](https://docs.airbyte.com/ai-agents/interfaces/sdk)** — `airbyte_agent_sdk` library for typed connector access within Python agent code.
- **[REST API](https://docs.airbyte.com/ai-agents/interfaces/sdk)** — HTTP interface for non-Python backends.

---

## Integration Points

### 1. CFO Brief Input via Airbyte MCP

The `CFOBrief` classes (`src/cme/cfo_os/briefs.py`) define the input schemas for `ForecastBrief`, `InvestmentBrief`, and `BoardBrief`. These fields are currently populated from CLI arguments.

**MCP Setup:**
```json
// Add to your MCP client config (Claude Desktop, Codex, Cursor, etc.)
{
  "mcpServers": {
    "airbyte": {
      "url": "https://mcp.airbyte.ai/mcp"
    }
  }
}
```

**Example prompt for Claude:**
> Using the Airbyte MCP, connect my Salesforce account and Stripe account. Then query my open deals > $50K and my MRR. Populate a CFO Brief with these values.

### 2. ContextEngine Data Hydration via SDK

The `ContextEngine` (`src/cme/context.py`) stores entities, events, and tasks. Airbyte connectors can hydrate these with live data.

```python
# src/cme/data/airbyte_connector.py — Example integration
from airbyte_agent_sdk import connect

async def hydrate_context(engine, workspace_id: str):
    """Pull live financial data via Airbyte SDK and seed the ContextEngine."""
    # Connect to Stripe for revenue data
    stripe = connect("stripe")
    invoices = await stripe.execute("invoices", "list", params={"limit": 100})
    
    # Write revenue metrics as context entities
    total_revenue = sum(inv["amount_paid"] for inv in invoices.data)
    engine.upsert_entity(
        entity_id="live_arr",
        kind="metric",
        properties={"value": total_revenue, "source": "stripe", "currency": "usd"},
    )
    
    # Connect to Salesforce for pipeline data
    sf = connect("salesforce")
    deals = await sf.execute("opportunities", "search", params={"stage": "Proposal"})
    engine.upsert_entity(
        entity_id="pipeline_weighted",
        kind="metric",
        properties={"value": sum(d["amount"] for d in deals.data), "source": "salesforce"},
    )
    await stripe.close()
    await sf.close()
```

### 3. Playbook Bullets from External Knowledge

Playbooks (`src/cme/playbook.py`) contain strategies, rules, and domain concepts that can be seeded from Airbyte-synced data.

**Recommended connectors:**
| Data Source | Connector | Playbook Use |
|-------------|-----------|-------------|
| Financial standards | Google Sheets / Notion | GAAP/IFRS rules, reporting templates |
| Policy docs | Google Drive | Internal finance policies, approval thresholds |
| Market benchmarks | FRED / Yahoo Finance | Interest rates, inflation, sector multiples |

### 4. CHP Decision Cases from CRM/ERP

`DecisionCase.dossier` fields (`constraints`, `scope`, `current_state`, `goal_state`) can be populated from live CRM or ERP data via the MCP.

### 5. SpacetimeDB as Airbyte Destination

Once CFO outputs are in SpacetimeDB's `AuditEntry`, `FinalArtifact`, and `Brief` tables, Airbyte can sync them to a data warehouse (Snowflake, BigQuery, Redshift) for compliance dashboards.

---

## Getting Started

1. **Sign up** at [app.airbyte.ai](https://app.airbyte.ai) (free tier available).
2. **Add the MCP server** to your client:
   ```
   URL: https://mcp.airbyte.ai/mcp
   ```
3. **Connect data sources** via the MCP credential flow (handled in-browser).
4. **Query live data** with natural language:
   > "Get my current Stripe MRR and Salesforce pipeline, then run the CFO OS with these as inputs."

Or for programmatic access:
```bash
pip install airbyte-agent-sdk
```

---

## Connector Catalog

Airbyte Agents supports 30+ connectors including:

| Category | Services |
|----------|----------|
| **CRM** | Salesforce, HubSpot, Zendesk Sell |
| **Billing** | Stripe, Recurly, Chargebee |
| **Support** | Zendesk, Intercom, Freshdesk |
| **Productivity** | Notion, Google Drive, Google Sheets |
| **Analytics** | Mixpanel, Amplitude, Google Analytics |
| **Data Warehouse** | Snowflake, BigQuery, Postgres, Redshift |
| **Communications** | Slack, Gong, Outreach |

See the full catalog at [docs.airbyte.com/ai-agents/connectors](https://docs.airbyte.com/ai-agents/connectors).
