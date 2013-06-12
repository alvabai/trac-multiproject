*** Settings ***
Documentation  Test adding users as deputies. 
...            Run with pybot --variable ENVIRONMENT:<server_resource> <testfile>
Resource       ${ENVIRONMENT}.txt
Resource       http/permission_variables.txt
Test Timeout  2 minutes
Suite setup  Login
Test Setup  Go to Welcome Page
Suite Teardown  Close Browser

*** Variables ***
${suite_project}  home
${suite_user}
${suite_user2}
${suite_user3}
${suite_group}
${suite_email}  test@test.fi
${suite_password}  test1234!
${created}  Get created date

*** Test Cases ***

Create local users to system should be success
    ${suite_user}=  Get unique username  user1
    Set Suite Variable  ${suite_user}
    ${suite_user2}=  Get unique username  user2
    Set Suite Variable  ${suite_user2}
    ${suite_user3}=  Get unique username  user3
    Set Suite Variable  ${suite_user3}
    Click link  Admin panel
    Title should be  Administration: Edit categories - home
    Click link  Create user
    Title should be  Administration: Create User - home
    Create user  ${suite_user}  ${suite_email}
    Page should contain  Created new local user: ${suite_user}
    Create user  ${suite_user2}  ${suite_email}
    Page should contain  Created new local user: ${suite_user2}
    Create user  ${suite_user3}  ${suite_email}
    Page should contain  Created new local user: ${suite_user3}

Create group to system should be success
    ${suite_group}=  Get unique groupname
    Set Suite Variable  ${suite_group}
    Go to  ${SERVER}/home/admin/general/permissions
    Title should be  Administration: Permissions - home
    Create group  ${suite_group}  ${USER_AUTHOR}
    Page should contain  ${suite_group}

Add users to group
    
