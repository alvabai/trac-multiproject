*** Settings ***
Documentation  Should not see project relations in Admin space
Resource       ${ENVIRONMENT}.txt
Test Timeout  1 minute
Suite setup  Login
Test Setup  Go to Welcome Page
Suite Teardown  Close Browser

*** Variables ***

*** Test Cases ***

Should not see project relations in Admin space
    ${proj_name}  Get unique project name 
    Create new project    ${proj_name}
    Title should be  ${proj_name} - ${proj_name}
    Click link  Admin
    Page should not contain   Project relations


# vim:sw=4:ts=4
