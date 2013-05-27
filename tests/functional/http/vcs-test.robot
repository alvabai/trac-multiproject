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
  Git clone  ${git_https}/ci_test_project/git/git-repo  git-repo
  [Teardown]  Remove directory  git-repo  recursive=True

Git clone over ssh should succeed
  Git clone  ${git_ssh}/ci_test_project/git/git-repo  git-repo
  [Teardown]  Remove directory  git-repo  recursive=True
