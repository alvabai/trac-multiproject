*** Settings ***
Documentation  Creating a duplicate project should fail
Resource       ${ENVIRONMENT}.txt
Test Timeout  1 minute
Suite setup  Login
Test Setup  Go to Welcome Page
Suite Teardown  Close Browser

*** Test Cases ***

Creating a project with same environment name as an existing one should fail incl archived projects
    [Tags]      unstable
    ${archived_proj_name}  Get unique project name 
    Create new project    ${archived_proj_name}
    Title should be  ${archived_proj_name} - ${archived_proj_name}
    Page should not contain   ${failed_to_create}
    Remove project  ${archived_proj_name}
    Goto  ${WELCOME_PAGE}
    Create new project    ${archived_proj_name}
    Page should contain   ${failed_to_create}

Creating a project with same environment name as an existing one should fail
    ${proj_name}  Get unique project name 
    Create new project    ${proj_name}
    Title should be  ${proj_name} - ${proj_name}
    Page should not contain   ${failed_to_create}
    Goto  ${WELCOME_PAGE}
    Create new project    ${proj_name}
    Page should contain   ${failed_to_create}

# vim:sw=4:ts=4
