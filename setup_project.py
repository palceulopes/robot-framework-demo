"""
Setup script for automotive test framework.

Initialize project structure and verify dependencies.
"""

import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_python_version():
    """Verify Python 3.12+ is installed."""
    if sys.version_info < (3, 12):
        logger.error(f"Python 3.12+ required. Current: {sys.version}")
        sys.exit(1)
    logger.info(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")


def check_dependencies():
    """Check if required packages are installed."""
    required = {
        "robot": "robotframework",
        "cantools": "cantools",
        "can": "python-can",
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
            logger.info(f"✓ {package}")
        except ImportError:
            missing.append(package)
            logger.warning(f"✗ {package} not found")
    
    if missing:
        logger.error(f"\nMissing packages: {', '.join(missing)}")
        logger.info("Install with: uv pip install " + " ".join(missing))
        return False
    
    return True


def verify_project_structure():
    """Verify project directories exist."""
    required_dirs = [
        "libraries",
        "resources",
        "tests",
    ]
    
    project_root = Path(__file__).parent
    for directory in required_dirs:
        dir_path = project_root / directory
        if dir_path.exists():
            logger.info(f"✓ Directory: {directory}")
        else:
            logger.warning(f"✗ Directory missing: {directory}")
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"  Created: {directory}")


def verify_files():
    """Verify critical files exist."""
    required_files = {
        "config.py": "Centralized configuration",
        "mock_server.py": "Unified mock server (Flask + MQTT)",
        "libraries/automotive_lib.py": "Automotive library (REST + MQTT)",
        "tests/network_stack.robot": "E2E demo suite",
    }
    
    project_root = Path(__file__).parent
    for file_path, description in required_files.items():
        full_path = project_root / file_path
        if full_path.exists():
            logger.info(f"✓ {description}: {file_path}")
        else:
            logger.warning(f"✗ {description} missing: {file_path}")


def create_logs_directory():
    """Create logs directory if it doesn't exist."""
    logs_dir = Path(__file__).parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    logger.info(f"✓ Logs directory: logs/")


def print_next_steps():
    """Print instructions for running tests."""
    print("\n" + "="*60)
    print("AUTOMOTIVE TEST FRAMEWORK - SETUP COMPLETE")
    print("="*60)
    print("\nNext steps (demo-ready):")
    print("1. Install demo dependencies:")
    print("   uv sync --extra automotive")
    print("\n2. Run the E2E demo suite:")
    print("   uv run robot --pythonpath . --outputdir results tests/network_stack.robot")
    print("\nFor more information, see README.md")
    print("="*60 + "\n")


def main():
    """Execute setup checks."""
    logger.info("Initializing automotive test framework...\n")
    
    check_python_version()
    check_dependencies()
    verify_project_structure()
    verify_files()
    create_logs_directory()
    
    logger.info("\n✓ Setup verification complete!")
    print_next_steps()


if __name__ == "__main__":
    main()
