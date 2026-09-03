"""Session gate logic for CHP."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from cme.chp.models import SessionStatus, Verdict
from cme.rust_core import run_meshcfo_core


@dataclass(frozen=True)
class GateEvaluation:
    results: Dict[str, str]
    verdict: Verdict


def evaluate_r0_gate(*, solvable: bool, scoped: bool, valid: bool, worth_it: bool) -> GateEvaluation:
    payload = run_meshcfo_core(
        "evaluate_r0_gate",
        {"solvable": solvable, "scoped": scoped, "valid": valid, "worth_it": worth_it},
    )
    value = payload["value"]
    return GateEvaluation(results=dict(value["results"]), verdict=Verdict(value["verdict"]))


def evaluate_phase_gate(round_number: int, phase_one_status: SessionStatus) -> Verdict:
    payload = run_meshcfo_core(
        "evaluate_phase_gate",
        {"round_number": round_number, "phase_one_status": phase_one_status.value},
    )
    return Verdict(payload["value"])
