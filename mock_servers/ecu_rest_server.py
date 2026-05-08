"""
Standalone mock ECU REST API for local testing (Flask).

Pairs with libraries.rest_ecu_api.RestEcuApi — same routes and JSON shapes.

Usage:
  uv run python mock_servers/ecu_rest_server.py --host 127.0.0.1 --port 8765
"""

from __future__ import annotations

import argparse
import logging
import time
from typing import Any, Dict

try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS
except ImportError as e:
    raise SystemExit(
        "Flask and flask-cors are required. Install automotive extras: uv sync --extra automotive"
    ) from e

logger = logging.getLogger(__name__)


def create_app(initial: Dict[str, Any] | None = None) -> Flask:
    """Create Flask app with in-memory ECU state."""
    state: Dict[str, Any] = {
        "speed": 0.0,
        "rpm": 800.0,
        "temperature": 90.0,
        "fuel_level": 72.5,
        "voltage": 12.6,
        "errors": [],
        "version": "1.2.3-mock",
        "status": "RUNNING",
    }
    if initial:
        state.update(initial)

    started = time.time()
    app = Flask(__name__)
    CORS(app)

    @app.get("/api/health")
    def health() -> Any:
        return jsonify({"status": "ok", "ts": time.time()})

    @app.get("/api/signals/<name>")
    def signal(name: str) -> Any:
        key = name.lower().replace("-", "_")
        if key == "fuel":
            key = "fuel_level"
        allowed = ("speed", "rpm", "temperature", "fuel_level")
        if key not in allowed:
            return jsonify({"error": "unknown_signal", "signal": name}), 404
        return jsonify({"value": state[key], "unit": _unit_for(key), "signal": key})

    @app.get("/api/diagnostics/voltage")
    def voltage() -> Any:
        return jsonify({"value": state["voltage"], "unit": "V"})

    @app.get("/api/diagnostics/errors")
    def errors() -> Any:
        return jsonify({"errors": list(state["errors"]), "count": len(state["errors"])})

    @app.get("/api/system/version")
    def version() -> Any:
        return jsonify({"version": state["version"]})

    @app.get("/api/system/status")
    def status() -> Any:
        return jsonify(
            {
                "status": state["status"],
                "uptime_s": time.time() - started,
            }
        )

    @app.post("/api/config/<parameter>")
    def set_config(parameter: str) -> Any:
        body = request.get_json(force=True, silent=True) or {}
        val = body.get("value")
        state[f"cfg_{parameter}"] = val
        return jsonify({"ok": True, "parameter": parameter, "value": val})

    @app.post("/api/commands/<command>")
    def command(command: str) -> Any:
        body = request.get_json(force=True, silent=True) or {}
        return jsonify({"ok": True, "command": command, "args": body})

    return app


def _unit_for(key: str) -> str:
    return {
        "speed": "km/h",
        "rpm": "rpm",
        "temperature": "°C",
        "fuel_level": "%",
    }.get(key, "")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    p = argparse.ArgumentParser(description="Mock ECU REST server")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--debug", action="store_true")
    args = p.parse_args()

    app = create_app()
    logger.info("Mock ECU REST listening on http://%s:%s", args.host, args.port)
    app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)


if __name__ == "__main__":
    main()
