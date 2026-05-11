*** Settings ***
Documentation    Dispatch Service REST keywords (install: uv sync --extra automotive).
...
...              Point DISPATCH_BASE_URL at mock_servers/dispatch_rest_server.py.

Variables        variables.config
Library          Collections
Library          libraries.rest_dispatch_api    base_url=${DISPATCH_BASE_URL}


*** Keywords ***
Dispatch Service Should Be Reachable
    [Documentation]    GET /api/health must return HTTP 200.
    ${ok}=    Check Dispatch Connectivity
    Should Be True    ${ok}


Create Dispatch Job For Vehicle
    [Arguments]    ${vehicle_id}    ${command}
    [Documentation]    POST a job; Dispatch publishes to MQTT topic dispatch/commands/<vehicle_id>.
    ${resp}=    Create Dispatch Job    ${vehicle_id}    ${command}
    Dictionary Should Contain Key    ${resp}    job
    RETURN    ${resp}


Get Fleet Status From Dispatch
    [Documentation]    GET /api/v1/fleet/status
    ${st}=    Get Fleet Status
    RETURN    ${st}


List Open Dispatch Jobs
    [Documentation]    GET /api/v1/dispatch/jobs (jobs list).
    ${jobs}=    List Dispatch Jobs
    RETURN    ${jobs}
