"""
Embedded MQTT broker (aMQTT) — no Mosquitto binary required.

Default listen: 0.0.0.0:1883. For custom bind/port use the `amqtt -c config.yml` CLI.

Usage:
  uv run python mock_servers/mqtt_broker_helper.py

Stop with Ctrl+C.
"""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
from asyncio import CancelledError

try:
    from amqtt.broker import Broker
except ImportError as e:
    raise SystemExit(
        "amqtt is required for the embedded broker. Install: uv sync --extra automotive"
    ) from e


def _run_async_main() -> None:
    formatter = "[%(asctime)s] %(levelname)s %(name)s %(message)s"
    logging.basicConfig(level=logging.INFO, format=formatter)

    async def run_server() -> None:
        broker = Broker()
        await broker.start()
        logging.info("Embedded MQTT broker running (Ctrl+C to stop)")
        try:
            while True:
                await asyncio.sleep(3600)
        except CancelledError:
            raise
        finally:
            await broker.shutdown()

    asyncio.run(run_server())


def main() -> None:
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))

    try:
        _run_async_main()
    except KeyboardInterrupt:
        print("Broker stopped.")


if __name__ == "__main__":
    main()
