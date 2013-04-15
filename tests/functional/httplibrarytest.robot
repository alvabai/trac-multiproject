*** Settings ***
Resource       ${ENVIRONMENT}.txt
Library        HttpLibrary.HTTP
Library        htlib
Library        Collections
Suite Setup    Create Variables

*** Variables ***
${USER}    tracadmin
${PASSWD}  tracadmin


*** Test Cases ***

Go to home page
  Login
  Myget  /foo/admin
  Show Response Body In Browser


Change project description
  Login
  Myget  /foo/admin
  Show Response Body In Browser
  #Mypost
  #Myget  /foo/
  #Show Response Body In Browser


*** Keywords ***

Get Cookies
  [Arguments]  ${chead}
  ${c}=  Get Session Cookies  ${chead}
  [Return]  ${c}

Create Variables
  ${suite_cookies}=  Create Dictionary
  Set Suite Variable  ${suite_cookies}

Login
  Create HTTP Context  localhost:4433  https
  [Documentation]  Send a HTTP GET request, sending and storing all the cookies.
  [Arguments]  ${login_url}=/  ${params}=${EMPTY}
  GET  ${login_url}
  ${status}=  Get Response Status
  Run Keyword If  '${status}' == '302 Found'  Follow Response
  Save cookies

  ${form_token}=  Get From Dictionary  ${suite_cookies}  trac_form_token
  ${cookie_hdrs}=  Get Cookie Header  ${suite_cookies}
  Set Request Header  Cookie  ${cookie_hdrs}
  Set Request Body  __FORM_TOKEN=${form_token}&username=${VALID_USER}&password=${VALID_PASSWD}&login=Login&action=do_login
  POST  /home/user
  Save cookies


Myget
  [Arguments]  ${url}=/home
  ${cookie_hdrs}=  Get Cookie Header  ${suite_cookies}
  Set Request Header  Cookie  ${cookie_hdrs}
  GET  ${url}
  Save cookies


Mypost
  #[Arguments]  
  ${form_token}=  Get From Dictionary  ${suite_cookies}  trac_form_token
  Set Request Body  __FORM_TOKEN=${form_token}&descr=UUSI_KUVAUS
  POST /foo/admin
  Save cookies


Save cookies
  ${headers}=  Get Response Header  set-cookie
  ${cookies}=  Headers to Dict  ${headers}  key=trac
  Update Dictionary  ${suite_cookies}  ${cookies}
