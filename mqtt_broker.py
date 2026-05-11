"""Embedded MQTT broker — no Mosquitto install required."""

import asyncio
from amqtt.broker import Broker
import config


async def main():
    broker = Broker()
    await broker.start()
    print(f"MQTT broker running on {config.MQTT_HOST}:{config.MQTT_PORT}")
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
