*** Settings ***
Documentation  Tests project create failure if exists project with same identifier
Resource       common_resource.txt
Test Timeout  1 minute
Suite setup  Login
Test Setup  Go to Welcome Page
Suite Teardown  Close Browser

*** Variables ***
${proj_name}  test_project1
${proj_name}  test_project1
${failed_to_create}  A project with '''${proj_name}''' as identifier already exists.

*** Test Cases ***

Project create should fail if exists project with same identifier
    Create new project    ${proj_name}
    Goto  ${WELCOME_PAGE}
    Create new project    ${proj_name}
    Page should contain   ${failed_to_create}
    [Teardown]     Remove project  ${proj_name}


# vim:sw=4:ts=4
