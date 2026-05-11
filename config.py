"""
Single source of truth for all project constants.

Change a port, host, or topic here — every other file imports from this module.
Robot Framework picks up these module-level variables automatically via:
    Variables    config
"""

from pathlib import Path

# ── Paths ───────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent
PROJECT_ROOT_STR = str(PROJECT_ROOT)
DBC_PATH = PROJECT_ROOT / "resources" / "vehicle_signals.dbc"

# ── Flask (unified mock server) ─────────────────────────────────

FLASK_HOST = "127.0.0.1"
FLASK_PORT = 8080
BASE_URL = f"http://{FLASK_HOST}:{FLASK_PORT}"

# ── MQTT broker (embedded aMQTT) ────────────────────────────────

MQTT_HOST = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC_TEMPLATE = "vehicle/{vehicle_id}/commands"

# ── Test defaults ────────────────────────────────────────────────

TIMEOUT = 10
DEFAULT_VEHICLE_ID = "vehicle_42"
