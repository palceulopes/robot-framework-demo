"""
Automotive library for Robot Framework test suite.

Provides mock implementations for CAN bus communication and ADB commands,
simulating hardware interactions for vehicle cluster and infotainment testing.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

from robot.api.deco import library

try:
    import cantools
except ImportError:
    cantools = None

try:
    import can
except ImportError:
    can = None

logger = logging.getLogger(__name__)


@dataclass
class SpeedSignal:
    """Data class for speed signal representation."""
    value: float
    unit: str = "km/h"
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class AdbMock:
    """
    Mock implementation of ADB (Android Debug Bridge) commands.
    
    Simulates shell command execution for testing device communication
    without requiring actual hardware or USB connection.
    
    Example:
        adb = AdbMock(device_id="test_device_001")
        version = adb.get_property("ro.build.version.release")
    """
    
    def __init__(self, device_id: str = "test_device_001"):
        """
        Initialize AdbMock with a simulated device.
        
        Args:
            device_id: The virtual device identifier
        """
        self.device_id = device_id
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Simulated device properties
        self._properties = {
            "ro.build.version.release": "13.0",
            "ro.build.version.sdk": "33",
            "ro.product.brand": "TestBrand",
            "ro.product.model": "VirtualCluster",
            "ro.serialno": device_id,
            "ro.build.version.base_os": "",
            "ro.build.fingerprint": "test/virtual/cluster:13/TP1A.220624.014/test:user/release-keys",
        }
        self._shell_commands = {}
        self._init_mock_shell_commands()
        self.logger.debug(f"AdbMock initialized for device: {device_id}")
    
    def _init_mock_shell_commands(self) -> None:
        """Initialize mock responses for common shell commands."""
        self._shell_commands = {
            "pm list packages": "package:com.automotive.cluster\npackage:com.automotive.infotainment\n",
            "settings get secure android_id": "abcd1234efgh5678",
            "dumpsys package com.automotive.cluster": "Package [com.automotive.cluster] (...)",
        }
    
    def get_property(self, property_name: str) -> str:
        """
        Get a device property by name.
        
        Args:
            property_name: The Android property to retrieve
            
        Returns:
            The property value as a string
            
        Raises:
            KeyError: If property is not found
        """
        try:
            value = self._properties.get(property_name, "")
            self.logger.debug(f"getprop {property_name} => {value}")
            return value
        except Exception as e:
            self.logger.error(f"Failed to get property {property_name}: {e}")
            raise
    
    def shell_command(self, command: str) -> str:
        """
        Execute a simulated shell command.
        
        Args:
            command: The shell command to execute
            
        Returns:
            The command output as a string
        """
        try:
            output = self._shell_commands.get(command, f"Mock response for: {command}\n")
            self.logger.debug(f"shell: {command}")
            return output
        except Exception as e:
            self.logger.error(f"Failed to execute shell command '{command}': {e}")
            raise
    
    def set_property(self, property_name: str, value: str) -> bool:
        """
        Set a device property (mock only, no actual effect).
        
        Args:
            property_name: The property to set
            value: The value to set
            
        Returns:
            True if successful
        """
        try:
            self._properties[property_name] = value
            self.logger.debug(f"setprop {property_name} {value}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to set property {property_name}: {e}")
            return False


class CanBusManager:
    """
    Manager for CAN bus communication using cantools and python-can.
    
    Handles DBC file loading, signal injection, and CAN message reception
    in a virtual environment for testing purposes.
    
    Attributes:
        dbc_path: Path to the DBC file
        channel: Virtual CAN channel name (e.g., 'vcan0')
        interface: CAN interface type (default: 'virtual')
        bus: The python-can Bus instance
        database: The cantools database instance
    """
    
    def __init__(
        self,
        dbc_path: str,
        channel: str = "vcan0",
        interface: str = "virtual",
        bitrate: int = 500000,
    ):
        """
        Initialize the CAN Bus Manager.
        
        Args:
            dbc_path: Path to the DBC file
            channel: CAN channel name
            interface: CAN interface type
            bitrate: CAN bitrate in bits/second
            
        Raises:
            FileNotFoundError: If DBC file does not exist
            RuntimeError: If CAN bus initialization fails
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.dbc_path = Path(dbc_path)
        self.channel = channel
        self.interface = interface
        self.bitrate = bitrate
        
        self.database: Optional[Any] = None
        self.bus: Optional[Any] = None
        self._signal_cache: Dict[str, Any] = {}
        
        self._validate_dbc_file()
        self._load_database()
        self._init_bus()
        self.logger.info(
            f"CanBusManager initialized: {channel} on {interface} interface"
        )
    
    def _validate_dbc_file(self) -> None:
        """
        Validate that the DBC file exists.
        
        Raises:
            FileNotFoundError: If DBC file does not exist
        """
        if not self.dbc_path.exists():
            raise FileNotFoundError(f"DBC file not found: {self.dbc_path}")
        self.logger.debug(f"DBC file validated: {self.dbc_path}")
    
    def _load_database(self) -> None:
        """
        Load the CAN database from DBC file.
        
        Raises:
            RuntimeError: If cantools is not installed or file parsing fails
        """
        if cantools is None:
            raise RuntimeError("cantools is not installed. Install with: pip install cantools")
        
        try:
            self.database = cantools.database.load_file(str(self.dbc_path))
            message_count = len(self.database.messages)
            self.logger.info(f"DBC database loaded: {message_count} messages")
        except Exception as e:
            self.logger.error(f"Failed to load DBC file: {e}")
            raise RuntimeError(f"Failed to load DBC database: {e}")
    
    def _init_bus(self) -> None:
        """
        Initialize the virtual CAN bus.
        
        Raises:
            RuntimeError: If python-can is not installed or bus initialization fails
        """
        if can is None:
            self.logger.warning(
                "python-can not installed. CAN bus will be mocked. "
                "Install with: pip install python-can"
            )
            self.bus = MagicMock()
            return
        
        try:
            self.bus = can.interface.Bus(
                channel=self.channel,
                interface=self.interface,
                bitrate=self.bitrate,
            )
            self.logger.info(f"CAN bus initialized on {self.channel}")
        except Exception as e:
            self.logger.warning(f"Failed to initialize real CAN bus: {e}. Using mock.")
            self.bus = MagicMock()
    
    def send_signal(
        self,
        message_name: str,
        signal_name: str,
        value: float,
        multiplier: float = 1.0,
    ) -> bool:
        """
        Send a signal on the CAN bus.
        
        Args:
            message_name: Name of the CAN message
            signal_name: Name of the signal within the message
            value: The value to send
            multiplier: Optional signal multiplier for scaling
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.database is None:
                self.logger.error("Database not loaded")
                return False
            
            message = self.database.get_message_by_name(message_name)
            # cantools requires values for all signals in the frame for encoding
            phys: Dict[str, float] = {sig.name: 0.0 for sig in message.signals}
            phys[signal_name] = float(value) * multiplier

            encoded_data = message.encode(phys)
            
            if can is not None and self.bus is not None:
                msg = can.Message(
                    arbitration_id=message.frame_id,
                    data=encoded_data,
                    is_extended_id=message.is_extended_frame,
                )
                self.bus.send(msg)
            
            self.logger.debug(
                f"Signal sent: {message_name}.{signal_name} = {value * multiplier}"
            )
            self._signal_cache[f"{message_name}.{signal_name}"] = value
            return True
            
        except Exception as e:
            self.logger.error(
                f"Failed to send signal {message_name}.{signal_name}: {e}"
            )
            return False
    
    def inject_speed_signal(self, speed_km_h: float) -> bool:
        """
        Inject a speed signal into the CAN bus.
        
        Args:
            speed_km_h: Speed value in km/h
            
        Returns:
            True if successful
        """
        try:
            return self.send_signal(
                message_name="WheelSpeed",
                signal_name="Speed",
                value=speed_km_h,
            )
        except Exception as e:
            self.logger.error(f"Failed to inject speed signal: {e}")
            return False
    
    def get_message_names(self) -> List[str]:
        """
        Get list of all message names in the database.
        
        Returns:
            List of message names
        """
        if self.database is None:
            return []
        return [msg.name for msg in self.database.messages]
    
    def get_message_signals(self, message_name: str) -> List[str]:
        """
        Get list of signal names for a specific message.
        
        Args:
            message_name: Name of the CAN message
            
        Returns:
            List of signal names
        """
        try:
            if self.database is None:
                return []
            message = self.database.get_message_by_name(message_name)
            return [signal.name for signal in message.signals]
        except Exception as e:
            self.logger.error(f"Failed to get signals for message {message_name}: {e}")
            return []
    
    def close(self) -> None:
        """Close the CAN bus connection."""
        try:
            if self.bus is not None and hasattr(self.bus, 'shutdown'):
                self.bus.shutdown()
                self.logger.info("CAN bus closed")
        except Exception as e:
            self.logger.error(f"Error closing CAN bus: {e}")


@library(scope="SUITE", version="1.0.0", auto_keywords=True)
class AutomotiveLibrary:
    """
    Main automotive library for Robot Framework.
    
    Integrates ADB mock and CAN bus manager for comprehensive vehicle system testing.
    This library is designed to be extensible for future integration with real hardware.
    """

    def __init__(self, dbc_path: str = None, device_id: str = "test_device_001"):
        """
        Initialize the Automotive Library.
        
        Args:
            dbc_path: Path to the DBC file
            device_id: Virtual device identifier
        """
        self.logger = logging.getLogger(__name__)
        self.adb_mock = AdbMock(device_id=device_id)
        
        # Initialize CAN manager with provided or default DBC path
        if dbc_path is None:
            from variables.config import DBC_PATH
            dbc_path = str(DBC_PATH)
        
        try:
            self.can_manager = CanBusManager(dbc_path=dbc_path)
        except Exception as e:
            self.logger.warning(f"CAN manager initialization failed: {e}")
            self.can_manager = None
    
    def get_device_property(self, property_name: str) -> str:
        """
        Get a device property (Robot Framework keyword).
        
        Args:
            property_name: The property to retrieve
            
        Returns:
            The property value
        """
        return self.adb_mock.get_property(property_name)
    
    def execute_shell_command(self, command: str) -> str:
        """
        Execute a shell command on the mock device.
        
        Args:
            command: The command to execute
            
        Returns:
            Command output
        """
        return self.adb_mock.shell_command(command)
    
    def inject_speed_kmh(self, speed: float) -> bool:
        """
        Inject a speed signal in km/h.
        
        Args:
            speed: Speed value in km/h
            
        Returns:
            True if successful
        """
        if self.can_manager is None:
            self.logger.error("CAN manager not initialized")
            return False
        return self.can_manager.inject_speed_signal(speed)
    
    def get_can_messages(self) -> List[str]:
        """Get list of available CAN messages."""
        if self.can_manager is None:
            return []
        return self.can_manager.get_message_names()
    
    def get_can_signals(self, message_name: str) -> List[str]:
        """Get signals for a specific CAN message."""
        if self.can_manager is None:
            return []
        return self.can_manager.get_message_signals(message_name)
    
    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.can_manager:
            self.can_manager.close()
