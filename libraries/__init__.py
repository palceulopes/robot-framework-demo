"""
Automotive test framework libraries.

This package contains mock implementations and managers for automotive testing,
including ADB mock for device communication and CAN bus manager for signal injection.
"""

from .automotive_lib import (
    AdbMock,
    CanBusManager,
    AutomotiveLibrary,
    SpeedSignal,
)

__all__ = [
    "AdbMock",
    "CanBusManager",
    "AutomotiveLibrary",
    "SpeedSignal",
]

__version__ = "1.0.0"
