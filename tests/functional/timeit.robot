*** Settings ***
Documentation  Tests related for changing project visibility. 
...            Run with pybot --variable ENVIRONMENT:<server_resource> <testfile>
Resource       ${ENVIRONMENT}.txt
Test Timeout  2 minutes

*** Variables ***
${proj_name}  test_project6
${login_times}  5

*** Test Cases ***

Logging in should be quick
    ${start}=  Get time
    Log in ${login_times} times
    ${end}=  Get time
    Log  ${start}
    Log  ${end}


*** Keywords ***

Log in and out
    Login
    Log out
    [TearDown]  Close Browser

Log in ${arg} times
    Repeat keyword  ${arg} times  Log in and out

# vim:sw=4:ts=4
