"""
Configuration module for automotive test framework.

Centralizes global variables, paths, and constants used across the test suite.
"""

from pathlib import Path

# Base project paths (PROJECT_ROOT_STR: use in Robot as ${PROJECT_ROOT_STR}${/}resources/... after Variables import)
PROJECT_ROOT = Path(__file__).parent.parent
DBC_PATH = PROJECT_ROOT / "resources" / "vehicle_signals.dbc"
LOGS_PATH = PROJECT_ROOT / "logs"
PROJECT_ROOT_STR = str(PROJECT_ROOT)

# Vehicle Service — REST mock (mock_servers/vehicle_service_server.py)
VEHICLE_SERVICE_HOST = "127.0.0.1"
VEHICLE_SERVICE_PORT = 8765
VEHICLE_SERVICE_BASE_URL = f"http://{VEHICLE_SERVICE_HOST}:{VEHICLE_SERVICE_PORT}"

# Backwards-compatible aliases (ECU mock == Vehicle Service in this demo)
ECU_REST_HOST = VEHICLE_SERVICE_HOST
ECU_REST_PORT = VEHICLE_SERVICE_PORT
ECU_BASE_URL = VEHICLE_SERVICE_BASE_URL

# Dispatch Service — REST mock (mock_servers/dispatch_rest_server.py)
DISPATCH_SERVICE_HOST = "127.0.0.1"
DISPATCH_SERVICE_PORT = 8766
DISPATCH_BASE_URL = f"http://{DISPATCH_SERVICE_HOST}:{DISPATCH_SERVICE_PORT}"

MQTT_BROKER_HOST = "127.0.0.1" #default host for aMQTT
MQTT_BROKER_PORT = 1883 #default port for aMQTT

# Hardware simulation constants
DEFAULT_DEVICE_ID = "test_device_001"
CAN_CHANNEL = "vcan0"
CAN_INTERFACE = "virtual"

# Speed threshold constants (km/h)
MAX_SPEED_THRESHOLD = 120

# Expected software versions
CLUSTER_VERSION = "1.2.3" #just a placeholder

# Create logs directory if it doesn't exist
LOGS_PATH.mkdir(parents=True, exist_ok=True)

# Export all configuration as dictionary for Robot Framework
CONFIG = {
    "DBC_PATH": str(DBC_PATH),
    "DEFAULT_DEVICE_ID": DEFAULT_DEVICE_ID,
    "CAN_CHANNEL": CAN_CHANNEL,
    "CAN_INTERFACE": CAN_INTERFACE,
    "MAX_SPEED_THRESHOLD": MAX_SPEED_THRESHOLD,
    "CLUSTER_VERSION": CLUSTER_VERSION,
    "ECU_BASE_URL": ECU_BASE_URL,
    "VEHICLE_SERVICE_BASE_URL": VEHICLE_SERVICE_BASE_URL,
    "DISPATCH_BASE_URL": DISPATCH_BASE_URL,
    "MQTT_BROKER_HOST": MQTT_BROKER_HOST,
    "MQTT_BROKER_PORT": MQTT_BROKER_PORT,
}
