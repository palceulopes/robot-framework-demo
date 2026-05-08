"""
Configuration module for automotive test framework.

Centralizes global variables, paths, and constants used across the test suite.
"""

import os
from pathlib import Path

# Base project paths
PROJECT_ROOT = Path(__file__).parent.parent
DBC_PATH = PROJECT_ROOT / "resources" / "vehicle_signals.dbc"
LOGS_PATH = PROJECT_ROOT / "logs"
PROJECT_ROOT_STR = str(PROJECT_ROOT)
MOCK_SERVERS_DIR = str(PROJECT_ROOT / "mock_servers")

# Mock ECU REST (mock_servers/ecu_rest_server.py) and MQTT (mock_servers/mqtt_broker_helper.py or amqtt CLI)
ECU_REST_HOST = "127.0.0.1"
ECU_REST_PORT = 8765
ECU_BASE_URL = f"http://{ECU_REST_HOST}:{ECU_REST_PORT}"

MQTT_BROKER_HOST = "127.0.0.1"
MQTT_BROKER_PORT = 1883

# Hardware simulation constants
DEFAULT_DEVICE_ID = "test_device_001"
CAN_CHANNEL = "vcan0"
CAN_INTERFACE = "virtual"
CAN_BITRATE = 500000

# Speed threshold constants (km/h)
MAX_SPEED_THRESHOLD = 120
SPEED_ALERT_THRESHOLD = 100

# Simulation parameters
CAN_MESSAGE_TIMEOUT = 5.0  # seconds
SPEED_SIMULATION_STEP = 10  # km/h per increment

# Expected software versions
CLUSTER_VERSION = "1.2.3"
INFOTAINMENT_VERSION = "2.1.0"

# Logging configuration
LOG_LEVEL = "DEBUG"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Create logs directory if it doesn't exist
LOGS_PATH.mkdir(parents=True, exist_ok=True)

# Export all configuration as dictionary for Robot Framework
CONFIG = {
    "DBC_PATH": str(DBC_PATH),
    "DEFAULT_DEVICE_ID": DEFAULT_DEVICE_ID,
    "CAN_CHANNEL": CAN_CHANNEL,
    "CAN_INTERFACE": CAN_INTERFACE,
    "MAX_SPEED_THRESHOLD": MAX_SPEED_THRESHOLD,
    "SPEED_ALERT_THRESHOLD": SPEED_ALERT_THRESHOLD,
    "CLUSTER_VERSION": CLUSTER_VERSION,
    "INFOTAINMENT_VERSION": INFOTAINMENT_VERSION,
    "ECU_BASE_URL": ECU_BASE_URL,
    "MQTT_BROKER_HOST": MQTT_BROKER_HOST,
    "MQTT_BROKER_PORT": MQTT_BROKER_PORT,
}
