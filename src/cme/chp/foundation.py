"""Foundation-stage helpers for CHP."""
from __future__ import annotations

from cme.chp.models import FoundationAttack, FoundationDisclosure, Verdict
from cme.rust_core import run_meshcfo_core


def foundation_verdict(attack: FoundationAttack) -> Verdict:
    payload = run_meshcfo_core("foundation_verdict", {"foundation_score": attack.foundation_score})
    return Verdict(payload["value"])


def validate_foundation_pair(
    disclosure: FoundationDisclosure, attack: FoundationAttack
) -> list[str]:
    payload = run_meshcfo_core(
        "validate_foundation_pair",
        {"disclosure": disclosure.__dict__, "attack": attack.__dict__},
    )
    return list(payload["value"])
