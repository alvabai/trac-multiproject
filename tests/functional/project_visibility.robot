*** Settings ***
Documentation  Tests related for changing project visibility
Resource       common_resource.txt
Test Timeout  1 minute
Suite setup  Login
Test Setup  Go to Welcome Page
Suite Teardown  Close Browser

*** Variables ***
${proj_name}  test_project6

*** Test Cases ***

Change public project to private
    Create new project    ${proj_name}
    Title should be  ${projname} – ${projname}
    Click link  Admin
    Click link  Permissions
    Click element  name=makeprivate
    Page should contain  Project is currently : private
    Click link  Projects Home
    Click link  All public projects >
    Page should not contain  ${proj_name}
    Click link  My Projects
    Page should contain  ${proj_name}
    [Teardown]     Remove project  ${proj_name}

Removing project should succeed
    Create new project  ${projname}
    Title should be  ${projname} – ${projname}
    Remove project  ${projname}
    Title should be  My projects – home
    Page should not contain  ${projname}



# vim:sw=4:ts=4
