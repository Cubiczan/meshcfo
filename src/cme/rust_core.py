from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "rust" / "Cargo.toml"
DEBUG_BIN = ROOT / "rust" / "target" / "debug" / "meshcfo-core"
RELEASE_BIN = ROOT / "rust" / "target" / "release" / "meshcfo-core"


def run_meshcfo_core(command: str, payload: dict) -> dict:
    request = json.dumps({"command": command, "input": payload})
    if RELEASE_BIN.exists():
        proc = subprocess.run([str(RELEASE_BIN)], input=request, text=True, capture_output=True, check=True)
        return json.loads(proc.stdout)
    if DEBUG_BIN.exists():
        proc = subprocess.run([str(DEBUG_BIN)], input=request, text=True, capture_output=True, check=True)
        return json.loads(proc.stdout)

    proc = subprocess.run(
        ["cargo", "run", "--quiet", "--manifest-path", str(MANIFEST), "--bin", "meshcfo-core"],
        input=request,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(proc.stdout)


def compute_sig(key: str, record: dict, prev_sig: str) -> str:
    payload = {
        "key": key,
        "record": record,
        "prev_sig": prev_sig,
    }
    response = run_meshcfo_core("compute_sig", payload)
    value = response["value"]
    return value["sig"] if isinstance(value, dict) else value


def score_foundation(payload: dict) -> int:
    response = run_meshcfo_core("score_foundation", {"input": payload})
    value = response["value"]
    if isinstance(value, dict):
        return int(value["score"])
    return int(value)


def select_context(payload: dict) -> list[str]:
    response = run_meshcfo_core("select_context", {"input": payload})
    value = response["value"]
    return list(value["selected_ids"] if isinstance(value, dict) else value)


def verify_audit_chain(payload: dict) -> dict:
    response = run_meshcfo_core("verify_audit_chain", {"input": payload})
    return response["value"]


def department_metrics(payload: dict) -> dict:
    response = run_meshcfo_core("department_metrics", {"input": payload})
    return response["value"]
