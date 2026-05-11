"""Robot Framework library — REST + MQTT keywords."""

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from robot.api.deco import library  # noqa: E402
import requests  # noqa: E402
import paho.mqtt.client as mqtt  # noqa: E402
import config  # noqa: E402


@library(scope="SUITE", version="3.0.0", auto_keywords=True)
class AutomotiveLib:

    def __init__(
        self,
        base_url: str = config.BASE_URL,
        mqtt_host: str = config.MQTT_HOST,
        mqtt_port: int = config.MQTT_PORT,
    ):
        self.base_url = base_url
        self.mqtt_host = mqtt_host
        self.mqtt_port = int(mqtt_port)
        self._messages: list[Dict[str, Any]] = []
        self._client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id="robot_test"
        )
        self._client.on_message = self._on_message

    def _on_message(self, client, userdata, msg):
        self._messages.append({"topic": msg.topic, "payload": json.loads(msg.payload)})

    # ── MQTT ────────────────────────────────────────────────────

    def connect_mqtt(self):
        self._client.connect(self.mqtt_host, self.mqtt_port)
        self._client.loop_start()
        time.sleep(0.5)

    def disconnect_mqtt(self):
        self._client.loop_stop()
        self._client.disconnect()

    def subscribe(self, topic: str):
        self._client.subscribe(topic)

    def publish(self, topic: str, message: Dict[str, Any]):
        self._client.publish(topic, json.dumps(message))

    def wait_for_message(self, timeout: int = 5) -> Optional[Dict[str, Any]]:
        deadline = time.time() + int(timeout)
        while time.time() < deadline:
            if self._messages:
                return self._messages.pop(0)
            time.sleep(0.1)
        return None

    # ── REST ────────────────────────────────────────────────────

    def get_vehicle_status(self) -> Dict[str, Any]:
        return requests.get(f"{self.base_url}/api/vehicle/status").json()

    def server_should_be_healthy(self):
        r = requests.get(f"{self.base_url}/api/vehicle/status")
        assert r.status_code == 200
