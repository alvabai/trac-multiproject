*** Settings ***
Documentation  Tests related to better warn message for archived projects. 
...            Run with pybot --variable ENVIRONMENT:<server_resource> <testfile>
Resource       ${ENVIRONMENT}.txt
Test Timeout  2 minutes
Suite setup  Login
Test Setup  Go to Welcome Page
Suite Teardown  Close Browser

*** Variables ***
${proj_name}  test_archived_project
${non_existent_project}  non_existing_project
${archived_message}  This project has been archived.
${not_found_message}  Environment not found

*** Test Cases ***

better warn message for archived project
    [Tags]  unstable
    ${projname}  Get unique project name  test_archived_project
    Create new project  ${projname}
    Check that title contains  ${projname} - ${projname}
    Remove project  ${projname}
    Check that title contains  My projects - home
    Page should not contain  ${projname}
    Go to        ${SERVER}/${proj_name}
    Page should contain  ${archived_message}


non existing project should return environment not found
    Go to  ${SERVER}/${non_existent_project}
    Page should contain  ${not_found_message}



# vim:sw=4:ts=4
