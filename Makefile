# Makefile — Vehicle Service + MQTT demo

install:
	uv sync --extra automotive

install-dev:
	uv sync --extra automotive --extra dev

test:
	uv run robot -d results tests/network_stack.robot

lint:
	uv run flake8 mock_server.py mqtt_broker.py libraries/automotive_lib.py config.py --max-line-length=88
	uv run black --check mock_server.py mqtt_broker.py libraries/automotive_lib.py config.py

format:
	uv run black mock_server.py mqtt_broker.py libraries/automotive_lib.py config.py

clean:
	rm -rf results output.xml log.html report.html __pycache__

.PHONY: install install-dev test lint format clean
