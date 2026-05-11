*** Settings ***
Documentation    Pragmatic Lab Setup — REST + MQTT end-to-end demo.
...
...              One unified server (mock_server.py :8080) with embedded MQTT broker (:1883).
...              Flow: Subscribe → POST job → Validate MQTT message.

Library          Process
Library          Collections
Library          libraries.automotive_lib
...                  base_url=http://127.0.0.1:8080
...                  mqtt_host=127.0.0.1
...                  mqtt_port=1883

Suite Setup      Start Lab
Suite Teardown   Stop Lab


*** Variables ***
${VEHICLE_ID}    vehicle_42


*** Test Cases ***
REST And MQTT Integration
    [Documentation]    Subscribe → POST → Validate.  The core demo flow.
    [Tags]    demo    e2e

    # 1. Subscribe BEFORE the action that publishes
    Subscribe    vehicle/${VEHICLE_ID}/commands
    Clear Inbox

    # 2. REST POST — server publishes the command to MQTT
    ${resp}=    Create Job    ${VEHICLE_ID}    reduce_speed
    Dictionary Should Contain Key    ${resp}    job_id

    # 3. Wait for the MQTT message and validate
    ${msg}=    Wait For Message    vehicle/${VEHICLE_ID}/commands    10
    Should Not Be Equal    ${msg}    ${NONE}    msg=No MQTT message received within timeout
    ${payload}=    Get From Dictionary    ${msg}    payload
    Should Be Equal As Strings    ${payload}[command]    reduce_speed
    Should Be Equal As Strings    ${payload}[vehicle_id]    ${VEHICLE_ID}
    Log To Console    \n✓ MQTT command received: ${payload}[command]


Vehicle Status Endpoint
    [Documentation]    Verify the vehicle status REST endpoint returns expected keys.
    [Tags]    demo    rest

    ${status}=    Get Vehicle Status
    Dictionary Should Contain Key    ${status}    speed
    Dictionary Should Contain Key    ${status}    rpm
    Log To Console    \n✓ Vehicle status: speed=${status}[speed] rpm=${status}[rpm]


*** Keywords ***
Start Lab
    [Documentation]    Launch unified mock server and connect MQTT client.
    Log To Console    \n=== Starting Pragmatic Lab ===
    ${py}=    Evaluate    __import__('sys').executable
    Start Process    ${py}    mock_server.py    alias=server
    Sleep    2.5s
    Server Should Be Healthy
    ${ok}=    Connect Mqtt
    Should Be True    ${ok}    msg=MQTT connection failed
    Log To Console    === Lab ready ===


Stop Lab
    [Documentation]    Disconnect MQTT and terminate server process.
    Log To Console    \n=== Stopping Lab ===
    Run Keyword And Ignore Error    Disconnect Mqtt
    Run Keyword And Ignore Error    Terminate Process    server    kill=true
