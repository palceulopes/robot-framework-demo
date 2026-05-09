# Automotive Test Framework (Robot + Python)

Automation framework built with **Robot Framework** and **Python 3.12**, with a simple “microservices” setup for a demo:

- **Mock ECU via REST (Flask)**: simulates ECU-like endpoints.
- **Embedded MQTT broker (aMQTT)**: pub/sub to simulate a vehicle/sensor network.
- **Python client libraries**: Robot keywords call technical libraries.
- **Custom listener**: metrics beyond PASS/FAIL.

The goal is to show **real day-to-day workflow**: run tests, interpret failures, and adjust quickly (config/resources/libraries).

## TL;DR (demo commands that work)

```bash
uv sync --extra automotive
uv run robot --pythonpath . --listener libraries.automotive_listener tests/network_stack.robot
```

Suites load config with `Variables    variables.config` (module `variables/config.py`). Use `--pythonpath .` **or** `uv pip install -e .` so Python resolves the `variables` package.

To wipe prior Robot output before a clean run (PowerShell, from repo root):
```powershell
Remove-Item -Recurse -Force results, logs, .robocache -ErrorAction SilentlyContinue
```
Optional on Windows: `delete_logs_results.bat` removes `results/`, `logs/`, `.robocache/` (no `uv`) before a clean rerun.

## Structure (quick view)

```
robot-framework/
├── libraries/        # Python technical logic (REST client, MQTT client, listener, CAN bonus)
├── mock_servers/     # processes: Flask mock ECU + MQTT broker helper
├── resources/        # reusable Robot keywords (REST/MQTT/CAN)
├── tests/            # Robot suites (main demo: network_stack.robot)
└── variables/        # configuration (hosts/ports/paths)
```

## Documentation

- **Quick start**: `QUICKSTART.md`
- **Technical details / architecture**: `TECHNICAL_DOCUMENTATION.md`

## Notes (for the live session)

- **REST + MQTT + Listener** are the critical path for the demo.
- **CAN/DBC** exists as an automotive “bonus”, but it’s not required for the session.
