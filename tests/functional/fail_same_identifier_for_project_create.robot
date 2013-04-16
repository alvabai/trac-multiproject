*** Settings ***
Documentation  Creating a duplicate project should fail
Resource       ${ENVIRONMENT}.txt
Test Timeout  1 minute
Suite setup  Login
Test Setup  Go to Welcome Page
Suite Teardown  Close Browser

*** Variables ***
${archived_proj_name}  duplicate_projectxn
${proj_name}  a_duplicate_project_xnn
${failed_to_create}  This project already exists! Change identifier

*** Test Cases ***

Creating a project with same environment name as an existing one should fail incl archived projects
    Create new project    ${archived_proj_name}
    Remove project  ${archived_proj_name}
    Goto  ${WELCOME_PAGE}
    Create new project    ${archived_proj_name}
    Page should contain   ${failed_to_create}

Creating a project with same environment name as an existing one should fail
    Create new project    ${proj_name}
    Goto  ${WELCOME_PAGE}
    Create new project    ${proj_name}
    Page should contain   ${failed_to_create}

# vim:sw=4:ts=4
