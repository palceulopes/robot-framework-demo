# Makefile — Pragmatic Lab Setup

install:
	uv sync --extra automotive

install-dev:
	uv sync --extra automotive --extra dev

# Run the E2E demo suite (starts mock_server.py + MQTT broker automatically)
test:
	uv run robot --pythonpath . --outputdir results tests/network_stack.robot

# Lint Python sources
lint:
	uv run flake8 mock_server.py libraries/automotive_lib.py --max-line-length=88
	uv run black --check mock_server.py libraries/automotive_lib.py

# Auto-format
format:
	uv run black mock_server.py libraries/automotive_lib.py

# Start the unified server manually (for ad-hoc testing)
server:
	uv run python mock_server.py

# Remove generated artifacts
clean:
	rm -rf results output.xml log.html report.html logs __pycache__

help:
	@echo "Pragmatic Lab Setup"
	@echo "==================="
	@echo ""
	@echo "  make install      Install dependencies (uv sync --extra automotive)"
	@echo "  make install-dev  Install with dev extras (flake8, black, pytest)"
	@echo "  make test         Run E2E demo (Robot Framework)"
	@echo "  make lint         flake8 + black --check"
	@echo "  make format       Auto-format with black"
	@echo "  make server       Start mock server manually"
	@echo "  make clean        Remove generated artifacts"

.PHONY: install install-dev test lint format server clean help
