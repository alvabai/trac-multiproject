*** Settings ***
Resource       ${ENVIRONMENT}.txt
Resource       ../common_keywords.txt
Resource       http.txt
Suite Setup    Setup and login
Suite Teardown  Logout
Variables       urls.py

*** Test Cases ***

URLs should be valid
  ${project}=  Set Variable  foo
  :FOR  ${url}  IN  @{URLS}
  \  Run Keyword And Continue On Failure   Myget  /${project}/${url}
