*** Settings ***
Library    Process
Library    libraries.automotive_lib

Suite Setup       Start Lab
Suite Teardown    Stop Lab


*** Test Cases ***
REST Vehicle Speed
    ${resp}=    Get Vehicle Speed
        
    # Should Be Equal As Numbers    ${resp}[speed]    100
    Sleep    1s
    ${resp2}=    Get Vehicle Speed
    Should Be Higher than        ${resp}[speed]    ${resp2}[speed]
    

MQTT Vehicle Speed
    Subscribe Speed
    Publish Speed    88
    ${msg}=    Wait For Message
    Should Be Equal As Numbers    ${msg}[speed]    88


*** Keywords ***
Start Lab
    ${py}=    Evaluate    __import__('sys').executable
    Start Process    ${py}    mqtt_broker.py    alias=broker
    Sleep    1.5s
    Start Process    ${py}    mock_server.py    alias=server
    Sleep    1s
    Connect Mqtt

Stop Lab
    Run Keyword And Ignore Error    Disconnect Mqtt
    Run Keyword And Ignore Error    Terminate Process    server    kill=true
    Run Keyword And Ignore Error    Terminate Process    broker    kill=true
