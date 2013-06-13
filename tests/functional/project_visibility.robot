*** Settings ***
Documentation  Tests related for changing project visibility. 
...            Run with pybot --variable ENVIRONMENT:<server_resource> <testfile>
Resource       ${ENVIRONMENT}.txt
Test Timeout  2 minutes
Suite setup  Login
Test Setup  Go to Welcome Page
Suite Teardown  Close Browser

*** Variables ***

*** Test Cases ***

Change public project to private
    [Tags]      unstable
    [Timeout]      3 minutes
    ${proj_name}  Get unique project name 
    Create new project    ${proj_name}
    Title should be  ${proj_name} - ${proj_name}
    Click link  Admin
    Click link  Permissions
    Click element  name=makeprivate
    Page should contain  Project is currently: private
    Click link  Projects Home
    Click link  All public projects >
    Page should not contain  ${proj_name}
    Click link  My Projects
    Page should contain  ${proj_name}
    [Teardown]     Remove project  ${proj_name}

Removing project should succeed
    [Tags]      unstable
    ${projname}  Get unique project name 
    Create new project  ${projname}
    Title should be  ${projname} - ${projname}
    Remove project  ${projname}
    Title should be  My projects - home
    Page should not contain  ${projname}



# vim:sw=4:ts=4
