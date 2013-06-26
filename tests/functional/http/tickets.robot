*** Settings ***
Resource       ${ENVIRONMENT}.txt
Resource       ../common_keywords.txt
Resource       http.txt
Suite Setup    Setup and login

*** Variables ***
${proj_name}

*** Test Cases ***

Go to home page
  Myget  /home
  ${body}=  Get Response Body
  Element Should contain  ${body}  title  multiproject - home
  ${proj_name}=  Get unique project name
  Set Suite Variable  ${proj_name}
  Create new project  ${proj_name}  svn-repo

ctxtnavitems should not be shown if only 1 ticket
  Myget  /${proj_name}/newticket
  ${body}=  Get Response Body
  Element Should contain  ${body}  h1  Create New Ticket
  Create ticket  /${proj_name}/newticket  ticket1  testing ticket
  Show Response Body in Browser
  ${body}=  Get Response Body
  Element Should contain  ${body}  a  Ticket #1
  Element Should Not contain  ${body}  li  ← Previous Ticket

ctxtnavitems should be shown if there is more than 1 ticket
  Myget  /${proj_name}/newticket
  ${body}=  Get Response Body
  Element Should contain  ${body}  h1  Create New Ticket
  Create ticket  /${proj_name}/newticket  ticket2  testing ticket
  Myget  /${proj_name}/ticket/2
  Show Response Body in Browser
  ${body}=  Get Response Body
  Element Should contain  ${body}  a  Ticket #2
  Element Should contain  ${body}  a  Previous Ticket