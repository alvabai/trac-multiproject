*** Settings ***
Resource       ${ENVIRONMENT}.txt
Resource       ../common_keywords.txt
Resource       http.txt
Suite Setup    Setup and create project  # creates ${suite_project} and ${suite_cookies}
Suite Teardown  Cleanup and exit

*** Variables ***
${suite_project}
*** Test Cases ***

Go to home page
  Myget  /home
  ${body}=  Get Response Body
  Element Should contain  ${body}  title  multiproject - home

Creating a new project with git repo should work
  ${suite_project}=  Get unique project name
  Set Suite Variable  ${suite_project}
  Create new project  ${suite_project}  ${suite_project}-git-repo  git
  ${body}=  Get Response Body
  Element Should contain  ${body}  title  ${suite_project}

Empty git repo should be reachable and download as zip button should be disabled
  Myget  /${suite_project}/browser/${suite_project}-git-repo
  ${body}=  Get Response Body
  Should contain  ${body}  class="disabledButton"
