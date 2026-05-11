# Automotive Test Framework — Pragmatic Lab Setup

Simplified **Robot Framework + Python 3.12** demo for REST + MQTT integration testing.

One unified server, one library, one test — easy to explain in a live presentation.

## Architecture

```
mock_server.py        ← Flask :8080 + embedded aMQTT broker :1883
libraries/automotive_lib.py  ← Robot keywords (REST + MQTT, thread-safe)
tests/network_stack.robot    ← E2E test: Subscribe → POST → Validate
```

### Flow

```
Robot Test
  │
  ├─ Subscribe to  vehicle/{id}/commands  (MQTT)
  │
  ├─ POST /api/v1/jobs  ──→  Flask handler
  │                             ├─ stores job
  │                             └─ publishes to MQTT  vehicle/{id}/commands
  │                                       │
  │                                       ▼
  └─ Wait For Message  ◄──────  aMQTT broker  ◄──  paho subscriber
```

## Quick start

```bash
uv sync --extra automotive          # install deps
uv run robot --pythonpath . --outputdir results tests/network_stack.robot
```

Or via Make:

```bash
make install
make test
```

### Ports

| Service | Port |
|---------|------|
| Flask REST API | 8080 |
| MQTT broker (aMQTT) | 1883 |

### Manual server (optional)

```bash
uv run python mock_server.py
```

## Project structure

```
├── mock_server.py              # Unified Flask + MQTT broker
├── libraries/
│   └── automotive_lib.py       # Robot keywords (REST + MQTT)
├── tests/
│   └── network_stack.robot     # E2E demo suite
├── variables/
│   └── config.py               # Shared constants
├── resources/
│   └── vehicle_signals.dbc     # CAN DBC file (bonus reference)
├── _old/                       # Previous multi-service files (archived)
├── Makefile
└── pyproject.toml
```

## Code quality

```bash
make lint       # flake8 + black --check
make format     # auto-format with black
```
