"""
Unified Mock Server — Flask REST API + embedded aMQTT broker in a single process.

All ports, hosts, and topic patterns are read from config.py.

Usage:
  uv run python mock_server.py
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
import time
import uuid
from typing import Any, Dict

from amqtt.broker import Broker
from flask import Flask, jsonify, request
from flask_cors import CORS
import paho.mqtt.client as paho_mqtt

import config

logger = logging.getLogger(__name__)

# ── Embedded MQTT broker ────────────────────────────────────────


def _start_mqtt_broker(host: str = "0.0.0.0", port: int = config.MQTT_PORT) -> None:
    """Run aMQTT broker in a daemon thread with its own event loop."""

    async def _serve() -> None:
        broker = Broker()
        await broker.start()
        logger.info("MQTT broker listening on %s:%s", host, port)
        while True:
            await asyncio.sleep(3600)

    def _target() -> None:
        asyncio.run(_serve())

    threading.Thread(target=_target, daemon=True).start()


# ── Flask application ───────────────────────────────────────────


def create_app(
    mqtt_host: str = config.MQTT_HOST,
    mqtt_port: int = config.MQTT_PORT,
) -> Flask:
    app = Flask(__name__)
    CORS(app)

    vehicle_state: Dict[str, Any] = {
        "speed": 0.0,
        "rpm": 800.0,
        "temperature": 90.0,
        "fuel_level": 72.5,
        "status": "RUNNING",
        "version": "1.0.0-demo",
    }

    @app.get("/api/health")
    def health() -> Any:
        return jsonify({"status": "ok", "ts": time.time()})

    @app.get("/api/vehicle/status")
    def vehicle_status() -> Any:
        return jsonify(vehicle_state)

    @app.post("/api/v1/jobs")
    def create_job() -> Any:
        body = request.get_json(force=True, silent=True) or {}
        vehicle_id = body.get("vehicle_id", "unknown")
        command = body.get("command", "noop")
        job_id = str(uuid.uuid4())

        topic = config.MQTT_TOPIC_TEMPLATE.format(vehicle_id=vehicle_id)
        payload = {
            "job_id": job_id,
            "vehicle_id": vehicle_id,
            "command": command,
            "ts": time.time(),
        }

        def _publish() -> None:
            client = paho_mqtt.Client(
                paho_mqtt.CallbackAPIVersion.VERSION2,
                client_id=f"server_{uuid.uuid4().hex[:8]}",
            )
            try:
                client.connect(mqtt_host, mqtt_port, keepalive=15)
                client.loop_start()
                time.sleep(0.2)
                info = client.publish(topic, json.dumps(payload), qos=1)
                info.wait_for_publish(timeout=config.TIMEOUT)
                client.loop_stop()
                client.disconnect()
            except Exception as exc:
                logger.error("MQTT publish failed: %s", exc)

        threading.Thread(target=_publish, daemon=True).start()
        return jsonify({"ok": True, "job_id": job_id, "mqtt_topic": topic}), 201

    return app


# ── Entrypoint ──────────────────────────────────────────────────


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(name)s — %(message)s",
    )
    _start_mqtt_broker(port=config.MQTT_PORT)
    time.sleep(1)

    app = create_app()
    logger.info("Unified Mock Server → %s", config.BASE_URL)
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, threaded=True)


if __name__ == "__main__":
    main()
