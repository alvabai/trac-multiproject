*** Settings ***
Documentation  Tests related for accessing to the home project permission with trac_admin rights
Resource       common_resource.txt
Suite setup  Login
Test Setup  Go to Welcome Page
Suite Teardown  Close Browser

*** Variables ***
${proj_name}  home


*** Test Cases ***

Access to home project permission
    Title Should be  multiproject – home
    Click link  Admin panel
    Title Should be  Administration: Edit categories – home
