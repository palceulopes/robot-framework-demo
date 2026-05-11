# AGENTS.md

## Cursor Cloud specific instructions

### Overview

Automotive Test Framework — Robot Framework + Python 3.12 test automation suite. All infrastructure (MQTT broker, Vehicle Service, Dispatch Service) is self-contained via embedded mock servers; no external databases, Docker, or message brokers required.

### Quick reference

Commands are documented in `README.md` and `Makefile` (`make help`). Key ones:

| Action | Command |
|---|---|
| Install deps | `uv sync --extra automotive --extra dev` |
| Lint | `uv run flake8 libraries/ mock_servers/ --max-line-length=88` |
| Format check | `uv run black --check libraries/ mock_servers/` |
| All tests | `uv run robot --pythonpath . --listener libraries.automotive_listener --outputdir results tests/network_stack.robot tests/bonus/` |
| Main demo only | `uv run robot --pythonpath . --listener libraries.automotive_listener --outputdir results tests/network_stack.robot` |
| Bonus suites | `uv run robot --pythonpath . tests/bonus/` |
| Setup verify | `uv run python setup_project.py` |

### Gotchas

- `uv` must be on `PATH`. It installs to `~/.local/bin` — the update script handles this.
- The main demo suite (`tests/network_stack.robot`) auto-starts MQTT broker (:1883), Vehicle Service (:8765), and Dispatch Service (:8766) via its `Suite Setup` keyword. No manual process startup needed.
- Always pass `--pythonpath .` to `robot` so the `variables` and `libraries` packages resolve correctly.
- Clean artifacts before reruns: `rm -rf results output.xml log.html report.html`
- The `VirtualBus was not properly shut down` warning in bonus tests is benign and expected.
- Pre-existing lint issues exist (W293 whitespace, E501 line length) — these are in the repo's current state.
