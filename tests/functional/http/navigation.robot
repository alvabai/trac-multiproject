*** Settings ***
Resource       ${ENVIRONMENT}.txt
Resource       ../common_keywords.txt
Resource       http.txt
Suite Setup    Setup and login
Suite Teardown  Logout
Variables       urls.py

*** Test Cases ***

URLs should be valid
  [Documentation]  Create a project and test access to various pages.
  ${project}=  Get unique project name
  Create new project  ${project}  ${project}-git-repo  git
  :FOR  ${url}  IN  @{URLS}
  \  Run Keyword And Continue On Failure   Myget  /${project}/${url}
  [Teardown]  Remove project  ${project}
