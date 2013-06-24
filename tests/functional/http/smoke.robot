*** Settings ***
Resource       ${ENVIRONMENT}.txt
Resource       ../common_keywords.txt
Resource       http.txt
Suite Setup    Setup and create project  # creates ${suite_project} and ${suite_cookies}
Suite Teardown  Cleanup and exit

*** Variables ***
${proj_name}  test_project6
${login_times}  5

*** Test Cases ***

Go to home page
  Myget  /home
  ${body}=  Get Response Body
  Element Should contain  ${body}  title  multiproject - home

Go to admin page
  Myget  /${suite_project}/admin
  ${body}=  Get Response Body
  Element Should contain  ${body}  title  Administration: Basics - ${suite_project}

Creating a new project with svn repo should work
  ${project}=  Get unique project name
  Create new project  ${project}  ${project}-svn-repo  svn
  ${body}=  Get Response Body
  Element Should contain  ${body}  title  ${project}


Changing project description should work
  [Documentation]  Change description for ${suite_project}
  ${time}=  Get time
  ${new_desc}=  Set Variable  New description at ${time}
  Change project description  ${suite_project}  ${new_desc}
  Myget  /${suite_project}
  ${body}=  Get Response Body
  Element Should contain  ${body}  p  ${new_desc}


Changing project visibility should work
  Myget  /${suite_project}/admin/general/permissions
  ${body}=  Get Response Body
  Element Should contain  ${body}  p  Project is currently: <strong>public</strong>
  Change project visibility  ${suite_project}  private
  [Teardown]  Change project visibility  ${suite_project}  public


Backend respond to logging in should be quick
    [Tags]      unstable
    ${start}=  Get time  epoch
    Log in ${login_times} times
    ${end}=  Get time  epoch
    Log  ${end}
    ${diff}=  Evaluate  (${end}-${start})/${login_times}
    Save time info  ${diff}


*** Keywords ***
