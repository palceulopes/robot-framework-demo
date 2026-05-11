"""
Examples of using the automotive test framework.

Demonstrates common patterns for testing vehicle systems.
"""

from libraries.automotive_lib import AdbMock, CanBusManager, AutomotiveLibrary
from variables.config import DBC_PATH, DEFAULT_DEVICE_ID, MAX_SPEED_THRESHOLD


def example_adb_mock():
    """Example: Using ADB Mock to retrieve device properties."""
    print("\n" + "="*60)
    print("EXAMPLE 1: ADB Mock - Device Properties")
    print("="*60)
    
    # Create ADB mock instance
    adb = AdbMock(device_id=DEFAULT_DEVICE_ID)
    
    # Get device properties
    model = adb.get_property("ro.product.model")
    brand = adb.get_property("ro.product.brand")
    version = adb.get_property("ro.build.version.release")
    serial = adb.get_property("ro.serialno")
    
    print(f"\nDevice Information:")
    print(f"  Model:   {model}")
    print(f"  Brand:   {brand}")
    print(f"  Version: {version}")
    print(f"  Serial:  {serial}")
    
    # Execute shell command
    output = adb.shell_command("pm list packages")
    print(f"\nShell Command Output:\n{output[:100]}...")
    
    # Set property (mock only)
    success = adb.set_property("test.property", "test_value")
    print(f"\nProperty Set Success: {success}")


def example_can_bus_manager():
    """Example: Using CAN Bus Manager to send signals."""
    print("\n" + "="*60)
    print("EXAMPLE 2: CAN Bus Manager - Signal Injection")
    print("="*60)
    
    try:
        # Create CAN manager
        can_mgr = CanBusManager(dbc_path=str(DBC_PATH))
        
        # Get available messages
        messages = can_mgr.get_message_names()
        print(f"\nAvailable CAN Messages:")
        for msg in messages:
            print(f"  - {msg}")
        
        # Get signals for WheelSpeed message
        signals = can_mgr.get_message_signals("WheelSpeed")
        print(f"\nSignals in WheelSpeed message:")
        for signal in signals:
            print(f"  - {signal}")
        
        # Inject speed signal
        print(f"\nInjecting speed signals:")
        for speed in [0, 50, 100, 120, 150]:
            result = can_mgr.inject_speed_signal(speed)
            status = "✓" if result else "✗"
            print(f"  {status} Speed: {speed} km/h")
        
        # Close CAN bus
        can_mgr.close()
        print("\nCAN bus closed successfully")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("Note: This example requires cantools and python-can installed")


def example_automotive_library():
    """Example: Using the main AutomotiveLibrary."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Automotive Library - Integrated Usage")
    print("="*60)
    
    try:
        # Create library instance
        lib = AutomotiveLibrary(
            dbc_path=str(DBC_PATH),
            device_id=DEFAULT_DEVICE_ID
        )
        
        # Get device property
        version = lib.get_device_property("ro.build.version.release")
        print(f"\nDevice Version: {version}")
        
        # Get available CAN messages
        messages = lib.get_can_messages()
        print(f"\nAvailable CAN Messages: {messages}")
        
        # Simulate speed increase
        print(f"\nSimulating speed profile:")
        for speed in range(0, 160, 40):
            success = lib.inject_speed_kmh(speed)
            status = "✓" if success else "✗"
            print(f"  {status} Injected {speed} km/h")
        
        # Cleanup
        lib.cleanup()
        print("\nLibrary cleaned up")
        
    except Exception as e:
        print(f"\nError: {e}")


def example_robot_framework_usage():
    """Example: How to use from Robot Framework."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Robot Framework Integration")
    print("="*60)
    
    print("""
In Robot Framework test file (smoke_tests.robot):

*** Settings ***
Resource         resources/vehicle_keywords.resource
Library          libraries.automotive_lib

Suite Setup      Initialize System Mocks
Suite Teardown   Cleanup System Resources

*** Test Cases ***
Verify High Speed Behavior
    [Documentation]    Verify system responds to high speed
    [Tags]    smoke    critical
    
    # Setup
    Validate Software Version    expected_version=1.2.3
    Verify CAN Message Available    WheelSpeed
    
    # Execute
    Inject Speed Signal    120
    
    # Validate
    Validate High Speed Alert Triggered    threshold_kmh=120
    
    Log    Test passed!

*** Keywords ***
(Keywords are defined in vehicle_keywords.resource)
""")


def example_extend_can_signals():
    """Example: How to extend CAN signals in DBC."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Extending CAN Signals")
    print("="*60)
    
    print("""
To add a new signal to vehicle_signals.dbc:

1. Define new message in DBC:

BO_ 103 EngineStatus: 8 Engine
 SG_ EngineRPM : 0|16@1+ (0.25,0) [0|16383.75] "RPM" Cluster
 SG_ EngineTemperature : 16|8@1+ (1,-40) [-40|215] "°C" Cluster,Infotainment
 SG_ FuelLevel : 24|8@1+ (0.5,0) [0|100] "%" Cluster

2. Use in Python code:

can_mgr = CanBusManager("path/to/vehicle_signals.dbc")

# Send RPM signal
can_mgr.send_signal("EngineStatus", "EngineRPM", 3000)

# Send temperature signal
can_mgr.send_signal("EngineStatus", "EngineTemperature", 85)

# Send fuel level
can_mgr.send_signal("EngineStatus", "FuelLevel", 50)

3. Create new keyword in Robot Framework:

Simulate Engine Start
    [Documentation]    Simulate engine startup sequence
    [Arguments]    ${target_rpm}=1000
    
    ${rpm}=    Set Variable    0
    While    ${rpm} < ${target_rpm}
        Inject Engine RPM    ${rpm}
        ${rpm}=    Evaluate    ${rpm} + 200
        Sleep    0.1s
    End While
""")


def example_error_handling():
    """Example: Error handling patterns."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Error Handling Patterns")
    print("="*60)
    
    print("""
1. File not found error:

from libraries.automotive_lib import CanBusManager

try:
    can_mgr = CanBusManager("invalid/path/file.dbc")
except FileNotFoundError as e:
    logger.error(f"DBC file not found: {e}")

2. Signal injection error:

try:
    result = can_mgr.send_signal("WheelSpeed", "Speed", 200)
    if not result:
        logger.warning("Failed to send signal")
except Exception as e:
    logger.error(f"CAN error: {e}")

3. Robot Framework error handling:

Inject Speed With Retry
    [Documentation]    Retry signal injection on failure
    [Arguments]    ${speed}    ${max_retries}=3
    
    ${retry}=    Set Variable    0
    
    While    ${retry} < ${max_retries}
        TRY
            Inject Speed Signal    ${speed}
            BREAK
        EXCEPT
            ${retry}=    Evaluate    ${retry} + 1
            Log    Retry ${retry}/${max_retries}
            Sleep    0.5s
        END
    End While
""")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print(" AUTOMOTIVE TEST FRAMEWORK - USAGE EXAMPLES ".center(70, "="))
    print("="*70)
    
    example_adb_mock()
    example_can_bus_manager()
    example_automotive_library()
    example_robot_framework_usage()
    example_extend_can_signals()
    example_error_handling()
    
    print("\n" + "="*70)
    print("For more examples and documentation, see:")
    print("  - README.md")
    print("  - TECHNICAL_DOCUMENTATION.md")
    print("  - tests/smoke_tests.robot")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
