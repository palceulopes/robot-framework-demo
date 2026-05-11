# Makefile for automotive test framework (Windows cmd-compatible where noted)

# Setup and initialization
setup:
	uv run python setup_project.py

# Run default suites under tests/ (excludes nothing — bonus lives in tests/bonus/)
test:
	uv run robot --pythonpath . tests/

# Bonus suites (CAN / integration demos)
test-smoke:
	uv run robot --pythonpath . tests/bonus/smoke_tests.robot

test-integration:
	uv run robot --pythonpath . tests/bonus/integration_tests.robot

# Main Vehicle + Dispatch + MQTT demo (recommended)
test-demo:
	uv run robot --pythonpath . --listener libraries.automotive_listener --outputdir results tests/network_stack.robot

# Run specific test case (example)
test-speed:
	uv run robot --pythonpath . -t "Verify High Speed Behavior" tests/bonus/smoke_tests.robot

# HTML report output
test-report:
	uv run robot --pythonpath . --outputdir ./results tests/
	@echo Open results/report.html to view report

# Run examples script (optional tutorial snippets)
examples:
	uv run python examples.py

# Clean up generated files
clean:
	@echo Cleaning up test artifacts...
	@if exist results (rmdir /s /q results)
	@if exist logs (rmdir /s /q logs)
	@if exist .robocache (rmdir /s /q .robocache)
	@echo Cleanup complete

# Install / sync (preferred: full project with extras)
install:
	uv sync --extra automotive

install-dev:
	uv sync --extra automotive --extra dev

# Check code quality
lint:
	uv run flake8 libraries/ mock_servers/ --max-line-length=88
	uv run black --check libraries/ mock_servers/

format:
	uv run black libraries/ mock_servers/

# Documentation pointer
docs:
	@echo Automotive Test Framework
	@echo ========================
	@echo See README.md for setup, ports, and demo commands.

# Help
help:
	@echo Automotive Test Framework - Available Commands
	@echo ==============================================
	@echo.
	@echo Setup:
	@echo   make setup              - Run setup verification (uv run python setup_project.py)
	@echo   make install            - uv sync --extra automotive
	@echo   make install-dev        - uv sync with dev extras
	@echo.
	@echo Testing:
	@echo   make test               - All Robot suites under tests/
	@echo   make test-demo          - Vehicle + Dispatch + MQTT (network_stack.robot + listener)
	@echo   make test-smoke         - tests/bonus/smoke_tests.robot
	@echo   make test-integration   - tests/bonus/integration_tests.robot
	@echo   make test-speed         - Example: single test from smoke suite
	@echo   make test-report        - All tests with HTML under results/
	@echo.
	@echo Examples:
	@echo   make examples           - python examples.py via uv
	@echo   make docs               - Points to README.md
	@echo.
	@echo Code quality:
	@echo   make lint               - flake8 + black --check
	@echo   make format             - black
	@echo.
	@echo Maintenance:
	@echo   make clean              - Remove results, logs, .robocache
	@echo.
	@echo Example: make install ^&^& make test-demo
	@echo.

.PHONY: setup test test-demo test-smoke test-integration test-speed test-report examples clean install install-dev lint format docs help
