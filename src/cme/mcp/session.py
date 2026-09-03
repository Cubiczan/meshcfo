"""In-process MeshCFO session used by the MCP tools.

Mirrors ``cme.cli._cmd_cfo_os`` / ``cfo.lock`` / ``AuditLedger.verify`` so the
MCP pipe does not invent a protocol or rebuild the orchestrator.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

from cme.audit import AuditLedger, default_ledger_path
from cme.cfo_os import (
    BoardBrief,
    CFOOperatingSystem,
    ForecastBrief,
    InvestmentBrief,
)
from cme.chp.registry import DecisionRegistry
from cme.context import ContextEngine

REGISTRY_ENV = "MESHCFO_REGISTRY"
LEDGER_ENV = "MESHCFO_LEDGER"
COMPANY_ENV = "MESHCFO_COMPANY"


def _default_agents():
    from demo import ComplianceAgent, FinanceAgent, StrategyAgent

    return [FinanceAgent(), StrategyAgent(), ComplianceAgent()]


class MeshCFOService:
    """Shared registry + ledger; fresh CFO OS per task (same as the CLI)."""

    def __init__(
        self,
        *,
        registry_path: Path | str | None = None,
        ledger_path: Path | str | None = None,
        company_name: str = "Acme",
    ) -> None:
        self.registry_path = Path(registry_path) if registry_path else Path(".chp_registry.json")
        self.ledger_path = Path(ledger_path) if ledger_path else default_ledger_path()
        self.company_name = company_name
        self.registry = DecisionRegistry.load(self.registry_path)
        self.ledger = AuditLedger(self.ledger_path)

    @classmethod
    def from_env(cls) -> "MeshCFOService":
        return cls(
            registry_path=os.environ.get(REGISTRY_ENV),
            ledger_path=os.environ.get(LEDGER_ENV),
            company_name=os.environ.get(COMPANY_ENV, "Acme"),
        )

    def _cfo(self) -> CFOOperatingSystem:
        return CFOOperatingSystem(
            agents=_default_agents(),
            registry=self.registry,
            context=ContextEngine(),
            company_name=self.company_name,
            ledger=self.ledger,
        )

    def _save(self) -> None:
        self.registry.save(self.registry_path)

    def run_forecast(
        self,
        *,
        title: str,
        problem: str,
        company: str = "",
        owner: str = "cfo",
        origin_model: str = "GPT-5.4",
        partner_model: str = "GPT-5-equivalent",
        partner_system: str = "Partner",
        strategic_priorities: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        base_revenue_usd: float = 0.0,
        base_opex_usd: float = 0.0,
        growth_assumption_pct: float = 0.20,
        churn_assumption_pct: float = 0.08,
        minimum_runway_months: int = 12,
        current_runway_months: int = 18,
    ) -> dict:
        brief = ForecastBrief(
            title=title,
            company=company or self.company_name,
            problem=problem,
            owner=owner,
            origin_model=origin_model,
            partner_model=partner_model,
            partner_system=partner_system,
            strategic_priorities=strategic_priorities or [],
            constraints=constraints or [],
            base_revenue_usd=base_revenue_usd,
            base_opex_usd=base_opex_usd,
            growth_assumption_pct=growth_assumption_pct,
            churn_assumption_pct=churn_assumption_pct,
            minimum_runway_months=minimum_runway_months,
            current_runway_months=current_runway_months,
        )
        report = self._cfo().run(brief)
        self._save()
        return report.to_dict()

    def run_investment_case(
        self,
        *,
        title: str,
        problem: str,
        company: str = "",
        owner: str = "cfo",
        origin_model: str = "GPT-5.4",
        partner_model: str = "GPT-5-equivalent",
        partner_system: str = "Partner",
        strategic_priorities: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        investment_amount_usd: float = 0.0,
        expected_payback_months: int = 18,
        minimum_runway_months: int = 12,
        current_runway_months: int = 18,
        expected_upside: Optional[List[str]] = None,
        key_risks: Optional[List[str]] = None,
    ) -> dict:
        brief = InvestmentBrief(
            title=title,
            company=company or self.company_name,
            problem=problem,
            owner=owner,
            origin_model=origin_model,
            partner_model=partner_model,
            partner_system=partner_system,
            strategic_priorities=strategic_priorities or [],
            constraints=constraints or [],
            investment_amount_usd=investment_amount_usd,
            expected_payback_months=expected_payback_months,
            minimum_runway_months=minimum_runway_months,
            current_runway_months=current_runway_months,
            expected_upside=expected_upside or [],
            key_risks=key_risks or [],
        )
        report = self._cfo().run(brief)
        self._save()
        return report.to_dict()

    def run_board_output(
        self,
        *,
        title: str,
        problem: str,
        company: str = "",
        owner: str = "cfo",
        origin_model: str = "GPT-5.4",
        partner_model: str = "GPT-5-equivalent",
        partner_system: str = "Partner",
        strategic_priorities: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        options: Optional[List[str]] = None,
        recommended_option_index: int = 0,
        open_questions: Optional[List[str]] = None,
        prior_board_decisions: Optional[List[str]] = None,
        strategic_risks: Optional[List[str]] = None,
    ) -> dict:
        brief = BoardBrief(
            title=title,
            company=company or self.company_name,
            problem=problem,
            owner=owner,
            origin_model=origin_model,
            partner_model=partner_model,
            partner_system=partner_system,
            strategic_priorities=strategic_priorities or [],
            constraints=constraints or [],
            options=options or [],
            recommended_option_index=recommended_option_index,
            open_questions=open_questions or [],
            prior_board_decisions=prior_board_decisions or [],
            strategic_risks=strategic_risks or [],
        )
        report = self._cfo().run(brief)
        self._save()
        return report.to_dict()

    def lock(
        self,
        decision_id: str,
        *,
        validator: str,
        item: str,
        rationale: str,
        challenge: str = "Stress test before lock progression.",
        confirm: bool = True,
    ) -> dict:
        case = self._cfo().lock(
            decision_id,
            validator=validator,
            item=item,
            rationale=rationale,
            challenge=challenge,
            confirm=confirm,
        )
        self._save()
        return {
            "decision_id": case.decision_id,
            "lock_state": case.status.value,
            "locked_decisions": list(case.locked_decisions),
            "third_party_log": [v.to_dict() for v in case.third_party_log],
            "case": case.to_dict(),
        }

    def verify_audit(self, path: Optional[str] = None) -> dict:
        target = Path(path) if path else self.ledger_path
        ledger = AuditLedger(target)
        intact, first_tampered_index = ledger.verify()
        records = ledger.read_records(target)
        return {
            "intact": intact,
            "first_tampered_index": first_tampered_index,
            "path": str(target),
            "record_count": len(records),
        }
