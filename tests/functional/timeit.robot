*** Settings ***
Documentation  Tests related for changing project visibility. 
...            Run with pybot --variable ENVIRONMENT:<server_resource> <testfile>
Resource       ${ENVIRONMENT}.txt
Resource       ../common_keywords.txt
Library        OperatingSystem
Test Timeout  2 minutes

*** Variables ***
${proj_name}  test_project6
${login_times}  5

*** Test Cases ***

Logging in should be quick
    [Tags]      unstable
    ${start}=  Get time  epoch
    Log in ${login_times} times with browser
    ${end}=  Get time  epoch
    Log  ${end}
    ${diff}=  Evaluate  (${end}-${start})/${login_times}
    Save time info  ${diff}


*** Keywords ***

Log in and out with browser
    Login
    Logout
    [TearDown]  Close Browser

Log in ${arg} times with browser
    Repeat keyword  ${arg} times  Log in and out with browser

# vim:sw=4:ts=4
