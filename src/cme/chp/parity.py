"""Model parity assessment for CHP sessions."""
from __future__ import annotations

from cme.chp.models import ModelParityCheck, ModelTier
from cme.rust_core import run_meshcfo_core


def _infer_tier(model_name: str) -> ModelTier:
    name = model_name.lower()
    if any(token in name for token in ("opus", "max", "frontier")):
        return ModelTier.FRONTIER
    if any(token in name for token in ("gpt-5", "claude 4", "claude-4", "high")):
        return ModelTier.HIGH
    if any(token in name for token in ("sonnet", "4o", "mid", "gpt-4")):
        return ModelTier.MID
    if any(token in name for token in ("mini", "small", "haiku")):
        return ModelTier.SMALL
    return ModelTier.UNKNOWN


def assess_model_parity(origin_model: str, partner_model: str) -> ModelParityCheck:
    payload = run_meshcfo_core(
        "assess_model_parity",
        {"origin_model": origin_model, "partner_model": partner_model},
    )
    return ModelParityCheck.from_dict(payload["value"])
