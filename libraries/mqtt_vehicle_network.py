"""
MQTT Vehicle Network Library for Robot Framework.

Provides keywords for vehicle network simulation using MQTT.
Simulates vehicle communication channels (CAN-like over MQTT).

Example:
    *** Settings ***
    Library    libraries.mqtt_vehicle_network    broker_host=localhost
    
    *** Test Cases ***
    Test Vehicle Speed Alert
        Publish Vehicle Signal    vehicle/speed    {"value": 120, "unit": "kmh"}
        Wait For Vehicle Alert    vehicle/alerts/high_speed    5s
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from robot.api.deco import library

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None

logger = logging.getLogger(__name__)


@library(scope="SUITE", version="1.0.0", auto_keywords=True)
class MqttVehicleNetwork:
    """
    MQTT-based vehicle network simulation for testing.
    
    Provides:
    - Signal injection via MQTT topics
    - Message subscription and waiting
    - Vehicle network simulation
    - Topic-based communication (CAN-like)
    """
    
    # Standard vehicle topics
    TOPICS = {
        "speed": "vehicle/sensors/speed",
        "temperature": "vehicle/sensors/temperature",
        "rpm": "vehicle/sensors/engine/rpm",
        "fuel_level": "vehicle/sensors/fuel_level",
        "alerts": "vehicle/alerts/+",
        "high_speed": "vehicle/alerts/high_speed",
        "high_temp": "vehicle/alerts/high_temperature",
        "maintenance": "vehicle/alerts/maintenance",
        "diagnostics": "vehicle/diagnostics/+",
    }
    
    def __init__(
        self,
        broker_host: str = "localhost",
        broker_port: int = 1883,
        client_id: str = "automotive_test",
        auto_connect: bool = True,
    ):
        """
        Initialize MQTT vehicle network.
        
        Args:
            broker_host: MQTT broker hostname
            broker_port: MQTT broker port
            client_id: MQTT client ID
            auto_connect: Automatically connect on init
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        if mqtt is None:
            raise RuntimeError(
                "paho-mqtt not installed. Install with: pip install paho-mqtt"
            )
        
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = client_id
        self.connected = False
        
        # Message storage for waiting/assertions
        self.received_messages: Dict[str, List[Dict[str, Any]]] = {}
        
        # Create MQTT client
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        # Callbacks for message receipt
        self._message_callbacks: Dict[str, Callable] = {}
        
        if auto_connect:
            self.connect_to_broker()
    
    def _on_connect(self, client, userdata, connect_flags, reason_code, properties=None):
        """MQTT on_connect callback."""
        if reason_code == 0:
            self.connected = True
            self.logger.info(f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            # Subscribe to all vehicle topics
            for topic in self.TOPICS.values():
                client.subscribe(topic, qos=1)
        else:
            self.logger.error(f"MQTT connection failed: {reason_code}")
            self.connected = False
    
    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties=None):
        """MQTT on_disconnect callback."""
        self.connected = False
        self.logger.warning(f"Disconnected from MQTT broker (code: {reason_code})")
    
    def _on_message(self, client, userdata, message):
        """MQTT on_message callback."""
        try:
            payload = message.payload.decode('utf-8')
            data = json.loads(payload)
            
            # Store message for later retrieval
            if message.topic not in self.received_messages:
                self.received_messages[message.topic] = []
            
            self.received_messages[message.topic].append({
                "timestamp": time.time(),
                "topic": message.topic,
                "payload": data,
                "raw": payload,
            })
            
            self.logger.debug(f"Message received on {message.topic}: {data}")
            
            # Call registered callbacks
            if message.topic in self._message_callbacks:
                self._message_callbacks[message.topic](data)
        
        except json.JSONDecodeError:
            self.logger.warning(f"Invalid JSON on {message.topic}")
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
    
    def connect_to_broker(self) -> bool:
        """
        Connect to MQTT broker.
        
        Returns:
            True if connection successful
        """
        try:
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            time.sleep(0.5)  # Wait for connection
            return self.connected
        except Exception as e:
            self.logger.error(f"Failed to connect to broker: {e}")
            return False
    
    def disconnect_from_broker(self) -> bool:
        """Disconnect from MQTT broker."""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            self.logger.info("Disconnected from MQTT broker")
            return True
        except Exception as e:
            self.logger.error(f"Error disconnecting: {e}")
            return False
    
    def publish_vehicle_signal(
        self,
        signal_type: str,
        value: float,
        unit: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Publish a vehicle signal.
        
        Args:
            signal_type: Type of signal (speed, temperature, rpm, etc.)
            value: Signal value
            unit: Signal unit (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            True if published successfully
        """
        try:
            topic = self.TOPICS.get(signal_type, f"vehicle/signals/{signal_type}")
            
            payload = {
                "timestamp": time.time(),
                "value": value,
                "unit": unit,
            }
            
            if metadata:
                payload.update(metadata)
            
            self.client.publish(topic, json.dumps(payload), qos=1)
            self.logger.info(f"Published {signal_type}: {value} {unit}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to publish signal: {e}")
            return False
    
    def publish_raw_message(self, topic: str, message: Dict[str, Any]) -> bool:
        """
        Publish a raw MQTT message to a topic.
        
        Args:
            topic: MQTT topic
            message: Message dictionary
            
        Returns:
            True if published successfully
        """
        try:
            payload = json.dumps(message)
            self.client.publish(topic, payload, qos=1)
            self.logger.debug(f"Published to {topic}: {message}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to publish message: {e}")
            return False
    
    def wait_for_message(self, topic: str, timeout: int = 5) -> Optional[Dict[str, Any]]:
        """
        Wait for a message on a topic.
        
        Args:
            topic: MQTT topic to wait for
            timeout: Timeout in seconds
            
        Returns:
            Message payload or None if timeout
        """
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                if topic in self.received_messages and self.received_messages[topic]:
                    messages = self.received_messages[topic]
                    return messages.pop(0)  # FIFO
                time.sleep(0.1)
            
            self.logger.warning(f"Timeout waiting for message on {topic}")
            return None
        
        except Exception as e:
            self.logger.error(f"Error waiting for message: {e}")
            return None
    
    def wait_for_alert(self, alert_type: str, timeout: int = 5) -> bool:
        """
        Wait for a specific alert.
        
        Args:
            alert_type: Alert type (high_speed, high_temp, etc.)
            timeout: Timeout in seconds
            
        Returns:
            True if alert received
        """
        try:
            topic = self.TOPICS.get(alert_type, f"vehicle/alerts/{alert_type}")
            message = self.wait_for_message(topic, timeout)
            return message is not None
        except Exception as e:
            self.logger.error(f"Error waiting for alert: {e}")
            return False
    
    def get_message_count(self, topic: str) -> int:
        """Get number of messages received on a topic."""
        return len(self.received_messages.get(topic, []))
    
    def clear_messages(self, topic: Optional[str] = None) -> None:
        """Clear received messages."""
        if topic:
            if topic in self.received_messages:
                self.received_messages[topic] = []
        else:
            self.received_messages = {}
    
    def get_broker_status(self) -> Dict[str, Any]:
        """Get MQTT broker connection status."""
        return {
            "connected": self.connected,
            "broker_host": self.broker_host,
            "broker_port": self.broker_port,
            "client_id": self.client_id,
            "message_topics": list(self.received_messages.keys()),
        }
