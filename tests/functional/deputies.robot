*** Settings ***
Documentation  Test adding users as deputies. 
...            Run with pybot --variable ENVIRONMENT:<server_resource> <testfile>
Resource       ${ENVIRONMENT}.txt
Resource       http/permission_variables.txt
Test Timeout  5 minutes
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
${password}  test112233!

*** Keywords ***
Add deputy for user
    [Arguments]  ${deputy}
    Input Text  id=add_deputy  ${deputy}.${deputy}
    Click element  id=add_deputy_button

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

Changing user passwords and status should be success
    Go to  ${SERVER}/home/admin/users/manage?username=${suite_user}.${suite_user}
    Activate local user  ${suite_user}  ${password}
    Page should contain  User ${suite_user}.${suite_user} updated
    Go to  ${SERVER}/home/admin/users/manage?username=${suite_user2}.${suite_user2}
    Activate local user  ${suite_user2}  ${password}
    Page should contain  User ${suite_user2}.${suite_user2} updated
    Go to  ${SERVER}/home/admin/users/manage?username=${suite_user3}.${suite_user3}
    Activate local user  ${suite_user3}  ${password}
    Page should contain  User ${suite_user3}.${suite_user3} updated

Create group to system should be success
    ${suite_group}=  Get unique groupname
    Set Suite Variable  ${suite_group}
    Go to  ${SERVER}/home/admin/general/permissions
    Title should be  Administration: Permissions - home
    Create group  ${suite_group}  ${USER_AUTHOR}
    Page should contain  ${suite_group}

Adding users to group should succeed
    Go to  ${SERVER}/home/admin/general/permissions
    Add user to group  ${suite_group}  ${suite_user2}
    Page should contain  User ${suite_user2}.${suite_user2} has been added to group ${suite_group}
    Add user to group  ${suite_group}  ${suite_user3}
    Page should contain  User ${suite_user3}.${suite_user3} has been added to group ${suite_group}

Deputies should work as defined
    Go to  ${SERVER}/home/admin/users/manage?username=${suite_user}.${suite_user}
    Add deputy for user  ${suite_user2}
    Page should contain  Deputy ${suite_user2}.${suite_user2} added.
    Logout
    Login within testcase  ${suite_user2}.${suite_user2}  ${password}
    Go to  ${SERVER}/home/admin/users/manage
    Page should contain  ${suite_user}.${suite_user}
    Logout
    Login within testcase  ${suite_user3}.${suite_user3}  ${password}
    Go to  ${SERVER}/home/admin/users/manage
    Page Should Not Contain  ${suite_user}.${suite_user}
    Go to  ${SERVER}/home/admin/users/manage?username=${suite_user}.${suite_user}
    Page should contain  USER_AUTHOR privileges are required to perform this operation on user:
    Logout
    Login within testcase  ${VALID_USER}  ${VALID_PASSWD}
    Go to  ${SERVER}/home/admin/users/manage?username=${suite_user3}.${suite_user3}
    Add deputy for user  ${suite_user}
    Page should contain  Deputy ${suite_user}.${suite_user} didn't have enough rights
    Go to  ${SERVER}/home/admin/users/manage?username=${suite_user}.${suite_user}
    Click element  id=${suite_user2}.${suite_user2}_remove_deputy
    Confirm Action
    Page Should Not Contain  ${suite_user2}.${suite_user2}
    Logout
    Login within testcase  ${suite_user2}.${suite_user2}  ${password}
    Go to  ${SERVER}/home/admin/users/manage
    Page Should Not Contain  ${suite_user}.${suite_user}





