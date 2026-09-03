# Publishing MeshCFO MCP (later)

Packaging is ready. **Do not** `npm publish` or `twine upload` from this
environment — there are no registry tokens here.

## Python (not on PyPI yet)

```bash
pip install -e ".[mcp]"
# later: python -m build && twine upload dist/*
```

Console script: `meshcfo-mcp` → `cme.mcp:main`.

## npm (`@cubiczan/meshcfo-mcp`)

Thin spawn wrapper only. It execs `python3 -m cme.mcp` after probing
`import cme.mcp`. Publish from a machine with npm credentials:

```bash
# later, from a trusted machine:
npm publish --access public
```

Until then, hosts should use the Python entrypoint (`meshcfo-mcp` or
`python3 -m cme.mcp`) after `pip install -e ".[mcp]"`.
