*** Settings ***
Documentation  Test ticket funktionality
...            Run with pybot --variable ENVIRONMENT:<server_resource> <testfile>
Resource       ${ENVIRONMENT}.txt
Test Timeout  2 minutes
Suite setup  Login
Test Setup  Go to Welcome Page
Suite Teardown  Close Browser

*** Variables ***
${proj_name}
*** Keywords ***

*** Test Cases ***

Create project should succeed
  ${proj_name}  Get unique project name
  Set Suite Variable  ${proj_name}
  Create new project    ${proj_name}

ctxnavigation should not be visible when adding 1 ticket
  Go to  ${SERVER}/${proj_name}/newticket
  Check that title contains  New Ticket - ${proj_name}
  Create ticket  Ticket 1  Testing ticket
  Check that title contains  Ticket 1
  Page Should Not Contain Element  id=ctxtnavitems

ctxnavigation should be visible if there are more than 1 ticket
  Go to  ${SERVER}/${proj_name}/newticket
  Check that title contains  New Ticket - ${proj_name}
  Create ticket  Ticket 2  Testing ticket
  Check that title contains  Ticket 2
  Page Should Contain Element  id=ctxtnavitems

ctxnavigation should have new ticket link
  Go to  ${SERVER}/${proj_name}/ticket/1
  Check that title contains  Ticket 1
  Click link  New ticket
  Check that title contains  New Ticket - ${proj_name}