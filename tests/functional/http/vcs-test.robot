*** Settings ***
Resource  vcs.txt

*** Test Cases ***

Cloning a local git repository should succeed
  Git clone  /Users/martti/Documents/tmp/multip  /tmp/multip-clone

Cloning a git repository from projects should succeed
  Clone a git repository   https://projects.qa.developer.nokia.com/foobar/git/gitrepo  /tmp/gitrepo


