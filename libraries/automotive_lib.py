"""
Unified Automotive Library for Robot Framework.

Single class providing both REST (requests) and MQTT (paho-mqtt) keywords
for the "Pragmatic Lab Setup" demo.

Thread-safe message inbox allows the classic pattern:
  Subscribe → REST POST → Wait For Message
without race conditions.

All default values come from config.py — no hardcoded strings here.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from typing import Any, Dict, List, Optional

from robot.api.deco import library

import requests
import paho.mqtt.client as mqtt

import config


@library(scope="SUITE", version="2.0.0", auto_keywords=True)
class AutomotiveLib:
    """REST + MQTT client for the unified mock server."""

    def __init__(
        self,
        base_url: str = config.BASE_URL,
        mqtt_host: str = config.MQTT_HOST,
        mqtt_port: int = config.MQTT_PORT,
        timeout: int = config.TIMEOUT,
    ):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.base_url = base_url.rstrip("/")
        self.mqtt_host = mqtt_host
        self.mqtt_port = int(mqtt_port)
        self.timeout = timeout

        # Thread-safe MQTT inbox
        self._lock = threading.Lock()
        self._inbox: Dict[str, List[Dict[str, Any]]] = {}
        self._subscribed: set[str] = set()
        self._connected = False

        self._mqtt = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id="robot_test_client",
        )
        self._mqtt.on_connect = self._on_connect
        self._mqtt.on_message = self._on_message
        self._mqtt.on_disconnect = self._on_disconnect

    # ── MQTT callbacks (internal) ───────────────────────────────

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        self._connected = rc == 0
        if self._connected:
            self.logger.info("MQTT connected (%s:%s)", self.mqtt_host, self.mqtt_port)
            for topic in self._subscribed:
                client.subscribe(topic, qos=1)

    def _on_disconnect(self, client, userdata, flags, rc, properties=None):
        self._connected = False

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            payload = msg.payload.decode()

        entry = {"topic": msg.topic, "payload": payload, "ts": time.time()}
        with self._lock:
            self._inbox.setdefault(msg.topic, []).append(entry)

    # ── MQTT keywords ───────────────────────────────────────────

    def connect_mqtt(self) -> bool:
        """Connect to the MQTT broker and start the network loop."""
        self._mqtt.connect(self.mqtt_host, self.mqtt_port, keepalive=60)
        self._mqtt.loop_start()
        time.sleep(0.5)
        return self._connected

    def disconnect_mqtt(self):
        """Stop the network loop and disconnect."""
        self._mqtt.loop_stop()
        self._mqtt.disconnect()
        self._connected = False

    def subscribe(self, topic: str):
        """Subscribe to a topic. Call *before* the action that publishes."""
        self._mqtt.subscribe(topic, qos=1)
        self._subscribed.add(topic)
        self.logger.info("Subscribed → %s", topic)

    def wait_for_message(
        self, topic: str, timeout: int = config.TIMEOUT
    ) -> Optional[Dict[str, Any]]:
        """Block until a message arrives on *topic* or *timeout* seconds elapse."""
        deadline = time.time() + int(timeout)
        while time.time() < deadline:
            with self._lock:
                msgs = self._inbox.get(topic, [])
                if msgs:
                    return msgs.pop(0)
            time.sleep(0.1)
        return None

    def clear_inbox(self):
        """Discard every buffered MQTT message."""
        with self._lock:
            self._inbox.clear()

    # ── REST keywords ───────────────────────────────────────────

    def get_vehicle_status(self) -> Dict[str, Any]:
        """GET /api/vehicle/status — returns the full vehicle state dict."""
        r = requests.get(f"{self.base_url}/api/vehicle/status", timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def server_should_be_healthy(self):
        """GET /api/health — asserts HTTP 200."""
        r = requests.get(f"{self.base_url}/api/health", timeout=self.timeout)
        assert r.status_code == 200, f"Health check failed: {r.status_code}"

    def create_job(self, vehicle_id: str, command: str) -> Dict[str, Any]:
        """POST /api/v1/jobs — returns JSON with job_id and mqtt_topic."""
        r = requests.post(
            f"{self.base_url}/api/v1/jobs",
            json={"vehicle_id": vehicle_id, "command": command},
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()
