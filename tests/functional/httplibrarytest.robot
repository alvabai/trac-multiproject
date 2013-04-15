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

Changing project description should work
  ${time}=  Get time
  ${new_desc}=  Set Variable  New description at ${time}
  Change project description  foo  ${new_desc}
  Myget  /foo
  Show Response Body In Browser
  ${body}=  Get Response Body
  htlib.Element Should contain  ${body}  elem="p"  ${new_desc}


*** Keywords ***

Change project description
  [Arguments]  ${project}  ${new_description}
  Login
  Myget   /${project}
  Myget   /${project}/admin  # needed to get form_token ?
  Mypost  /${project}/admin  form_values=icon=&name=foo&author_id=4&created=2013-03-04 18:33:58&published=2013-03-04 18:33:59&descr=${new_description}&apply=Apply changes


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
  [Documentation]  Make a GET request to the given url.
  [Arguments]  ${url}=/home
  ${cookie_hdrs}=  Get Cookie Header  ${suite_cookies}
  Set Request Header  Cookie  ${cookie_hdrs}
  GET  ${url}
  Save cookies


Mypost
  [Documentation]  Make a POST request to the given url with given arguments. All form values except the form_token should be given as the second argument, separated with ampersands.
  [Arguments]  ${url}  ${form_values}
  ${form_token}=  Get From Dictionary  ${suite_cookies}  trac_form_token
  Set Request Body  __FORM_TOKEN=${form_token}&${form_values}
  POST  ${url}
  Save cookies
  Follow Response


Save cookies
  [Documentation]  Save current cookies. Note that path information is not considered, so cookies with same name but different path-attributes override each other.
  ${headers}=  Get Response Header  set-cookie
  ${cookies}=  Headers to Dict  ${headers}  key=trac
  Update Dictionary  ${suite_cookies}  ${cookies}
