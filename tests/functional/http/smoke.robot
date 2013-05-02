*** Settings ***
Resource       ${ENVIRONMENT}.txt
Resource       ../common_keywords.txt
Resource       http.txt
Suite Setup    Setup and login
Suite Teardown  Logout

*** Variables ***

*** Test Cases ***

Go to home page
  Myget  /home
  ${body}=  Get Response Body
  Element Should contain  ${body}  title  multiproject - home

Go to admin page
  Myget  /foo/admin
  ${body}=  Get Response Body
  Show response body in browser
  Element Should contain  ${body}  title  Administration: Basics - foo

Creating a project should work
  ${project}=  Get unique project name
  Create new project  ${project}
  ${body}=  Get Response Body
  Show response body in browser
  Log Response Headers
  htlib.Element Should contain  ${body}  title  ${project}


Changing project description should work
  ${time}=  Get time
  ${new_desc}=  Set Variable  New description at ${time}
  Change project description  foo  ${new_desc}
  Myget  /foo
  ${body}=  Get Response Body
  Element Should contain  ${body}  p  ${new_desc}


Changing project visibility should work
  Myget  /foo/admin/general/permissions
  ${body}=  Get Response Body
  Show response body in browser
  Element Should contain  ${body}  p  Project is currently: <strong>public</strong>
  Change project visibility  foo  private
  [Teardown]  Change project visibility  foo  public

*** Keywords ***

