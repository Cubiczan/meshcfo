#!/usr/bin/env node
/**
 * Thin npm wrapper: spawn the Python MeshCFO stdio MCP.
 *
 * Honest pipe only — does not reimplement CFOOperatingSystem.
 * Requires `pip install -e ".[mcp]"` (MeshCFO is not on PyPI yet).
 */
import { spawn, spawnSync } from "node:child_process";

function canImportCme(python) {
  const probe = spawnSync(
    python,
    ["-c", "import cme.mcp, cme.cfo_os; print('ok')"],
    { encoding: "utf8" },
  );
  return probe.status === 0;
}

function resolvePython() {
  const explicit = process.env.MESHCFO_PYTHON;
  if (explicit) return explicit;
  for (const candidate of ["python3", "python"]) {
    const which = spawnSync("sh", ["-c", `command -v ${candidate}`], {
      encoding: "utf8",
    });
    if (which.status === 0 && which.stdout.trim()) return candidate;
  }
  return "python3";
}

function installHint() {
  return [
    "MeshCFO MCP needs the Python package (not on PyPI yet).",
    "",
    "  git clone https://github.com/Cubiczan/meshcfo.git",
    "  cd meshcfo && pip install -e \".[mcp]\"",
    "",
    "Then re-run this command, or point your MCP host at:",
    '  { "command": "meshcfo-mcp", "args": [] }',
    "  or: python3 -m cme.mcp",
    "",
    "Override the interpreter with MESHCFO_PYTHON if needed.",
  ].join("\n");
}

const python = resolvePython();
if (!canImportCme(python)) {
  process.stderr.write(`${installHint()}\n`);
  process.exit(1);
}

const child = spawn(python, ["-m", "cme.mcp", ...process.argv.slice(2)], {
  stdio: "inherit",
  env: process.env,
});
child.on("exit", (code, signal) => {
  if (signal) process.kill(process.pid, signal);
  process.exit(code ?? 1);
});
child.on("error", (err) => {
  process.stderr.write(`Failed to spawn ${python} -m cme.mcp: ${err.message}\n`);
  process.exit(1);
});
