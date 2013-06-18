*** Settings ***
Resource      vcs.txt
Resource      ${ENVIRONMENT}.txt
Resource      http.txt
Library       Operating System
Suite Setup   Create project with default repositories  # creates project ${suite_project}
Test Setup    Cd to temp dir
Test Timeout  2 minutes

*** Variables ***
${tmp_dir}     /tmp/
${local}       /tmp/gitrepo
${file}        TEST.TXT


*** Test Cases ***

Git clone over https should succeed
  Set environment variable  GIT_SSL_NO_VERIFY  true
  Run until succeeds   Git clone  ${https_proto}/${suite_project}/git/git-repo  git-repo
  [Teardown]  Remove directory  git-repo  recursive=True

Git clone over ssh should succeed
  Git clone  ${git_ssh}/${suite_project}/git/git-repo  git-repo
  [Teardown]  Remove directory  git-repo  recursive=True

Git commit over https should succeed
  Set environment variable  GIT_SSL_NO_VERIFY  true
  ${time}=    Get Time
  Git clone and push  ${https_with_cred}/${suite_project}/git/git-repo  git-repo  ${time}
  Verify file from ui  ${PROTOCOL}://${SERVER}:${HTTPS_PORT}/${suite_project}/browser/git-repo/${file}  ${time}
  [Teardown]  Remove directory  git-repo  recursive=True

Git commit over ssh should succeed
  ${time}=    Get Time
  Git clone and push  ${git_ssh}/${suite_project}/git/git-repo  git-repo  ${time}
  Verify file from ui  ${PROTOCOL}://${SERVER}:${HTTPS_PORT}/${suite_project}/browser/git-repo/${file}  ${time}
  [Teardown]  Remove directory  git-repo  recursive=True

Hg clone over https should succeed
  [Timeout]  4 min
  Run until succeeds   hg clone  ${https_proto}/${suite_project}/hg/hg-repo  hg-repo
  [Teardown]  Remove directory  hg-repo  recursive=True

Hg commit should succeed
  [Timeout]  5 min
  Run until succeeds   hg clone  ${https_proto}/${suite_project}/hg/hg-repo  hg-repo
  ${prev}=  cd  hg-repo
  ${time}=  Get time
  Create file  ${file}  ${time}
  Run until succeeds   Hg commit  ${VALID_USER}  ${file}  new commit at ${time}
  Run until succeeds   Hg push  ${https_with_cred}/${suite_project}/hg/hg-repo
  Verify file from ui  ${https_proto}/${suite_project}/browser/hg-repo/${file}  ${time}
  [Teardown]  Remove directory  ${prev}/hg-repo  recursive=True


SVN checkout should succeed
  Run until succeeds  svn checkout  ${https_proto}/${suite_project}/svn/svn-repo  svn-repo
  [Teardown]  Remove directory  /tmp/svn-repo  recursive=True

SVN commit should succeed
  [Documentation]  Commit file, provided that certificate is accepted and saved earlier.
  Run until succeeds  svn checkout  ${https_proto}/${suite_project}/svn/svn-repo  svn-repo
  ${prev}=  cd  svn-repo
  ${time}=  Get time
  Create file  ${file}  ${time}
  svn add   ${file}
  svn commit  ${VALID_USER}  ${VALID_PASSWD}  new commit at ${time}
  Verify file from ui  ${https_proto}/${suite_project}/browser/svn-repo/${file}  ${time}
  cd  ${prev}
  [Teardown]  Remove directory  svn-repo  recursive=True



*** Keywords ***

Git clone and push
  [Arguments]  ${remote}  ${local}  ${content}
  Set environment variable  GIT_SSL_NO_VERIFY  true
  Run until succeeds   Git clone  ${remote}  ${local}
  ${prev}=  cd  ${local}
  Create file  ${file}  ${content}
  Git add  ${file}
  Git commit  ${file}  new commit
  Git push
  cd   ${prev}
  @{files}=  List Directory  ${local}
  Log Many  @{files}

Verify file from ui
  [Arguments]  ${url}  ${content}
  Myget  ${url}
  ${body}=  Get response body
  Should contain  ${body}  ${content}

Create project with default repositories
  [Documentation]  Login and create a project having repositories named
  ...              svn-repo, hg-repo and git-repo, with the obvious types.
  Setup and create project  # creates project ${suite_project}
  Add a repository  ${suite_project}  svn  svn-repo
  Add a repository  ${suite_project}  hg  hg-repo
  Add a repository  ${suite_project}  git  git-repo


Run until succeeds
  [Arguments]  ${kw}  @{args}
  [Timeout]  65s
  :FOR  ${i}  IN RANGE  22
  \     ${status}=  Run keyword and return status  ${kw}  @{args}
  \     Log  ${status}
  \     Run keyword if   ${status}   Exit for loop
  \     Sleep  3
  Should Be True  ${status}


