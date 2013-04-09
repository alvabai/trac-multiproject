*** Settings ***
Resource       ${ENVIRONMENT}.txt
Library        HttpLibrary.HTTP
Library        htlib

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
  ${chead}=  Get Response Header  set-cookie  
  ${c1}=  Get Session Cookies  ${chead}
  Log  ${c1}
  ${form_token}=  Get Session Cookies  ${chead}  key=form_token
  ${form_token}=  Evaluate  str("${form_token}").split('=')[1]
  Log  ${form_token}
  Set Request Header  Cookie  ${c1}
  Set Request Body  __FORM_TOKEN=${form_token}&username=tracadmin&password=tracadmin&login=Login&action=do_login
  POST  /home/user
  ${all_cookies}=  Get Response Header  set-cookie
  ${auth_cookie}=  Get Session Cookies  ${all_cookies}  key=auth 
  Log  ${auth_cookie}
  Set Request Header  Cookie  ${c1}; ${auth_cookie}
  GET  /home/
  #${body}=  Get response body
  #Log  ${body}
  #Response Status Code Should Equal  200
  #Set Request Body  username=tracadmin&password=tracadmin&action=do_login
  Show Response Body In Browser
  #POST  /home/user/
  #Response Status Code Should Equal  200

*** Keywords ***
