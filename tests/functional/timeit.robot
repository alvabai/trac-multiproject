*** Settings ***
Documentation  Tests related for changing project visibility. 
...            Run with pybot --variable ENVIRONMENT:<server_resource> <testfile>
Resource       ${ENVIRONMENT}.txt
Library        OperatingSystem
Test Timeout  2 minutes

*** Variables ***
${proj_name}  test_project6
${login_times}  5

*** Test Cases ***

Logging in should be quick
    ${start}=  Get time  epoch
    Log in ${login_times} times
    ${end}=  Get time  epoch
    Log  ${end}
    ${diff}=  Evaluate  (${start}-${end})/${login_times}
    Save time info  ${diff}


*** Keywords ***

Log in and out
    Login
    Log out
    [TearDown]  Close Browser

Log in ${arg} times
    Repeat keyword  ${arg} times  Log in and out

Save time info
    [Documentation]  Save timing data to a csv file
    [Arguments]  ${time}
    Create file  data.csv  ${time}


# vim:sw=4:ts=4
