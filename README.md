# Automotive Test Framework (Robot + Python)

Automation framework built with **Robot Framework** and **Python 3.12**, with a small **microservices-style** stack for demos and HiL-style integration tests:

- **Vehicle Service** (`mock_servers/vehicle_service_server.py`): Flask REST mock (signals, diagnostics, health) — the “ECU-facing” HTTP façade.
- **Dispatch Service** (`mock_servers/dispatch_rest_server.py`): Flask REST mock for jobs/fleet; posting a job publishes to MQTT `dispatch/commands/<vehicle_id>`.
- **MQTT broker** (`mock_servers/mqtt_broker_helper.py`): embedded **aMQTT** — no Mosquitto binary required.
- **Python libraries + Robot resources**: REST/MQTT keywords and optional CAN/DBC bonus paths.
- **Custom listener** (`libraries/automotive_listener.py`): extra metrics beyond PASS/FAIL.

Use **uv** for installs and `uv run` so CLI usage matches CI and the live demo.

## TL;DR (demo commands)

Install extras once:

```bash
uv sync --extra automotive
```

Main demo suite (Vehicle + Dispatch + MQTT; starts mocks via `Process` — nothing manual to launch):

```bash
uv run robot --pythonpath . --listener libraries.automotive_listener ^
  --logtitle "HiL Vehicle/Dispatch" ^
  --reporttitle "Integration demo" ^
  --tagstatinclude demo ^
  --outputdir results ^
  tests/network_stack.robot
```

(PowerShell uses `` ` `` for line continuation, or put the command on one line.)

Suites load config with `Variables    variables.config` (`variables/config.py`). Use `--pythonpath .` **or** `uv pip install -e .` so Python resolves the `variables` and `libraries` packages.

### Ports (defaults)

| Service | Port |
|--------|------|
| Vehicle Service (REST) | 8765 |
| Dispatch Service (REST) | 8766 |
| MQTT (aMQTT) | 1883 |

Clean prior Robot artifacts before a rerun (PowerShell, repo root):

```powershell
Remove-Item -Recurse -Force results, logs, .robocache -ErrorAction SilentlyContinue
```

On Windows you can also run `delete_logs_results.bat`.

### Manual mock processes (optional)

If you start mocks yourself instead of the suite `Suite Setup`:

```bash
uv run python mock_servers/mqtt_broker_helper.py
uv run python mock_servers/vehicle_service_server.py --host 127.0.0.1 --port 8765
uv run python mock_servers/dispatch_rest_server.py --host 127.0.0.1 --port 8766 --mqtt-host 127.0.0.1 --mqtt-port 1883
```

## Structure

```
robot-framework/
├── libraries/        # REST Vehicle/Dispatch clients, MQTT, listener, CAN bonus
├── mock_servers/     # vehicle_service_server, dispatch_rest_server, mqtt broker helper
├── resources/        # Robot keyword wrappers (*.resource)
├── tests/            # network_stack.robot (main demo); bonus/ for CAN-focused suites
└── variables/        # config (hosts, ports, DBC path)
```

## Makefile (Windows-oriented)

Run `make help`. Targets use **`uv run`** where applicable. Smoke/integration suites live under `tests/bonus/`.

## Notes for a technical interview / live demo

- **Vehicle + Dispatch + MQTT + listener** is the primary narrative (microservices + messaging).
- **CAN/DBC** under `tests/bonus/` is optional depth, not required for the REST/MQTT story.
