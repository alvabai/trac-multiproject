*** Settings ***
Resource       ${ENVIRONMENT}.txt
Resource       http.txt
Suite Setup    Setup and create project  # creates project ${suite_project}
Suite Teardown  Logout

*** Variables ***

*** Test Cases ***

Repository manager should be accessible
  [Documentation]  Test that we can access repository manager.
  Myget  /${suite_project}/admin/general/vcm
  ${body}=  Get Response Body
  Element Should contain  ${body}  h2  Add new repository


Adding new SVN repository should succeed
  [Documentation]  Test that we can add a svn repository.
  Add a repository  ${suite_project}  svn  my-svn-repository


Adding new repositories should succeed
  [Documentation]  Test that we can add new repositories.
  [Template]  Add a repository
  ${suite_project}  svn  my-svn-repository
  ${suite_project}  git  my-git-repository
  ${suite_project}  hg  my-hg-repository
