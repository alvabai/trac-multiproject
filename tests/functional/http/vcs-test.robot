*** Settings ***
Resource  vcs.txt

*** Variables ***
${repo1}   /Users/martti/Documents/tmp/multip  
${repo2}  /tmp/test_repo


*** Test Cases ***

Cloning a local git repository should succeed
  Git clone  /Users/martti/Documents/tmp/multip  /tmp/multip-clone

Cloning a git repository from projects should succeed
  Git clone   https://projects.qa.developer.nokia.com/foobar/git/gitrepo  /tmp/gitrepo
