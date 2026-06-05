# Multi-Agent CFO Operating System

Multi-agent collaboration platform that automates CFO-grade financial decision-making through a Cognitive Mesh of specialist agents hardened by a Consensus Hardening Protocol -- producing forecasts, investment cases, and board outputs with a single auditable reasoning trail.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](tests/)

---

## Overview

A single CFO task -- "build the FY plan", "fund the enterprise tier", "approve the board ask" -- usually fragments across three failure modes: context fragmentation across departments, reasoning opacity in the final output, and soft consensus that looks unanimous because assumptions were never adversarially reviewed.

Multi-Agent CFO OS solves all three by fusing two well-specified frameworks into one system. The **Cognitive Mesh** layer coordinates three specialist agents (Finance, Strategy, and Compliance) that reason on a shared context engine with visible expansion/compression reasoning cycles and self-improving playbooks. The **Consensus Hardening Protocol (CHP)** wraps every session in decision governance with foundation disclosure, adversarial assumption attacks, R0 gate checks, and explicit lock progression from EXPLORING through PROVISIONAL_LOCK to LOCKED.

Every line in the final CFO artifact traces back to the agent that produced it, the expansion step in that agent's reasoning, the grounding source and confidence level, and the CHP foundation findings that hardened or weakened the claim. The result is a board-ready markdown document with complete provenance -- suitable for audit committees, board presentations, and regulatory compliance.

## Architecture

```
                       ┌──────────────────────────────┐
  ┌───── shared ──────>│        ContextEngine          |<───── shared ─────┐
  │                     │  (entities / events / tasks   │                    │
  │                     │   + short / long memory)       │                    │
  │                     └──────────────────────────────┘                    │
  v                                                                       v
┌────────────────────┐    ┌────────────────────┐    ┌────────────────────────┐
│ Finance Agent       │    │ Strategy Agent     │    │ Compliance Agent      │
│  ├─ Playbook (ACE)  │    │  ├─ Playbook (ACE) │    │  ├─ Playbook (ACE)   │
│  └─ Protocol (CMP)  │    │  └─ Protocol (CMP) │    │  └─ Protocol (CMP)   │
└──────────┬─────────┘    └──────────┬─────────┘    └──────────┬───────────┘
           │ produces               │ consumes+produces          │ consumes
           v                        v                            v
      budget_envelope          market_positioning           risk_register
      roi_model                go_to_market                 mitigations
           │                        │                            │
           └──────────────┬─────────┴──────────────┬─────────────┘
                          v                        v
                 ┌──────────────────────────────────────────┐
                 │           CFOOperatingSystem              │
                 │   1. CHP DecisionCase + Foundation         │
                 │   2. EnterpriseOrchestrator (Mesh)        │
                 │   3. Lock progression (EXPLORING > LOCK)  │
                 │   4. CFOArtifact + AuditTrail             │
                 └──────────────────────────────────────────┘
```

### Session Flow

