*** Settings ***
Resource       ${ENVIRONMENT}.txt
Library        HttpLibrary.HTTP

*** Variables ***
${proj_name}  test_project6
${login_times}  5

*** Test Cases ***

Example
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
  Follow Response  
  Response Status Code Should Equal  200
  #Response Body Should Contain  generating different HTTP codes


*** Keywords ***
