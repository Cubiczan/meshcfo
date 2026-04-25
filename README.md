# Multi-Agent CFO Operating System

CHP-hardened, shared-context platform where Finance, Strategy, and Compliance agents collaborate on **forecasts**, **investment cases**, and **board outputs** with a single auditable reasoning trail.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](tests/)

---

## What this is

A single CFO task — "build the FY plan", "fund the enterprise tier", "approve the board ask" — usually fragments across three failure modes:

1. **Context fragmentation** — finance, strategy, and compliance each see a different slice
2. **Reasoning opacity** — the CFO gets a conclusion without seeing how it was reached
3. **Soft consensus** — agreement looks unanimous because no one ran the assumptions through adversarial review

This system fuses two well-specified frameworks to fix all three:

| Layer | Role |
|---|---|
| **Cognitive Mesh** | Three specialist agents (Finance, Strategy, Compliance) reason on a **shared ContextEngine**. Each agent runs through the Cognitive Mesh Protocol — visible expansion/compression cycles with grounding checks and self-improving playbooks. |
| **Consensus Hardening Protocol (CHP)** | Wraps the multi-agent run in a **DecisionCase** with foundation disclosure → adversarial attack → R0 gate → lock progression. A decision can advance only when foundation passes; LOCKED requires third-party validation. |
| **CFO Operating System** | The capstone: takes a CFO **brief** (forecast / investment case / board output), runs Mesh + CHP, and produces a domain-specific artifact tied back to every claim's origin via an **AuditTrail**. |

Every line in the final artifact traces back to:
- the agent that produced it,
- the expansion step in that agent's reasoning,
- the grounding source/confidence,
- the CHP foundation findings that hardened or weakened it.

---

## Quick start

```bash
git clone https://github.com/zan-maker/multi-agent-cfo-os.git
cd multi-agent-cfo-os
pip install -e .
cfo-os cfo-os --task investment_case \
  --title "Fund enterprise tier Q3" \
  --company "Acme" \
  --problem "Should we fund a dedicated enterprise tier this quarter?" \
  --amount 4000000 \
  --payback-months 14 \
  --current-runway 18 \
  --upside "Higher ACV" --upside "Lower strategic-account churn" \
  --risk "Adoption lag" --risk "Implementation complexity"
```

Or without installing:

```bash
PYTHONPATH=src python3 -m cme.cli cfo-os --task forecast \
  --title "FY26 driver-based plan" \
  --company "Acme" \
  --problem "Build the FY26 driver-based operating plan with stress views." \
  --base-revenue 42000000 --base-opex 33000000 \
  --growth-pct 0.28 --churn-pct 0.09
```

---

## The three CFO tasks

### `--task investment_case` → InvestmentCaseMemo

Capital allocation case. The system requires `--amount`, `--payback-months`, runway floors, expected upside, and key risks. Foundation-attacks the timing assumptions; produces a memo with milestone-gated capital release and explicit flip criteria.

### `--task forecast` → ForecastPack

Driver-based operating plan. Takes baseline revenue/opex and growth/churn assumptions; lands a **Driver Registry**, **Stress Views** (downside/central/upside), and a lock state tied to the foundation score.

### `--task board_output` → BoardOutput

Board decision packet. Takes `--option` (repeatable), `--recommended-index`, `--open-question`, and strategic risks; lands a single decision statement, ranked options, dissent surface, and a replayable lock state.

---

## How a session runs

```
brief
  │
  ▼
build DecisionCase + Dossier ──► CHP foundation disclosure + attack
  │                              R0 gate + parity assessment
  ▼                              initial PAYLOAD envelope
seed shared ContextEngine
  │
  ▼
EnterpriseOrchestrator
  ├─ Finance agent     (produces budget_envelope, roi_model)
  ├─ Strategy agent    (consumes budget_envelope; produces market_positioning)
  └─ Compliance agent  (consumes both; produces risk_register, mitigations)
  │
  ▼
foundation PASS + no failure mode  ──►  status = PROVISIONAL_LOCK
  │
  ▼
synthesize CFO artifact (Forecast / Investment / Board)
  + AuditTrail linking every claim to expansion step + grounding + CHP findings
  │
  ▼
third-party validation  ──►  status = LOCKED
```

Lock progression is explicit: `EXPLORING → PROVISIONAL_LOCK → LOCKED`. The CFO can stop at any point, reopen items, or re-run with new constraints — every state transition is recorded in the registry.

---

## Architecture

```
                        ┌──────────────────────────┐
   ┌───── shared ──────▶│   ContextEngine          │◀───── shared ─────┐
   │                    │   (entities/events/tasks │                   │
   │                    │    + short/long memory)  │                   │
   │                    └──────────────────────────┘                   │
   ▼                                                                    ▼
┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐
│ Finance Agent      │     │ Strategy Agent     │     │ Compliance Agent   │
│  ├─ Playbook (ACE) │     │  ├─ Playbook (ACE) │     │  ├─ Playbook (ACE) │
│  └─ Protocol (CMP) │     │  └─ Protocol (CMP) │     │  └─ Protocol (CMP) │
└──────────┬─────────┘     └──────────┬─────────┘     └──────────┬─────────┘
           │ produces                 │ consumes+produces        │ consumes
           ▼                          ▼                          ▼
      budget_envelope        market_positioning            risk_register
      roi_model              go_to_market                  mitigations
           │                          │                          │
           └──────────────┬───────────┴──────────────┬───────────┘
                          ▼                          ▼
                 ┌──────────────────────────────────────────┐
                 │  CFOOperatingSystem                      │
                 │   1. CHP DecisionCase + Foundation       │
                 │   2. EnterpriseOrchestrator (Mesh)       │
                 │   3. Lock progression                    │
                 │   4. CFOArtifact + AuditTrail            │
                 └──────────────────────────────────────────┘
```

