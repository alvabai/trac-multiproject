*** Settings ***
Resource       ${ENVIRONMENT}.txt
Library        HttpLibrary.HTTP

*** Variables ***
${proj_name}  test_project6
${login_times}  5

*** Test Cases ***

Goto login page
  [Documentation]   Fetching login page should succeed
  Create HTTP Context   localhost:4433  https
  GET  /home/user
  Response Status Code Should Equal  200
  #Follow Response  
  #Response Body Should Contain  generating different HTTP codes


Follow redirect
  [Documentation]   Fetching login page should succeed
  Create HTTP Context   localhost:4433  https
  GET  /
  Response Status Code Should Equal  302
  Log Response Headers
  Follow Response  
  Log Response Headers
  Response Status Code Should Equal  200

Login
  Create HTTP Context   localhost:4433  https
  GET  /
  Follow Response  
  Set Basic Auth  tracadmin   tracadmin
  POST  /home/user?goto=https://localhost:4433/home/
  Log Response Status  
  Log Response Headers  
  Response Status Code Should Equal  200
  Set Request Body  username=tracadmin&password=tracadmin&action=do_login
  POST  /home/user/
  Show Response Body In Browser
  Response Status Code Should Equal  200

*** Keywords ***
