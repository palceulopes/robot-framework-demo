# Makefile equivalent for automotive test framework
# Windows PowerShell usage

# Setup and initialization
setup:
	python setup_project.py

# Run all tests
test:
	robot tests/

# Run specific test suite
test-smoke:
	robot tests/smoke_tests.robot

test-integration:
	robot tests/integration_tests.robot

# Run specific test case
test-speed:
	robot -t "Verify High Speed Behavior" tests/smoke_tests.robot

# Run with detailed reports
test-report:
	robot --outputdir ./results tests/
	@echo Open results/report.html to view report

# Run examples
examples:
	python examples.py

# Quick start menu
quickstart:
	python quickstart.py

# Clean up generated files
clean:
	@echo Cleaning up test artifacts...
	@if exist results (rmdir /s /q results)
	@if exist logs (rmdir /s /q logs)
	@if exist .robocache (rmdir /s /q .robocache)
	@echo Cleanup complete

# Install dependencies
install:
	uv pip install robotframework cantools python-can

install-dev:
	uv pip install robotframework cantools python-can pytest pytest-cov black flake8

# Check code quality
lint:
	flake8 libraries/ --max-line-length=88
	black --check libraries/

format:
	black libraries/

# Documentation
docs:
	@echo Automotive Test Framework Documentation
	@echo ========================================
	@echo.
	@echo Quick Links:
	@echo - README.md - Main documentation
	@echo - QUICKSTART.md - Quick start guide
	@echo - TECHNICAL_DOCUMENTATION.md - Technical details
	@echo - examples.py - Usage examples
	@echo.

# Help
help:
	@echo Automotive Test Framework - Available Commands
	@echo ==============================================
	@echo.
	@echo Setup and Installation:
	@echo   make setup              - Run setup verification
	@echo   make install            - Install dependencies
	@echo   make install-dev        - Install dev dependencies
	@echo.
	@echo Testing:
	@echo   make test               - Run all tests
	@echo   make test-smoke         - Run smoke tests only
	@echo   make test-integration   - Run integration tests only
	@echo   make test-speed         - Run specific speed test
	@echo   make test-report        - Run tests with HTML report
	@echo.
	@echo Examples and Documentation:
	@echo   make examples           - Show usage examples
	@echo   make quickstart         - Interactive quick start menu
	@echo   make docs               - Show documentation links
	@echo.
	@echo Code Quality:
	@echo   make lint               - Check code style
	@echo   make format             - Format code
	@echo.
	@echo Maintenance:
	@echo   make clean              - Clean up generated files
	@echo.
	@echo Example Usage:
	@echo   make setup              - First time setup
	@echo   make test               - Run all tests
	@echo   make test-report        - View HTML report
	@echo.

.PHONY: setup test test-smoke test-integration test-speed test-report examples quickstart clean install install-dev lint format docs help