### Cognitive Mesh Protocol (`cme.protocol`)

Every agent turn runs through a visible breathing cycle: **Expansion** (Reframe → Constraints → Alternatives → Assumptions → Edge cases → Cross-domain analogy), then **Compression** (Integrate → Commit). Each claim is tagged `verified | inferred | pattern-match`. A `detect_hallucination_risk` heuristic flags unsourced authority phrases and bare percentages.

### Context Engine (`cme.context`)

Layered short/long-term memory + fixed-schema entity/event/task model. Context is selected by combined score (semantic relevance 50% + recency 20% + importance 20% + frequency 10%) with cosine dedup. Each agent receives a `snapshot_for(name, query)` packet — the entities, events, and notes it actually needs.

### Agentic Context Engineering (`cme.playbook`)

Each agent owns a **playbook**, not a prompt. Six sections (`strategies_and_hard_rules`, `verification_checklist`, `troubleshooting_and_pitfalls`, …). Updates are **delta-only** (`ADD`, `INCREMENT`, `MERGE`, `PRUNE`) — full regeneration is impossible by design. After every turn, a Reflector turns the trajectory into insights and a Curator turns insights into deltas.

### Consensus Hardening Protocol (`cme.chp`)

Decision governance layer. Every CFO session is a `DecisionCase` with:
- `Dossier` (core problem, goal state, current state, constraints, scope, structural vulnerabilities)
- `FoundationDisclosure` (1–3 weakest assumptions, 1–2 invalidation conditions, key vulnerability)
- `FoundationAttack` (assumption attacks, invalidation exploitation, vulnerability strike, foundation_score 0–100)
- `R0 gate` (solvable / scoped / valid / worth_it)
- `RoundRecord`s with `BEGIN_PAYLOAD`/`END_PAYLOAD` envelopes for cross-model exchange
- `ThirdPartyValidation` log to advance `PROVISIONAL_LOCK → LOCKED`

### CFO Operating System (`cme.cfo_os`)

The capstone:
- `briefs.py` — `ForecastBrief`, `InvestmentBrief`, `BoardBrief`
- `dossier_builders.py` — brief → CHP `DecisionCase + FoundationDisclosure + FoundationAttack`
- `artifacts.py` — `ForecastPack`, `InvestmentCaseMemo`, `BoardOutput`
- `audit.py` — fuses Mesh reasoning + CHP foundation findings into a single `AuditTrail`
- `orchestrator.py` — `CFOOperatingSystem.run(brief)` returns a `CFOSessionReport` that renders to a board-ready markdown document

---

## CLI reference

```bash
cfo-os cfo-os                  # Run a CFO OS session
  --task {forecast,investment_case,board_output}
  --title TITLE
  --company COMPANY
  --problem PROBLEM
  --priority X --constraint Y               # repeatable

  # forecast-only:
  --base-revenue --base-opex --growth-pct --churn-pct

  # investment-only:
  --amount --payback-months --upside --risk

  # board-only:
  --option --recommended-index --open-question --prior-decision

  --out-md PATH                 # Also write the markdown report
  --json                        # Emit structured JSON

cfo-os demo [PROBLEM]           # Base mesh orchestration on a problem
cfo-os playbook {finance,strategy,compliance}   # Show seeded playbook
cfo-os context                  # Dump seeded org context

cfo-os chp-start                # Start a raw CHP capital allocation session
cfo-os chp-receive              # Attach a partner packet
cfo-os chp-validate             # Apply third-party validation (LOCKED)
```

---

## Programmatic use

```python
from cme.cfo_os import CFOOperatingSystem, InvestmentBrief
from demo import FinanceAgent, StrategyAgent, ComplianceAgent

cfo = CFOOperatingSystem(agents=[FinanceAgent(), StrategyAgent(), ComplianceAgent()])

report = cfo.run(InvestmentBrief(
    title="Fund enterprise tier",
    company="Acme",
    problem="Should we fund a dedicated enterprise tier this quarter?",
    investment_amount_usd=2_500_000,
    expected_payback_months=14,
    current_runway_months=18,
    expected_upside=["Higher ACV"],
    key_risks=["Adoption lag"],
))

print(report.case.status.value)        # PROVISIONAL_LOCK
print(report.artifact.render())        # board-ready memo
print(report.audit.render())           # per-claim provenance

# Advance to LOCKED via third-party validation
cfo.lock(report.case.decision_id,
    validator="fresh_instance",
    item="Investment spec v1",
    rationale="Spec coheres; flip criteria explicit.",
)
```

---

## Tests

```bash
pip install pytest
PYTHONPATH=src pytest tests/ -v
```

The CFO OS test suite covers all three task types, lock progression, audit-trail provenance, and end-to-end mesh+CHP integration.

---

## License

MIT. See [LICENSE](LICENSE).
