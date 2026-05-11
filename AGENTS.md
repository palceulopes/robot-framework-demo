# AGENTS.md

## Cursor Cloud specific instructions

### Overview

Automotive Test Framework — "Pragmatic Lab Setup" with Robot Framework + Python 3.12. A single unified mock server (`mock_server.py`) hosts Flask REST on :8080 and an embedded aMQTT broker on :1883. No external infrastructure required.

### Quick reference

| Action | Command |
|---|---|
| Install deps | `uv sync --extra automotive --extra dev` |
| Run E2E test | `uv run robot --pythonpath . --outputdir results tests/network_stack.robot` |
| Lint | `uv run flake8 mock_server.py libraries/automotive_lib.py --max-line-length=88` |
| Format check | `uv run black --check mock_server.py libraries/automotive_lib.py` |
| Start server manually | `uv run python mock_server.py` |

See `Makefile` for shorthand targets (`make test`, `make lint`, etc.).

### Gotchas

- `uv` must be on `PATH` (`~/.local/bin`). The update script handles installation.
- Always pass `--pythonpath .` to `robot` so `libraries` and `variables` packages resolve.
- The test suite auto-starts `mock_server.py` via Robot's `Process` library — no manual startup needed.
- Old multi-service files are archived in `_old/` for reference.
- Clean artifacts before reruns: `rm -rf results output.xml log.html report.html`
