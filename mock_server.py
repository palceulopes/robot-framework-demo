"""Vehicle Service — Flask REST API."""

from flask import Flask
import config

app = Flask(__name__)


@app.get("/api/vehicle/speed")
def vehicle_speed():
    return {"speed": 100}


if __name__ == "__main__":
    app.run(port=config.FLASK_PORT)
