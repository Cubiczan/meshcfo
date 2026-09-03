"""Capital-allocation domain adapter for CHP sessions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from cme.chp.models import DecisionCase, Dossier, FoundationAttack, FoundationDisclosure
from cme.rust_core import run_meshcfo_core, score_foundation


@dataclass
class CapitalAllocationInput:
    title: str
    company: str
    proposal_summary: str
    investment_amount_usd: float
    expected_payback_months: int
    minimum_runway_months: int
    current_runway_months: int
    strategic_priorities: List[str]
    key_risks: List[str]
    expected_upside: List[str]
    owner: str = "cfo"
    origin_system: str = "Claude"
    origin_model: str = "GPT-5.4"
    partner_system: str = "Partner"
    partner_model: str = "GPT-5-equivalent"
    decision_id: str | None = None
    high_stakes: bool = True


def build_capital_allocation_case(
    payload: CapitalAllocationInput,
) -> tuple[DecisionCase, FoundationDisclosure, FoundationAttack]:
    payload_dict = {
        "title": payload.title,
        "company": payload.company,
        "proposal_summary": payload.proposal_summary,
        "investment_amount_usd": payload.investment_amount_usd,
        "expected_payback_months": payload.expected_payback_months,
        "minimum_runway_months": payload.minimum_runway_months,
        "current_runway_months": payload.current_runway_months,
        "strategic_priorities": payload.strategic_priorities,
        "key_risks": payload.key_risks,
        "expected_upside": payload.expected_upside,
        "owner": payload.owner,
        "origin_system": payload.origin_system,
        "origin_model": payload.origin_model,
        "partner_system": payload.partner_system,
        "partner_model": payload.partner_model,
        "decision_id": payload.decision_id,
        "high_stakes": payload.high_stakes,
    }
    response = run_meshcfo_core("build_capital_allocation_case", {"payload": payload_dict})
    value = response["value"]
    case = DecisionCase.from_dict(value["case"])
    disclosure = FoundationDisclosure(**value["disclosure"])
    attack = FoundationAttack(**value["attack"])
    return case, disclosure, attack


def _decision_id(title: str) -> str:
    seed = "".join(ch.lower() if ch.isalnum() else "-" for ch in title).strip("-")
    return f"cap-{seed[:32]}"


def _foundation_score(payload: CapitalAllocationInput) -> int:
    return score_foundation(
        {
            "kind": "capital_allocation",
            "current_runway_months": payload.current_runway_months,
            "minimum_runway_months": payload.minimum_runway_months,
            "expected_payback_months": payload.expected_payback_months,
            "key_risks_count": len(payload.key_risks),
            "investment_amount_usd": payload.investment_amount_usd,
        }
    )
