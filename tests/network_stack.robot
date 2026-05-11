*** Settings ***
Documentation    Vehicle Service + MQTT — simple E2E demo.

Library          Process
Library          Collections
Variables        ../config.py
Library          libraries.automotive_lib
...                  base_url=${BASE_URL}
...                  mqtt_host=${MQTT_HOST}
...                  mqtt_port=${MQTT_PORT}

Suite Setup      Start Lab
Suite Teardown   Stop Lab


*** Test Cases ***
Vehicle Status
    [Documentation]    GET /api/vehicle/status returns vehicle data.
    ${status}=    Get Vehicle Status
    Dictionary Should Contain Key    ${status}    speed
    Dictionary Should Contain Key    ${status}    rpm
    Log To Console    \n✓ Vehicle: speed=${status}[speed] rpm=${status}[rpm]


MQTT Publish And Receive
    [Documentation]    Publish a message on MQTT and verify it arrives.
    Subscribe    vehicle/speed
    Publish    vehicle/speed    {"value": 88, "unit": "km/h"}
    ${msg}=    Wait For Message    5
    Should Not Be Equal    ${msg}    ${NONE}
    Should Be Equal As Numbers    ${msg}[payload][value]    88
    Log To Console    \n✓ MQTT received: ${msg}[payload]


*** Keywords ***
Start Lab
    [Documentation]    Start MQTT broker, Vehicle Service, connect MQTT client.
    ${py}=    Evaluate    __import__('sys').executable
    Start Process    ${py}    mqtt_broker.py    alias=broker
    Sleep    1.5s
    Start Process    ${py}    mock_server.py    alias=server
    Sleep    1s
    Server Should Be Healthy
    Connect Mqtt
    Log To Console    \n=== Lab ready ===


Stop Lab
    Run Keyword And Ignore Error    Disconnect Mqtt
    Run Keyword And Ignore Error    Terminate Process    server    kill=true
    Run Keyword And Ignore Error    Terminate Process    broker    kill=true