```
brief
  |
  v
build DecisionCase + Dossier --> CHP foundation disclosure + attack
  |                              R0 gate + parity assessment
  v                              initial PAYLOAD envelope
seed shared ContextEngine
  |
  v
EnterpriseOrchestrator
  +-- Finance agent     (produces budget_envelope, roi_model)
  +-- Strategy agent    (consumes budget_envelope; produces market_positioning)
  +-- Compliance agent  (consumes both; produces risk_register, mitigations)
  |
  v
foundation PASS + no failure mode  -->  status = PROVISIONAL_LOCK
  |
  v
synthesize CFO artifact (Forecast / Investment / Board)
  + AuditTrail linking every claim to expansion step + grounding + CHP findings
  |
  v
third-party validation  -->  status = LOCKED
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Data Modeling | dataclasses (stdlib) |
| Context Engine | Custom entity/event/task graph with cosine dedup |
| Agent Protocol | Cognitive Mesh Protocol (expansion/compression cycles) |
| Decision Governance | Consensus Hardening Protocol (CHP) |
| Database | CockroachDB (via SQLAlchemy) |
| CLI | argparse (stdlib), entry point `cfo-os` |
| Testing | pytest 8.0+ |

## Key Features

- **Three Specialist Agents** -- Finance, Strategy, and Compliance agents collaborate on a shared ContextEngine with topological sequencing so producers run before consumers. Each agent implements the full Cognitive Mesh Protocol with visible expand/compress reasoning cycles.

- **Cognitive Mesh Protocol** -- Every agent turn runs through a visible breathing cycle: Expansion (Reframe, Constraints, Alternatives, Assumptions, Edge cases, Cross-domain analogy), then Compression (Integrate, Commit). Each claim is tagged as verified, inferred, or pattern-match.

- **Self-Improving Playbooks** -- Each agent owns a playbook (not just a prompt) with six sections. Updates are delta-only (ADD, INCREMENT, MERGE, PRUNE). After every turn, a Reflector turns the trajectory into insights and a Curator turns insights into targeted playbook amendments.

- **Consensus Hardening Protocol** -- Decision governance layer wrapping every CFO session: Dossier, FoundationDisclosure (weakest assumptions, invalidation conditions), FoundationAttack (assumption attacks, vulnerability strikes, foundation_score 0-100), R0 gate (solvable/scoped/valid/worth_it), and multi-round payload envelopes for cross-model exchange.

- **Explicit Lock Progression** -- Decisions advance through EXPLORING, PROVISIONAL_LOCK, and LOCKED states. PROVISIONAL_LOCK requires foundation pass and no agent failure modes. LOCKED requires third-party validation confirmation.

- **Audit Trail** -- Every claim in the final artifact traces back to the producing agent, expansion step, grounding source/confidence, and CHP foundation findings that hardened or weakened it.

- **Three CFO Task Types** -- Forecast (driver-based operating plans with stress views), Investment Case (capital allocation memos with milestone-gated release), and Board Output (decision packets with ranked options and dissent surface).

- **Context Engine** -- Layered short/long-term memory with fixed-schema entity/event/task model. Context is selected by combined score (semantic relevance 50%, recency 20%, importance 20%, frequency 10%) with cosine deduplication.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/zan-maker/multi-agent-cfo-os.git
cd multi-agent-cfo-os

# Install in editable mode
pip install -e .
```

### Quick Start

Run a full CFO OS investment case session from the command line:

```bash
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

Run a forecast session without installing:

```bash
PYTHONPATH=src python3 -m cme.cli cfo-os --task forecast \
  --title "FY26 driver-based plan" \
  --company "Acme" \
  --problem "Build the FY26 driver-based operating plan with stress views." \
  --base-revenue 42000000 --base-opex 33000000 \
  --growth-pct 0.28 --churn-pct 0.09
```

## Usage

### CLI Commands

```bash
# Run a full CFO OS session (forecast, investment_case, or board_output)
cfo-os cfo-os \
  --task {forecast,investment_case,board_output} \
  --title TITLE \
  --company COMPANY \
  --problem PROBLEM \
  --priority X --constraint Y \
  [--out-md PATH] [--json]

# Base mesh orchestration on a problem
cfo-os demo [PROBLEM]

# Show a seeded agent playbook
cfo-os playbook {finance,strategy,compliance}

# Dump the seeded organizational context
cfo-os context

# Start a raw CHP capital allocation session
cfo-os chp-start \
  --title TITLE --company COMPANY --problem PROBLEM \
  --amount AMOUNT --payback-months MONTHS \
  --current-runway MONTHS

# Attach a partner packet to an existing CHP decision
cfo-os chp-receive \
  --decision-id ID --packet-file FILE \
  --phase {0,1,2} --round N

