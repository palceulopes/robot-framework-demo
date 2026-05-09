*** Settings ***
Documentation    MQTT vehicle-network keywords (install: uv sync --extra automotive).
...
...              Use when an MQTT broker is reachable at MQTT_BROKER_HOST:MQTT_BROKER_PORT
...              (embedded: uv run python mock_servers/mqtt_broker_helper.py).

Variables        ${CURDIR}${/}../variables/config.py
Library          libraries.mqtt_vehicle_network
...                  broker_host=${MQTT_BROKER_HOST}
...                  broker_port=${MQTT_BROKER_PORT}
...                  auto_connect=False


*** Keywords ***
Connect To MQTT Vehicle Network
    [Documentation]    Connect library client to the broker (call after broker is up).
    ${ok}=    Connect To Broker
    Should Be True    ${ok}


Disconnect MQTT Vehicle Network
    [Documentation]    Stop background loop and disconnect.
    Disconnect From Broker


Publish Vehicle Speed Over MQTT
    [Arguments]    ${speed_kmh}
    [Documentation]    Publish speed on the standard vehicle/sensors/speed topic.
    Publish Vehicle Signal    speed    ${speed_kmh}    km/h


Wait For Vehicle Alert Over MQTT
    [Arguments]    ${alert_type}=high_speed    ${timeout_s}=5
    [Documentation]    Wait for an alert (e.g. high_speed, high_temp).
    ${ok}=    Wait For Alert    ${alert_type}    ${timeout_s}
    Should Be True    ${ok}


Clear MQTT Inbox
    [Documentation]    Clear buffered messages for assertions.
    Clear Messages


Get MQTT Client Status
    [Documentation]    Return connection and broker endpoint info as dict.
    ${s}=    Get Broker Status
    RETURN    ${s}
