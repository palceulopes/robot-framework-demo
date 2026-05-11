*** Settings ***
Documentation    Vehicle Service + Dispatch Service + MQTT (embedded mocks).
...
...              Narrative: fleet dispatch assigns jobs; commands surface on MQTT; Vehicle Service
...              exposes REST signals. Run:
...
...              uv sync --extra automotive
...
...              uv run robot --pythonpath . --listener libraries.automotive_listener \\
...                  --logtitle "HiL Vehicle/Dispatch" \\
...                  --reporttitle "Integration demo" \\
...                  --tagstatinclude demo \\
...                  --outputdir results \\
...                  tests/network_stack.robot

Library          Process
Library          Collections
Variables        variables.config
Resource         ${PROJECT_ROOT_STR}${/}resources/mqtt_keywords.resource
Resource         ${PROJECT_ROOT_STR}${/}resources/vehicle_service_keywords.resource
Resource         ${PROJECT_ROOT_STR}${/}resources/dispatch_keywords.resource

Suite Setup      Start Stack And Connect Clients
Suite Teardown   Stop Stack And Disconnect Clients


*** Test Cases ***
Vehicle Service REST Health And Signals
    [Documentation]    Vehicle Service (mock ECU REST): connectivity and signal reads.
    [Tags]    demo    network    rest    vehicle_service

    Log To Console    \n[Vehicle] REST health and signals
    ECU Should Be Reachable
    ${speed}=    Get ECU Signal Value    speed
    Should Be Equal As Numbers    ${speed}    ${0}
    ${ver}=    Get ECU Firmware Version String
    Should Contain    ${ver}    mock
    ECU Diagnostics Should Be Available


MQTT Vehicle Speed Publish And Receive
    [Documentation]    Telemetry on vehicle/sensors/speed (embedded broker + client).
    [Tags]    demo    network    mqtt

    Log To Console    \n[MQTT] Telemetry round-trip (vehicle/sensors/speed)
    Publish Vehicle Speed Over MQTT    ${88}
    ${msg}=    Wait For Message    vehicle/sensors/speed    ${5}
    Should Not Be Equal    ${msg}    ${NONE}
    Dictionary Should Contain Key    ${msg}    payload


Dispatch Assigns Job And MQTT Reflects Command
    [Documentation]    Dispatch Service POSTs a job; assignment appears on dispatch/commands/<vehicle_id>.
    [Tags]    demo    network    dispatch    integration

    Log To Console    \n[Dispatch] Job assignment via MQTT (dispatch/commands/<vehicle_id>)
    Dispatch Service Should Be Reachable
    ${cmd_topic}=    Catenate    SEPARATOR=    dispatch/commands/    ${DEFAULT_DEVICE_ID}
    Subscribe To MQTT Topic    ${cmd_topic}
    Clear MQTT Inbox
    ${resp}=    Create Dispatch Job For Vehicle    ${DEFAULT_DEVICE_ID}    reduce_speed
    Dictionary Should Contain Key    ${resp}    job
    Sleep    0.8s
    ${msg}=    Wait For Message    ${cmd_topic}    ${10}
    Should Not Be Equal    ${msg}    ${NONE}
    ${inner}=    Get From Dictionary    ${msg}    payload
    Dictionary Should Contain Key    ${inner}    command
    ${cmd}=    Get From Dictionary    ${inner}    command
    Should Be Equal As Strings    ${cmd}    reduce_speed
    Log To Console    OK: dispatch command observed on MQTT (${cmd_topic})


MQTT Vehicle Stack And Dispatch Sanity
    [Documentation]    Combined sanity: Vehicle REST + MQTT client + Dispatch REST.
    [Tags]    demo    network    integration

    Log To Console    \n[Stack] Vehicle + MQTT + Dispatch connectivity
    ECU Should Be Reachable
    Dispatch Service Should Be Reachable
    ${rpm}=    Get ECU Signal Value    rpm
    Should Be True    ${rpm} > ${0}
    Publish Vehicle Speed Over MQTT    ${50}
    ${st}=    Get MQTT Client Status
    Dictionary Should Contain Key    ${st}    connected
    ${fleet}=    Get Fleet Status From Dispatch
    Dictionary Should Contain Key    ${fleet}    total_jobs


*** Keywords ***
Start Stack And Connect Clients
    [Documentation]    Start MQTT broker, Vehicle Service (Flask), Dispatch Service (Flask); connect MQTT client.
    Log To Console    \n=== Stack startup: broker -> Vehicle Service :${ECU_REST_PORT} -> Dispatch Service :${DISPATCH_SERVICE_PORT} ===
    ${py}=    Evaluate    __import__('sys').executable
    Start Process    ${py}    mock_servers/mqtt_broker_helper.py
    ...    cwd=${PROJECT_ROOT_STR}
    ...    alias=mqtt_br
    Sleep    1.5s
    Start Process    ${py}    mock_servers/vehicle_service_server.py
    ...    --host    ${ECU_REST_HOST}
    ...    --port    ${ECU_REST_PORT}
    ...    cwd=${PROJECT_ROOT_STR}
    ...    alias=vehicle_rest
    Sleep    1.5s
    Start Process    ${py}    mock_servers/dispatch_rest_server.py
    ...    --host    ${DISPATCH_SERVICE_HOST}
    ...    --port    ${DISPATCH_SERVICE_PORT}
    ...    --mqtt-host    ${MQTT_BROKER_HOST}
    ...    --mqtt-port    ${MQTT_BROKER_PORT}
    ...    cwd=${PROJECT_ROOT_STR}
    ...    alias=dispatch_rest
    Sleep    1.5s
    Connect To MQTT Vehicle Network


Stop Stack And Disconnect Clients
    [Documentation]    Disconnect MQTT and terminate child processes (reverse order).
    Log To Console    \n=== Stack teardown ===
    Run Keyword And Ignore Error    Disconnect MQTT Vehicle Network
    Run Keyword And Ignore Error    Terminate Process    dispatch_rest    kill=true
    Run Keyword And Ignore Error    Terminate Process    vehicle_rest    kill=true
    Run Keyword And Ignore Error    Terminate Process    mqtt_br    kill=true
