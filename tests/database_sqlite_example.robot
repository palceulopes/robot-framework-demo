*** Settings ***
Documentation    Example SQLite checks using DatabaseLibrary (automotive extra).
...
...              Tag example_db — exclude from CI if SQLite driver differs per platform.

Library          Collections
Library          DatabaseLibrary

Suite Setup      Connect SQLite In Memory
Suite Teardown   Disconnect From Database


*** Test Cases ***
SQLite Engine Is Reachable
    [Documentation]    Minimal smoke on in-memory SQLite (zero external DB cost).
    [Tags]    example_db    database

    @{rows}=    Query    SELECT sqlite_version() AS v;
    Should Not Be Empty    ${rows}
    ${first}=    Get From List    ${rows}    ${0}
    Should Not Be Empty    ${first}


*** Keywords ***
Connect SQLite In Memory
    [Documentation]    DatabaseLibrary 2.x — sqlite3 with in-memory database file name.
    ${path}=    Set Variable    :memory:
    Connect To Database    sqlite3    database=${path}
