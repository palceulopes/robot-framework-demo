"""Robot Framework library — REST + MQTT keywords."""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from robot.api.deco import library  # noqa: E402
import requests  # noqa: E402
import paho.mqtt.client as mqtt  # noqa: E402 #client for MQTT communication
import config  # noqa: E402


@library(scope="SUITE", auto_keywords=True)
class AutomotiveLib:

    def __init__(self):
        self.messages = []
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_message = self._on_message

    def _on_message(self, client, userdata, msg):
        self.messages.append(json.loads(msg.payload))

    # MQTT

    def connect_mqtt(self):
        self.client.connect(config.MQTT_HOST, config.MQTT_PORT)
        self.client.loop_start()
        time.sleep(0.5)

    def disconnect_mqtt(self):
        self.client.loop_stop()
        self.client.disconnect()

    def publish_speed(self, speed):
        self.client.publish("vehicle/speed", json.dumps({"speed": int(speed)}))

    def subscribe_speed(self):
        self.client.subscribe("vehicle/speed")

    def wait_for_message(self, timeout=5):
        deadline = time.time() + int(timeout)
        while time.time() < deadline:
            if self.messages:
                return self.messages.pop(0)
            time.sleep(0.1)
        return None
    
    

    # REST

    def get_vehicle_speed(self): 
        return requests.get(f"{config.BASE_URL}/api/vehicle/speed").json()
