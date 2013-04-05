*** Settings ***
Documentation  Tests related to have most download tab in explore projects
Resource       ${ENVIRONMENT}.txt
Suite setup  Login
Test Setup  Go to Welcome Page
Suite Teardown  Close Browser

*** Test Cases ***

Access to explore section
    Click Link  All public projects >
    Element should be visible id=tab_download
