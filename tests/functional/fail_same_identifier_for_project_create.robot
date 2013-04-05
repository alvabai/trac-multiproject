*** Settings ***
Documentation  Creating a duplicate project should fail
Resource       ${ENVIRONMENT}.txt
Test Timeout  1 minute
Suite setup  Login
Test Setup  Go to Welcome Page
Suite Teardown  Close Browser

*** Variables ***
${proj_name}  duplicate_project
${failed_to_create}  This project already exists! Change identifier

*** Test Cases ***

Creating a project with a same name than an existing one should fail
    Create new project    ${proj_name}
    Goto  ${WELCOME_PAGE}
    Create new project    ${proj_name}
    Page should contain   ${failed_to_create}
    [Teardown]     Remove project  ${proj_name}


# vim:sw=4:ts=4
