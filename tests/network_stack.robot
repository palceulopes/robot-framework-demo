*** Settings ***
Documentation    MQTT + REST integration using embedded mock servers (automotive extra).
...
...              Run: uv sync --extra automotive
...              robot --listener libraries.automotive_listener tests/network_stack.robot

Library          Process
Library          Collections
Variables        variables.config
Resource         ${PROJECT_ROOT_STR}${/}resources/mqtt_keywords.resource
Resource         ${PROJECT_ROOT_STR}${/}resources/rest_ecu_keywords.resource

Suite Setup      Start Stack And Connect Clients
Suite Teardown   Stop Stack And Disconnect Clients


*** Test Cases ***
REST ECU Mock Health And Signals
    [Documentation]    Validates mock ECU REST endpoints against libraries.rest_ecu_api.
    [Tags]    network    rest    mock_ecu

    ECU Should Be Reachable
    ${speed}=    Get ECU Signal Value    speed
    Should Be Equal As Numbers    ${speed}    ${0}
    ${ver}=    Get ECU Firmware Version String
    Should Contain    ${ver}    mock
    ECU Diagnostics Should Be Available


MQTT Vehicle Speed Publish And Receive
    [Documentation]    Embedded broker + MQTT client round-trip on vehicle/sensors/speed.
    [Tags]    network    mqtt

    Publish Vehicle Speed Over MQTT    ${88}
    ${msg}=    Wait For Message    vehicle/sensors/speed    ${5}
    Should Not Be Equal    ${msg}    ${NONE}
    Dictionary Should Contain Key    ${msg}    payload


MQTT And REST Stack Sanity
    [Documentation]    Combined sanity check for parallel protocol use.
    [Tags]    network    integration

    ECU Should Be Reachable
    ${rpm}=    Get ECU Signal Value    rpm
    Should Be True    ${rpm} > ${0}
    Publish Vehicle Speed Over MQTT    ${50}
    ${st}=    Get MQTT Client Status
    Dictionary Should Contain Key    ${st}    connected


*** Keywords ***
Start Stack And Connect Clients
    [Documentation]    Start embedded MQTT (aMQTT) and mock ECU (Flask), then connect MQTT client.
    ${py}=    Evaluate    __import__('sys').executable
    Start Process    ${py}    mock_servers/mqtt_broker_helper.py
    ...    cwd=${PROJECT_ROOT_STR}
    ...    alias=mqtt_br
    Sleep    1.5s
    Start Process    ${py}    mock_servers/ecu_rest_server.py
    ...    --host    ${ECU_REST_HOST}
    ...    --port    ${ECU_REST_PORT}
    ...    cwd=${PROJECT_ROOT_STR}
    ...    alias=ecu_rest
    Sleep    1.5s
    Connect To MQTT Vehicle Network


Stop Stack And Disconnect Clients
    [Documentation]    Disconnect MQTT and terminate child processes.
    Run Keyword And Ignore Error    Disconnect MQTT Vehicle Network
    Run Keyword And Ignore Error    Terminate Process    ecu_rest    kill=true
    Run Keyword And Ignore Error    Terminate Process    mqtt_br    kill=true
