"""Tests for the signed, append-only audit ledger and its wiring."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cme.audit import AuditLedger, compute_sig  # noqa: E402
from cme.audit.ledger import TEST_DEFAULT_KEY, resolve_key  # noqa: E402


def _ledger(tmp_path: Path, key: str = "test-key") -> AuditLedger:
    return AuditLedger(tmp_path / "audit.jsonl", key=key)


def test_append_returns_signature_and_writes_line(tmp_path):
    led = _ledger(tmp_path)
    sig = led.append(
        event="recommendation", actor="finance", inputs={"problem": "invest?"},
        sources=["actuals"], confidence="high", rationale="Do X",
    )
    assert isinstance(sig, str) and len(sig) == 64  # hex sha256
    records = led.read_all()
    assert len(records) == 1
    rec = records[0]
    assert rec["event"] == "recommendation"
    assert rec["actor"] == "finance"
    assert rec["confidence"] == "high"
    assert rec["rationale"] == "Do X"
    assert rec["prev_sig"] == ""  # genesis
    assert rec["sig"] == sig
    assert "ts" in rec


def test_optional_fields_omitted_when_none(tmp_path):
    led = _ledger(tmp_path)
    led.append(event="board_narrative", actor="orchestrator",
               inputs={"a": 1}, sources=["finance"])
    rec = led.read_all()[0]
    assert "confidence" not in rec
    assert "rationale" not in rec


def test_chain_links_prev_sig(tmp_path):
    led = _ledger(tmp_path)
    s1 = led.append(event="e1", actor="a", inputs={}, sources=[])
    s2 = led.append(event="e2", actor="b", inputs={}, sources=[])
    recs = led.read_all()
    assert recs[0]["prev_sig"] == ""
    assert recs[1]["prev_sig"] == s1  # each line signs the prior signature
    assert s1 != s2


def test_verify_clean_chain(tmp_path):
    led = _ledger(tmp_path)
    for i in range(5):
        led.append(event=f"e{i}", actor="a", inputs={"i": i}, sources=[])
    intact, first_bad = led.verify()
    assert intact is True
    assert first_bad is None


def test_verify_empty_ledger_is_intact(tmp_path):
    led = _ledger(tmp_path)
    intact, first_bad = led.verify()
    assert intact is True
    assert first_bad is None


def test_tamper_detection_reports_first_index(tmp_path):
    led = _ledger(tmp_path)
    for i in range(4):
        led.append(event=f"e{i}", actor="a", inputs={"i": i}, sources=[],
                   rationale=f"claim {i}")
    path = tmp_path / "audit.jsonl"
    lines = path.read_text().splitlines()
    # Tamper the content of record index 2.
    rec = json.loads(lines[2])
    rec["rationale"] = "TAMPERED"
    lines[2] = json.dumps(rec)
    path.write_text("\n".join(lines) + "\n")

    intact, first_bad = led.verify()
    assert intact is False
    assert first_bad == 2


def test_deletion_breaks_chain(tmp_path):
    led = _ledger(tmp_path)
    for i in range(4):
        led.append(event=f"e{i}", actor="a", inputs={"i": i}, sources=[])
    path = tmp_path / "audit.jsonl"
    lines = path.read_text().splitlines()
    del lines[1]  # remove a line -> chain breaks at the next line
    path.write_text("\n".join(lines) + "\n")

    intact, first_bad = led.verify()
    assert intact is False
    assert first_bad == 1


def test_wrong_key_fails_verification(tmp_path):
    led = _ledger(tmp_path, key="right-key")
    led.append(event="e", actor="a", inputs={}, sources=[])
    other = AuditLedger(tmp_path / "audit.jsonl", key="wrong-key")
    intact, first_bad = other.verify()
    assert intact is False
    assert first_bad == 0


def test_key_resolution_prefers_explicit_then_env_then_default(tmp_path, monkeypatch):
    monkeypatch.delenv("AUDIT_LEDGER_KEY", raising=False)
    assert resolve_key() == TEST_DEFAULT_KEY
    monkeypatch.setenv("AUDIT_LEDGER_KEY", "from-env")
    assert resolve_key() == "from-env"
    assert resolve_key("explicit") == "explicit"


def test_signature_matches_manual_computation(tmp_path):
    led = _ledger(tmp_path, key="k")
    led.append(event="e", actor="a", inputs={"x": 1}, sources=["s"], ts="2026-01-01T00:00:00+00:00")
    rec = led.read_all()[0]
    manual = compute_sig("k", rec, "")
    assert rec["sig"] == manual


def test_orchestrator_writes_signed_recommendations(tmp_path):
    from demo import ComplianceAgent, FinanceAgent, StrategyAgent
    from cme.orchestrator import EnterpriseOrchestrator

    led = AuditLedger(tmp_path / "audit.jsonl", key="k")
    orch = EnterpriseOrchestrator(
        agents=[FinanceAgent(), StrategyAgent(), ComplianceAgent()], ledger=led
    )
    orch.orchestrate("Should we invest in an enterprise tier this quarter?")

    records = led.read_all()
    events = [r["event"] for r in records]
    assert events.count("recommendation") == 3  # one per agent
    assert "board_narrative" in events
    intact, first_bad = led.verify()
    assert intact is True and first_bad is None


if __name__ == "__main__":  # pragma: no cover
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