# Apply third-party validation to advance to LOCKED
cfo-os chp-validate \
  --decision-id ID \
  --validator NAME --item ITEM \
  --challenge "Stress test" \
  --result {CONFIRM,REJECT} \
  --rationale "Explanation..."
```

### Programmatic API

```python
from cme.cfo_os import CFOOperatingSystem, InvestmentBrief
from demo import FinanceAgent, StrategyAgent, ComplianceAgent

cfo = CFOOperatingSystem(
    agents=[FinanceAgent(), StrategyAgent(), ComplianceAgent()]
)

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
cfo.lock(
    report.case.decision_id,
    validator="fresh_instance",
    item="Investment spec v1",
    rationale="Spec coheres; flip criteria explicit.",
)
```

### Running Tests

```bash
pip install pytest
PYTHONPATH=src pytest tests/ -v
```

## Project Structure

```
Multi-agent-CFO-OS/
├── pyproject.toml              # Package config (entry point: cfo-os)
├── requirements.txt            # Runtime dependencies
├── LICENSE                     # MIT license
├── examples/
│   └── cfo_os_examples.sh      # Example CLI invocations
├── src/
│   ├── cme/
│   │   ├── __init__.py
│   │   ├── cli.py              # CLI entry point (all subcommands)
│   │   ├── agent.py            # MeshAgent base class + TurnResult
│   │   ├── protocol.py         # Cognitive Mesh Protocol (expand/compress)
│   │   ├── context.py          # ContextEngine (entity/event/task graph)
│   │   ├── playbook.py         # Playbook + Reflector + Curator (ACE)
│   │   ├── bridge.py           # BridgeFramework (Statement + Workflow)
│   │   ├── orchestrator.py     # EnterpriseOrchestrator (topological sequencing)
│   │   ├── chp/
│   │   │   ├── models.py       # DecisionCase, Phase, Verdict, SessionStatus
│   │   │   ├── foundation.py   # Foundation disclosure/attack/verdict
│   │   │   ├── gates.py        # R0 gate evaluation
│   │   │   ├── parity.py       # Model parity assessment
│   │   │   ├── payloads.py     # Payload envelope (BEGIN/END)
│   │   │   ├── rounds.py       # RoundRecord management
│   │   │   ├── registry.py     # DecisionRegistry (JSON persistence)
│   │   │   ├── validators.py   # Third-party validation
│   │   │   ├── dossier.py      # Dossier builder
│   │   │   ├── devil.py        # Adversarial devil's advocate
│   │   │   └── orchestrator.py # CHPOrchestrator (session lifecycle)
│   │   ├── cfo_os/
│   │   │   ├── briefs.py       # ForecastBrief, InvestmentBrief, BoardBrief
│   │   │   ├── dossier_builders.py  # Brief -> CHP DecisionCase
│   │   │   ├── artifacts.py    # ForecastPack, InvestmentCaseMemo, BoardOutput
│   │   │   ├── audit.py        # AuditTrail (per-claim provenance)
│   │   │   └── orchestrator.py # CFOOperatingSystem (capstone orchestrator)
│   │   ├── finance/
│   │   │   └── capital_allocation.py  # Capital allocation case builder
│   │   └── db/
│   │       └── cockroachdb_layer.py   # CockroachDB persistence
│   └── demo/
│       ├── finance_agent.py    # Finance agent implementation
│       ├── strategy_agent.py   # Strategy agent implementation
│       └── compliance_agent.py # Compliance agent implementation
└── tests/
    ├── test_chp_basics.py
    ├── test_chp_capital_flow.py
    ├── test_chp_registry_cli_flow.py
    ├── test_cfo_os.py
    └── test_mesh.py
```

## Contributing

Contributions are welcome. To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes and add tests where applicable
4. Run the test suite to ensure all tests pass (`PYTHONPATH=src pytest tests/ -v`)
5. Commit your changes with descriptive messages
6. Open a Pull Request against the `main` branch

Please ensure all new code includes appropriate test coverage and follows the existing code style.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for the full text.
