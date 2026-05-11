"""Vehicle Service — simple Flask REST API."""

from flask import Flask, request
import config

app = Flask(__name__)


@app.get("/api/vehicle/status")
def vehicle_status():
    return {
        "speed": 0,
        "rpm": 800,
        "temperature": 90,
        "status": "RUNNING",
    }


@app.post("/api/v1/jobs")
def create_job():
    data = request.get_json(force=True, silent=True) or {}
    return {
        "job_id": "abc-123",
        "vehicle_id": data.get("vehicle_id", "unknown"),
        "command": data.get("command", "noop"),
    }, 201


if __name__ == "__main__":
    app.run(port=config.FLASK_PORT)
