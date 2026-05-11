"""
Mock Dispatch Service — Flask REST API for fleet / job orchestration (demo).

Pairs with libraries.rest_dispatch_api.RestDispatchApi — same routes and JSON shapes.

When a job is created via POST, the service publishes the assignment to MQTT:
  dispatch/commands/<vehicle_id>

Usage:
  uv run python mock_servers/dispatch_rest_server.py --host 127.0.0.1 --port 8766
"""

from __future__ import annotations

import argparse
import json
import logging
import threading
import time
import uuid
from typing import Any, Dict, List, Optional

try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS
except ImportError as e:
    raise SystemExit(
        "Flask and flask-cors are required. Install automotive extras: uv sync --extra automotive"
    ) from e

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None

logger = logging.getLogger(__name__)


def _mqtt_publish(
    host: str,
    port: int,
    topic: str,
    payload: Dict[str, Any],
) -> None:
    if mqtt is None:
        logger.warning("paho-mqtt not installed; skipping MQTT publish for %s", topic)
        return

    def _run() -> None:
        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"dispatch_mock_{uuid.uuid4().hex[:8]}",
        )
        try:
            client.connect(host, port, keepalive=15)
            client.loop_start()
            time.sleep(0.2)
            body = json.dumps(payload)
            info = client.publish(topic, body, qos=1)
            info.wait_for_publish(timeout=5)
            client.loop_stop()
            client.disconnect()
            logger.info("Published dispatch job to MQTT topic=%s", topic)
        except Exception as exc:
            logger.error("MQTT publish failed: %s", exc)

    threading.Thread(target=_run, daemon=True).start()


def create_app(
    mqtt_broker_host: str = "127.0.0.1",
    mqtt_broker_port: int = 1883,
) -> Flask:
    """Create Flask app with in-memory job queue."""
    jobs: List[Dict[str, Any]] = []

    app = Flask(__name__)
    CORS(app)

    @app.get("/api/health")
    def health() -> Any:
        return jsonify({"status": "ok", "service": "dispatch", "ts": time.time()})

    @app.get("/api/v1/dispatch/jobs")
    def list_jobs() -> Any:
        return jsonify({"jobs": list(jobs), "count": len(jobs)})

    @app.post("/api/v1/dispatch/jobs")
    def create_job() -> Any:
        body = request.get_json(force=True, silent=True) or {}
        vehicle_id = body.get("vehicle_id") or "unknown_vehicle"
        command = body.get("command") or "noop"
        job_id = str(uuid.uuid4())
        record = {
            "id": job_id,
            "vehicle_id": vehicle_id,
            "command": command,
            "status": "queued",
            "created_ts": time.time(),
        }
        jobs.append(record)

        topic = f"dispatch/commands/{vehicle_id}"
        payload = {
            "job_id": job_id,
            "vehicle_id": vehicle_id,
            "command": command,
            "source": "dispatch_service",
            "ts": time.time(),
        }
        _mqtt_publish(mqtt_broker_host, mqtt_broker_port, topic, payload)

        return jsonify({"ok": True, "job": record, "mqtt_topic": topic}), 201

    @app.get("/api/v1/fleet/status")
    def fleet_status() -> Any:
        return jsonify(
            {
                "fleet": "demo",
                "pending_jobs": sum(1 for j in jobs if j.get("status") == "queued"),
                "total_jobs": len(jobs),
            }
        )

    return app


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    p = argparse.ArgumentParser(description="Mock Dispatch Service (Flask)")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8766)
    p.add_argument("--mqtt-host", default="127.0.0.1", help="Broker for outbound job publishes")
    p.add_argument("--mqtt-port", type=int, default=1883)
    p.add_argument("--debug", action="store_true")
    args = p.parse_args()

    app = create_app(
        mqtt_broker_host=args.mqtt_host,
        mqtt_broker_port=args.mqtt_port,
    )
    logger.info(
        "Dispatch Service (mock) listening on http://%s:%s (MQTT %s:%s)",
        args.host,
        args.port,
        args.mqtt_host,
        args.mqtt_port,
    )
    app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)


if __name__ == "__main__":
    main()
