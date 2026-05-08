*** Settings ***
Documentation    REST ECU API keywords (install: uv sync --extra automotive).
...
...              Point ECU_BASE_URL at mock_servers/ecu_rest_server.py or a real bench ECU.

Variables        ../variables/config.py
Library          Collections
Library          libraries.rest_ecu_api    base_url=${ECU_BASE_URL}


*** Keywords ***
ECU Should Be Reachable
    [Documentation]    GET /api/health must return HTTP 200.
    ${ok}=    Check Ecu Connectivity
    Should Be True    ${ok}


Get ECU Signal Value
    [Arguments]    ${signal_name}
    [Documentation]    Read a signal (speed, rpm, temperature, fuel, fuel_level, ...).
    ${val}=    Get Ecu Signal    ${signal_name}
    RETURN    ${val}


Get ECU Firmware Version String
    [Documentation]    GET /api/system/version JSON version field.
    ${v}=    Get Ecu Version
    RETURN    ${v}


ECU Diagnostics Should Be Available
    [Documentation]    Fetch diagnostics/errors payload from mock ECU.
    ${d}=    Get Diagnostics
    Dictionary Should Contain Key    ${d}    errors
