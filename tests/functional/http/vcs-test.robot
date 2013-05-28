*** Settings ***
Resource  vcs.txt
Resource      ${ENVIRONMENT}.txt
Library   Operating System
Suite Setup   Cd to temp dir
Test Timeout  10 s

*** Variables ***
${tmp_dir}     /tmp/
${local}       /tmp/gitrepo
${file}        TEST.TXT


*** Test Cases ***

Git clone over https should succeed
  Set environment variable  GIT_SSL_NO_VERIFY  true
  Git clone  ${https_proto}/ci_test_project/git/git-repo  git-repo
  [Teardown]  Remove directory  git-repo  recursive=True

Git clone over ssh should succeed
  Git clone  ${git_ssh}/ci_test_project/git/git-repo  git-repo
  [Teardown]  Remove directory  git-repo  recursive=True


SVN checkout over https should succeed
  svn checkout  ${https_proto}/ci_test_project/svn/svn-repo  svn-repo
  [Teardown]  Remove directory  svn-repo  recursive=True

Hg clone over https should succeed
  hg clone  ${https_proto}/ci_test_project/hg/hg-repo  hg-repo
  [Teardown]  Remove directory  hg-repo  recursive=True


Git commit over https should succeed
  Set environment variable  GIT_SSL_NO_VERIFY  true
  Git clone and push  ${https_proto}/ci_test_project/git/git-repo  git-repo
  [Teardown]  Remove directory  git-repo  recursive=True


*** Keywords ***

Git clone and push
  [Arguments]  ${remote}  ${local}
  Set environment variable  GIT_SSL_NO_VERIFY  true
  Git clone  ${remote}  ${local}
  ${prev}=  cd  ${local}
  ${time}=    Get Time
  Create file  ${file}  ${time}
  Git add  ${file}
  Git commit  ${file}  new commit
  Git push
  cd   ${prev}
  @{files}=  List Directory  ${local}
  Log Many  @{files}


