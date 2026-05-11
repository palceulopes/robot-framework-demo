*** Settings ***
Documentation    Smoke tests for automotive cluster and infotainment system.
...              Validates core functionality of vehicle signal handling and alerts.

Variables        variables.config
Resource         ${PROJECT_ROOT_STR}${/}resources/vehicle_keywords.resource

Suite Setup      Initialize System Mocks
Suite Teardown   Cleanup System Resources


*** Test Cases ***
Verify High Speed Behavior
    [Documentation]    Verify system responds correctly to high speed signals.
    ...                Injects 120 km/h speed signal and validates cluster behavior.
    [Tags]    smoke    critical    speed_validation
    
    # Setup: Validate system is operational
    Validate Software Version    expected_version=${CLUSTER_VERSION}
    
    # Verify CAN infrastructure is available
    Verify CAN Message Available    WheelSpeed
    
    # Test: Inject high speed signal
    Inject Speed Signal    120
    
    # Validation: Verify high speed alert is triggered
    Validate High Speed Alert Triggered    threshold_kmh=${MAX_SPEED_THRESHOLD}
    
    Log    Test passed: High speed behavior validated


Verify Speed Simulation Profile
    [Documentation]    Verify gradual speed increase and cluster response.
    ...                Simulates realistic speed profile from idle to highway speeds.
    [Tags]    smoke    speed_profile    simulation
    
    # Setup
    Validate Software Version    expected_version=${CLUSTER_VERSION}
    Verify CAN Message Available    WheelSpeed
    
    # Test: Simulate gradual speed increase
    Simulate Gradual Speed Increase    start_speed=0    end_speed=140    step=20
    
    # Validation
    Log    Speed profile simulation completed successfully


Verify Device Properties
    [Documentation]    Verify basic device properties are accessible.
    ...                Validates ADB mock functionality.
    [Tags]    smoke    device_validation
    
    # Retrieve and validate device properties
    ${model}=    Get Device Property    ro.product.model
    ${brand}=    Get Device Property    ro.product.brand
    ${version}=    Get Device Property    ro.build.version.release
    
    Should Not Be Empty    ${model}    Device model not found
    Should Not Be Empty    ${brand}    Device brand not found
    Should Not Be Empty    ${version}    Android version not found
    
    Log    Device properties validated: ${model} by ${brand} (Android ${version})


Verify System Status Report
    [Documentation]    Verify system can generate comprehensive status report.
    ...                Validates diagnostic information gathering.
    [Tags]    diagnostics    informational
    
    # Generate status report
    ${status}=    Get System Status Report
    
    # Validate report structure
    Dictionary Should Contain Key    ${status}    device_model
    Dictionary Should Contain Key    ${status}    device_brand
    Dictionary Should Contain Key    ${status}    android_version
    Dictionary Should Contain Key    ${status}    serial_number
    
    Log    System status report: ${status}
