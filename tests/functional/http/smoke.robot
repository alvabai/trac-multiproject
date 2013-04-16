*** Settings ***
Resource       ${ENVIRONMENT}.txt
Resource       http.txt
Suite Setup    Setup and login
Suite Teardown  Logout

*** Variables ***
${VALID_USER}    tracadmin
${VALID_PASSWD}  tracadmin


*** Test Cases ***

Go to home page
  Login
  Myget  /foo/admin
  ${body}=  Get Response Body
  htlib.Element Should contain  ${body}  elem="p"  Administration: Permissions – foo

Changing project description should work
  ${time}=  Get time
  ${new_desc}=  Set Variable  New description at ${time}
  Change project description  foo  ${new_desc}
  Myget  /foo
  ${body}=  Get Response Body
  htlib.Element Should contain  ${body}  elem="p"  ${new_desc}


Changing project visibility should work
  Myget  /foo/admin/general/permissions
  ${body}=  Get Response Body
  htlib.Element Should contain  ${body}  elem="p"  Project is currently : <strong>public</strong>
  Change project visibility  foo  private
  [Teardown]  Change project visibility  foo  public
