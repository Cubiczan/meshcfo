"""Stdio MCP pipe for MeshCFO.

CHP is the lock; MCP is the pipe. Tools wrap ``CFOOperatingSystem`` and the
HMAC-SHA256 audit ledger — the same surface as the ``cfo-os`` CLI.
"""

from cme.mcp.server import TOOL_NAMES, build_server, main

__all__ = ["TOOL_NAMES", "build_server", "main"]
