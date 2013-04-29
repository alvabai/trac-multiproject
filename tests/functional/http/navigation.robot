*** Settings ***
Resource       ${ENVIRONMENT}.txt
Resource       http.txt
Suite Setup    Setup and login
Suite Teardown  Logout
Variables       urls.py

*** Test Cases ***

URLs should be valid
  :FOR  ${url}  IN  @{URLS}
  \  Run Keyword And Continue On Failure   Myget  /foo/${url}
