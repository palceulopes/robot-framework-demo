# Automotive Test Framework

Simple **Robot Framework + Python 3.12** demo — Vehicle Service (REST) + MQTT.

## Architecture

```
mock_server.py        ← Flask REST API (:8080)
mqtt_broker.py        ← aMQTT broker (:1883)
libraries/automotive_lib.py  ← Robot keywords (REST + MQTT)
tests/network_stack.robot    ← E2E test
config.py             ← All ports/hosts in one place
```

## Quick start

```bash
uv sync --extra automotive
uv run robot -d results tests/network_stack.robot
```

## What the test does

1. Starts the MQTT broker and Vehicle Service
2. **Vehicle Status** — `GET /api/vehicle/status`, checks speed + rpm
3. **MQTT Publish & Receive** — publishes to `vehicle/speed`, verifies message arrives
