*** Settings ***
Resource        ${ENVIRONMENT}.txt
Test Timeout    2 minutes
Suite setup     Login
Test Setup      Go to Welcome Page
Suite Teardown  Close Browser


*** Variables ***
${proj_name}     tmp_proj
${HTTP_SPLIT_URL}  ${proj_name}/x%0d%0aContent-Type:text/html%0d%0a%0d%0a%3Cimg%20onerror='alert(234)'src=x%3E/


*** Test Cases ***
Request with invalid characters should be denied
    [Documentation]  This tests a scenario of HTTP response splitting
    [Setup]  Create new project  ${proj_name}
    Log    ${SERVER}
    Go to  ${SERVER}/${HTTP_SPLIT_URL}
    Page should contain   403
    Page should contain   Forbidden
    [Teardown]  Remove project  ${proj_name}


# vim:sw=4:ts=4
