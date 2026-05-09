*** Settings ***
Documentation    Integration tests for automotive system.
...              More complex scenarios combining multiple components.

Variables        ../../variables/config.py
Resource         ${PROJECT_ROOT_STR}${/}resources/vehicle_keywords.resource

Suite Setup      Initialize System Mocks
Suite Teardown   Cleanup System Resources


*** Test Cases ***
Complete Speed Profile Test
    [Documentation]    Test complete speed profile from startup to high speed.
    ...                Validates system behavior across speed range.
    [Tags]    integration    speed_profile    critical
    
    # Phase 1: System verification
    Log    Phase 1: System Verification
    Validate Software Version    expected_version=${CLUSTER_VERSION}
    Verify CAN Message Available    WheelSpeed
    Verify CAN Message Available    ClusterAlert
    
    # Phase 2: Idle state
    Log    Phase 2: Idle State
    Inject Speed Signal    0
    Sleep    0.5s
    
    # Phase 3: Gradual acceleration
    Log    Phase 3: Gradual Acceleration (0-60 km/h)
    Simulate Gradual Speed Increase    start_speed=0    end_speed=60    step=10
    
    # Phase 4: Highway speed
    Log    Phase 4: Highway Speed (60-120 km/h)
    Simulate Gradual Speed Increase    start_speed=60    end_speed=120    step=20
    
    # Phase 5: High speed alert
    Log    Phase 5: High Speed Alert
    Inject Speed Signal    ${MAX_SPEED_THRESHOLD}
    Validate High Speed Alert Triggered    threshold_kmh=${MAX_SPEED_THRESHOLD}
    
    # Phase 6: Return to idle
    Log    Phase 6: Return to Idle
    Simulate Gradual Speed Increase    start_speed=120    end_speed=0    step=20
    
    Log    Complete speed profile test passed


System Diagnostics Test
    [Documentation]    Comprehensive system diagnostics.
    ...                Gathers and validates system information.
    [Tags]    integration    diagnostics    information
    
    Log    Starting system diagnostics...
    
    # Get detailed status
    ${status}=    Get System Status Report
    
    # Verify all required fields
    Dictionary Should Contain Key    ${status}    device_model
    Dictionary Should Contain Key    ${status}    device_brand
    Dictionary Should Contain Key    ${status}    android_version
    Dictionary Should Contain Key    ${status}    serial_number
    
    # Validate device properties
    ${model}=    Get Device Property    ro.product.model
    ${brand}=    Get Device Property    ro.product.brand
    
    Should Not Be Empty    ${model}
    Should Not Be Empty    ${brand}
    
    # Verify CAN infrastructure
    ${can_messages}=    Get Can Messages
    Should Not Be Empty    ${can_messages}
    Should Contain    ${can_messages}    WheelSpeed
    Should Contain    ${can_messages}    ClusterAlert
    Should Contain    ${can_messages}    SystemStatus
    
    # Get all signals
    ${wheel_signals}=    Get Can Signals    WheelSpeed
    ${alert_signals}=    Get Can Signals    ClusterAlert
    ${status_signals}=    Get Can Signals    SystemStatus
    
    Should Not Be Empty    ${wheel_signals}
    Should Not Be Empty    ${alert_signals}
    Should Not Be Empty    ${status_signals}
    
    Log    System diagnostics completed successfully
    Log    Device: ${model} by ${brand}
    Log    CAN Messages: ${can_messages}


Multiple Speed Threshold Test
    [Documentation]    Test multiple speed thresholds for alerts.
    ...                Validates alert triggering at different speeds.
    [Tags]    integration    threshold_validation
    
    # Test speed below threshold
    Log    Testing speed below threshold
    ${below_threshold}=    Evaluate    ${MAX_SPEED_THRESHOLD} - 20
    Inject Speed Signal    ${below_threshold}
    Log    Speed ${below_threshold} km/h - no alert expected
    
    # Test speed at threshold
    Log    Testing speed at threshold
    Inject Speed Signal    ${MAX_SPEED_THRESHOLD}
    Validate High Speed Alert Triggered    threshold_kmh=${MAX_SPEED_THRESHOLD}
    
    # Test speed above threshold
    Log    Testing speed above threshold
    ${above_threshold}=    Evaluate    ${MAX_SPEED_THRESHOLD} + 20
    Inject Speed Signal    ${above_threshold}
    Validate High Speed Alert Triggered    threshold_kmh=${MAX_SPEED_THRESHOLD}
    
    # Return to safe speed
    Log    Returning to safe speed
    Inject Speed Signal    50
    
    Log    Multiple threshold test passed


Stress Test: Rapid Speed Changes
    [Documentation]    Stress test with rapid speed changes.
    ...                Verifies system stability under rapid signal injection.
    [Tags]    integration    stress_test    performance
    
    Log    Starting rapid speed change stress test
    
    # Rapid acceleration and braking
    FOR    ${iteration}    IN RANGE    1    11
        Log    Iteration ${iteration}/10
        Inject Speed Signal    0
        Sleep    0.1s
        Inject Speed Signal    150
        Sleep    0.1s
    END
    
    # Return to idle
    Inject Speed Signal    0
    
    Log    Stress test completed - System remained stable


Signal Injection Sequence Test
    [Documentation]    Test sequence of different signals.
    ...                Validates proper signal handling order.
    [Tags]    integration    signal_sequence    order
    
    Log    Testing signal injection sequence
    
    # Sequence 1: Low speed
    Log    Sequence 1: Low speed signals
    Inject Speed Signal    20
    Sleep    ${SPEED_CHANGE_DELAY}
    
    # Sequence 2: Medium speed
    Log    Sequence 2: Medium speed signals
    Inject Speed Signal    60
    Sleep    ${SPEED_CHANGE_DELAY}
    
    # Sequence 3: High speed with alert
    Log    Sequence 3: High speed with alert
    Inject Speed Signal    130
    Validate High Speed Alert Triggered
    Sleep    ${SPEED_CHANGE_DELAY}
    
    # Sequence 4: Back to idle
    Log    Sequence 4: Return to idle
    Inject Speed Signal    0
    Sleep    ${SPEED_CHANGE_DELAY}
    
    Log    Signal injection sequence test passed


*** Keywords ***
Validate All CAN Messages
    [Documentation]    Validate that all expected CAN messages are available.
    [Tags]    validation    can
    
    ${messages}=    Get Can Messages
    Should Contain    ${messages}    WheelSpeed
    Should Contain    ${messages}    ClusterAlert
    Should Contain    ${messages}    SystemStatus
    Log    All CAN messages validated
