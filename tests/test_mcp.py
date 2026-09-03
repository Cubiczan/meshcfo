"""MCP server: tool catalog + one real MeshCFO happy path (not a stub)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import asyncio

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from cme.mcp import TOOL_NAMES, build_server  # noqa: E402
from cme.mcp.session import MeshCFOService  # noqa: E402


def _service(tmp_path: Path) -> MeshCFOService:
    return MeshCFOService(
        registry_path=tmp_path / "registry.json",
        ledger_path=tmp_path / "audit.jsonl",
        company_name="Acme",
    )


def _payload(result) -> dict:
    """Unwrap MCP CallToolResult into the MeshCFO JSON dict."""
    if getattr(result, "structured_content", None):
        data = result.structured_content
        if isinstance(data, dict) and "result" in data and isinstance(data["result"], dict):
            return data["result"]
        if isinstance(data, dict):
            return data
    for block in getattr(result, "content", []) or []:
        text = getattr(block, "text", None)
        if text:
            parsed = json.loads(text)
            if isinstance(parsed, dict) and "result" in parsed and isinstance(parsed["result"], dict):
                return parsed["result"]
            return parsed
    raise AssertionError(f"unreadable tool result: {result!r}")


def test_tools_list_returns_cfo_tools(tmp_path):
    from mcp import Client

    async def _run():
        server = build_server(_service(tmp_path))
        async with Client(server) as client:
            listed = await client.list_tools()
            return {t.name for t in listed.tools}

    names = asyncio.run(_run())
    assert names == set(TOOL_NAMES)
    assert names == {
        "forecast",
        "investment_case",
        "board_output",
        "lock",
        "verify_audit",
    }


def test_investment_case_hits_real_library_and_writes_audit(tmp_path):
    from mcp import Client

    async def _run():
        service = _service(tmp_path)
        server = build_server(service)
        async with Client(server) as client:
            result = await client.call_tool(
                "investment_case",
                {
                    "title": "Fund enterprise tier",
                    "problem": "Should we fund a dedicated enterprise tier this quarter?",
                    "company": "Acme",
                    "investment_amount_usd": 2_500_000,
                    "expected_payback_months": 14,
                    "current_runway_months": 18,
                    "expected_upside": ["Higher ACV"],
                    "key_risks": ["Adoption lag"],
                },
            )
            payload = _payload(result)

            verify = _payload(await client.call_tool("verify_audit", {}))
            locked = _payload(
                await client.call_tool(
                    "lock",
                    {
                        "decision_id": payload["decision_id"],
                        "validator": "fresh_instance",
                        "item": "Investment spec v1",
                        "rationale": "Spec coheres; flip criteria explicit.",
                    },
                )
            )
            return payload, verify, locked

    payload, verify, locked = asyncio.run(_run())

    assert payload["task"] == "investment_case"
    assert payload["decision_id"]
    assert payload["lock_state"] == "PROVISIONAL_LOCK"
    assert payload["artifact_markdown"]
    assert "decision_id" in payload["artifact_markdown"]
    agents = {e["agent"] for e in payload["audit_entries"]}
    assert agents == {"finance", "strategy", "compliance"}
    assert payload["foundation_findings"]

    assert verify["intact"] is True
    assert verify["first_tampered_index"] is None
    assert verify["record_count"] >= 1
    assert Path(verify["path"]).exists()

    assert locked["lock_state"] == "LOCKED"
    assert "Investment spec v1" in locked["locked_decisions"]


def test_python_module_stdio_tools_list(tmp_path):
    """``python -m cme.mcp`` speaks MCP over stdio and lists the CFO tools."""
    from mcp import Client
    from mcp.client.stdio import StdioServerParameters

    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    env["MESHCFO_REGISTRY"] = str(tmp_path / "registry.json")
    env["MESHCFO_LEDGER"] = str(tmp_path / "audit.jsonl")

    async def _run():
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "cme.mcp"],
            env=env,
            cwd=str(ROOT),
        )
        async with Client(params) as client:
            listed = await client.list_tools()
            return {t.name for t in listed.tools}

    names = asyncio.run(_run())
    assert names == set(TOOL_NAMES)


def test_npm_wrapper_spawns_python_stdio(tmp_path):
    """``node bin/meshcfo-mcp.js`` execs the Python MCP when cme is importable."""
    import shutil

    from mcp import Client
    from mcp.client.stdio import StdioServerParameters

    node = shutil.which("node")
    if not node:
        return
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    env["MESHCFO_PYTHON"] = sys.executable
    env["MESHCFO_REGISTRY"] = str(tmp_path / "registry.json")
    env["MESHCFO_LEDGER"] = str(tmp_path / "audit.jsonl")

    async def _run():
        params = StdioServerParameters(
            command=node,
            args=[str(ROOT / "bin" / "meshcfo-mcp.js")],
            env=env,
            cwd=str(ROOT),
        )
        async with Client(params) as client:
            listed = await client.list_tools()
            return {t.name for t in listed.tools}

    names = asyncio.run(_run())
    assert names == set(TOOL_NAMES)
