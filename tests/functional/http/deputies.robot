*** Settings ***
Resource       ${ENVIRONMENT}.txt
Resource       ../common_keywords.txt
Resource       users_and_groups.txt
Resource       permission_variables.txt
Resource       http.txt
Suite Setup    Setup and login  # creates ${suite_project} and ${suite_cookies}
Suite Teardown  Logout

*** Variables ***
${suite_project}  home
${suite_user}
${suite_user2}
${suite_user3}
${suite_group}
${suite_email}  test@test.fi
${suite_password}  test1234!
${created}  Get created date
${suite_created}  


*** Test Cases ***

User with user author permissions should be able to add as deputy
  ${suite_user}=  Get unique username
  Set Suite Variable  ${suite_user}
  ${form_token}=  Get From Dictionary  ${suite_cookies}  trac_form_token
  ${cookie_hdrs}=  Get Cookie Header  ${suite_cookies}
  ${boundary}=  Get unique boundary
  Set Request Header  Cookie  ${cookie_hdrs} 
  Set Request Header  Content-Type  multipart/form-data; boundary=${boundary}
  Set Request Body  '${boundary} Content-Disposition: form-data; name="__FORM_TOKEN" ${form_token} ${boundary} Content-Disposition: form-data; name="first" ${suite_user} ${boundary} Content-Disposition: form-data; name="last" ${suite_user} ${boundary} Content-Disposition: form-data; name="username" ${suite_user} ${boundary} Content-Disposition: form-data; name="email" ${suite_email} ${boundary} Content-Disposition: form-data; name="mobile" ${boundary} Content-Disposition: form-data; name="icon"; filename="" Content-Type: application/octet-stream ${boundary} Content-Disposition: form-data; name="create" Create account ${boundary}--
  POST  /home/admin/users/create_local
  Save cookies
  ${status}=  Get Response Status
  Run Keyword If  '${status}' == '302 Found'  Follow Response
  Run Keyword If  '${status}' == '303 See Other'  Follow Response