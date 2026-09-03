import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import test from "node:test";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const pkg = JSON.parse(readFileSync(join(root, "package.json"), "utf8"));

test("npm package is the Cubiczan MeshCFO MCP wrapper", () => {
  assert.equal(pkg.name, "@cubiczan/meshcfo-mcp");
  assert.equal(pkg.bin["meshcfo-mcp"], "./bin/meshcfo-mcp.js");
  assert.match(pkg.author, /Sam Desigan/);
  assert.match(pkg.author, /sam@cubiczan.com/);
  assert.doesNotMatch(JSON.stringify(pkg), /CubicZan/);
});

test("wrapper fails honestly when Python MeshCFO is missing", () => {
  const result = spawnSync(process.execPath, [join(root, "bin/meshcfo-mcp.js")], {
    encoding: "utf8",
    env: { ...process.env, MESHCFO_PYTHON: "python3-not-meshcfo-missing" },
  });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /pip install -e/);
  assert.match(result.stderr, /python3 -m cme.mcp/);
});
