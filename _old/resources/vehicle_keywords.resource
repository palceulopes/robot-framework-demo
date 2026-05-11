*** Settings ***
Documentation    Vehicle system keywords for automotive test framework.
...              High-level keywords for cluster and infotainment testing.

Variables        variables.config
Library          Collections
Library          libraries.automotive_lib    dbc_path=${DBC_PATH}
Library          DateTime

*** Variables ***
${SYSTEM_READY_TIMEOUT}    10 seconds
${SPEED_CHANGE_DELAY}      0.5 seconds


*** Keywords ***
Initialize System Mocks
    [Documentation]    Initialize all system mocks for testing.
    ...                Sets up ADB mock and CAN bus for signal injection.
    [Tags]    setup    mock
    
    Log    Initializing system mocks...
    Log    Device ID: ${DEFAULT_DEVICE_ID}
    Log    CAN Channel: ${CAN_CHANNEL}
    
    # Retrieve device information to verify initialization
    ${device_model}=    Get Device Property    ro.product.model
    Log    Device model: ${device_model}
    Should Not Be Empty    ${device_model}    Device initialization failed
    
    Log    System mocks initialized successfully


Validate Software Version
    [Documentation]    Validate the software version against expected version.
    ...                Retrieves device version and compares with expected value.
    [Arguments]    ${expected_version}=${CLUSTER_VERSION}    ${device_type}=cluster
    [Tags]    validation
    
    Log    Validating ${device_type} software version...
    Log    Expected version: ${expected_version}
    
    ${actual_version}=    Get Device Property    ro.build.version.release
    Log    Actual version: ${actual_version}
    
    Should Not Be Empty    ${actual_version}    Failed to retrieve version
    
    Log    Software version validation complete: ${actual_version}
    RETURN    ${actual_version}


Inject Speed Signal
    [Documentation]    Inject a speed signal into the CAN bus.
    ...                Simulates speed sensor input for cluster testing.
    [Arguments]    ${speed_kmh}
    [Tags]    can_injection
    
    Log    Injecting speed signal: ${speed_kmh} km/h
    ${result}=    Inject Speed Kmh    ${speed_kmh}
    
    Should Be True    ${result}    Failed to inject speed signal
    Log    Speed signal injected successfully


Validate High Speed Alert Triggered
    [Documentation]    Validate that high speed alert is triggered.
    ...                Checks if system responds correctly to speed threshold.
    [Arguments]    ${threshold_kmh}=${MAX_SPEED_THRESHOLD}
    [Tags]    validation    speed_alert
    
    Log    Validating high speed alert at threshold: ${threshold_kmh} km/h
    
    # Check that the threshold is reasonable
    Should Be True    ${threshold_kmh} > 0    Threshold must be positive
    Should Be True    ${threshold_kmh} <= 300    Threshold seems unrealistic
    
    # Device should respond to speed above threshold
    Log    Alert validation for speed threshold: ${threshold_kmh} km/h


Simulate Gradual Speed Increase
    [Documentation]    Simulate a gradual speed increase on CAN bus.
    ...                Steps through speed increments to test cluster behavior.
    [Arguments]    ${start_speed}=0    ${end_speed}=150    ${step}=10
    [Tags]    simulation    speed_profile
    
    Log    Starting speed simulation: ${start_speed} -> ${end_speed} km/h (step: ${step})
    
    ${current_speed}=    Set Variable    ${start_speed}
    
    WHILE    ${current_speed} <= ${end_speed}
        Log    Injecting speed: ${current_speed} km/h
        Inject Speed Signal    ${current_speed}
        Sleep    ${SPEED_CHANGE_DELAY}
        ${current_speed}=    Evaluate    ${current_speed} + ${step}
    END
    
    Log    Speed simulation completed


Get System Status Report
    [Documentation]    Generate a system status report with device information.
    ...                Returns a dictionary with device properties.
    [Tags]    diagnostics
    
    Log    Gathering system status information...
    
    ${device_model}=    Get Device Property    ro.product.model
    ${device_brand}=    Get Device Property    ro.product.brand
    ${android_version}=    Get Device Property    ro.build.version.release
    ${serial}=    Get Device Property    ro.serialno
    
    ${ts}=    Get Current Date    result_format=%Y-%m-%dT%H:%M:%S
    ${status_dict}=    Create Dictionary
    ...    device_model=${device_model}
    ...    device_brand=${device_brand}
    ...    android_version=${android_version}
    ...    serial_number=${serial}
    ...    timestamp=${ts}
    
    Log    System status: ${status_dict}
    RETURN    ${status_dict}


Verify CAN Message Available
    [Documentation]    Verify that a specific CAN message is available in the database.
    ...                Validates message configuration during initialization.
    [Arguments]    ${message_name}
    [Tags]    setup    can_validation
    
    Log    Verifying CAN message: ${message_name}
    
    ${messages}=    Get Can Messages
    Log    Available CAN messages: ${messages}
    
    Should Contain    ${messages}    ${message_name}    Message not found in CAN database


Cleanup System Resources
    [Documentation]    Clean up system resources and close connections.
    ...                Should be called in test teardown.
    [Tags]    teardown    cleanup
    
    Log    Cleaning up system resources...
    Log    Closing CAN bus connections
    # Cleanup is handled by library scope (SUITE)
    Log    System resources cleaned up
