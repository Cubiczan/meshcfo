"""Official-SDK stdio MCP server for MeshCFO.

Tools wrap ``CFOOperatingSystem`` and ``AuditLedger`` — CHP stays the lock.
"""
from __future__ import annotations

import sys
from typing import List, Optional

from cme.mcp.session import MeshCFOService

TOOL_NAMES = (
    "forecast",
    "investment_case",
    "board_output",
    "lock",
    "verify_audit",
)

SERVER_NAME = "meshcfo"
SERVER_VERSION = "0.1.0"
INSTRUCTIONS = (
    "Cubiczan MeshCFO — auditable multi-agent CFO. "
    "CHP is the lock; MCP is the pipe. "
    "Default demo agents run offline with no API key. "
    "Tools: forecast, investment_case, board_output, lock, verify_audit."
)


def _load_sdk():
    try:
        from mcp.server import MCPServer

        return MCPServer
    except ImportError:
        try:
            from mcp.server.fastmcp import FastMCP as MCPServer  # type: ignore[no-redef]

            return MCPServer
        except ImportError as exc:  # pragma: no cover - install hint
            raise SystemExit(
                "The official MCP SDK is required. "
                "Install MeshCFO with the mcp extra: pip install -e '.[mcp]'"
            ) from exc


def build_server(service: MeshCFOService | None = None):
    """Build the MeshCFO MCP server (stdio via ``run()``)."""
    service = service or MeshCFOService.from_env()
    MCPServer = _load_sdk()
    mcp = MCPServer(
        name=SERVER_NAME,
        version=SERVER_VERSION,
        instructions=INSTRUCTIONS,
    )

    @mcp.tool()
    def forecast(
        title: str,
        problem: str,
        company: str = "Acme",
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
        """Run a driver-based operating forecast (Finance + Strategy + Compliance + CHP)."""
        return service.run_forecast(
            title=title,
            problem=problem,
            company=company,
            owner=owner,
            origin_model=origin_model,
            partner_model=partner_model,
            partner_system=partner_system,
            strategic_priorities=strategic_priorities,
            constraints=constraints,
            base_revenue_usd=base_revenue_usd,
            base_opex_usd=base_opex_usd,
            growth_assumption_pct=growth_assumption_pct,
            churn_assumption_pct=churn_assumption_pct,
            minimum_runway_months=minimum_runway_months,
            current_runway_months=current_runway_months,
        )

    @mcp.tool()
    def investment_case(
        title: str,
        problem: str,
        company: str = "Acme",
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
        """Build a capital-allocation investment case with milestone-gated release."""
        return service.run_investment_case(
            title=title,
            problem=problem,
            company=company,
            owner=owner,
            origin_model=origin_model,
            partner_model=partner_model,
            partner_system=partner_system,
            strategic_priorities=strategic_priorities,
            constraints=constraints,
            investment_amount_usd=investment_amount_usd,
            expected_payback_months=expected_payback_months,
            minimum_runway_months=minimum_runway_months,
            current_runway_months=current_runway_months,
            expected_upside=expected_upside,
            key_risks=key_risks,
        )

    @mcp.tool()
    def board_output(
        title: str,
        problem: str,
        company: str = "Acme",
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
        """Produce a board decision packet with ranked options and dissent surface."""
        return service.run_board_output(
            title=title,
            problem=problem,
            company=company,
            owner=owner,
            origin_model=origin_model,
            partner_model=partner_model,
            partner_system=partner_system,
            strategic_priorities=strategic_priorities,
            constraints=constraints,
            options=options,
            recommended_option_index=recommended_option_index,
            open_questions=open_questions,
            prior_board_decisions=prior_board_decisions,
            strategic_risks=strategic_risks,
        )

    @mcp.tool()
    def lock(
        decision_id: str,
        validator: str,
        item: str,
        rationale: str,
        challenge: str = "Stress test before lock progression.",
        confirm: bool = True,
    ) -> dict:
        """Apply third-party validation and advance CHP lock state (PROVISIONAL_LOCK → LOCKED)."""
        return service.lock(
            decision_id,
            validator=validator,
            item=item,
            rationale=rationale,
            challenge=challenge,
            confirm=confirm,
        )

    @mcp.tool()
    def verify_audit(path: Optional[str] = None) -> dict:
        """Verify the HMAC-SHA256 append-only audit ledger chain."""
        return service.verify_audit(path)

    return mcp


def main(argv: List[str] | None = None) -> int:
    """Start the stdio MCP server. ``argv`` is accepted for CLI symmetry and ignored."""
    del argv
    try:
        build_server().run(transport="stdio")
    except KeyboardInterrupt:
        return 130
    except BrokenPipeError:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
