*** Settings ***

Documentation  Tests projects explore page
Resource       common_resource.txt
Suite setup  Login
Suite Teardown  Close Browser


*** Variables ***

${proj_name}  home
${proj2_name}  new_demo
${no_categories_el}  .no_selected_cat
${category_el}  .sb_category


*** Test Cases ***

Should show correct page title
    Go to  ${EXPLORE_PAGE}
    Title Should be  Explore projects – ${proj_name}

Should show selected search category
		Goto  ${WELCOME_PAGE}
		Create new project    ${proj2_name}
		Go to  ${BASE_URL}${proj2_name}/admin
		Click Link  Categorization
		Click Element  id=cat_267
		Go to  ${EXPLORE_PAGE}
    Click Element  css=.list_name
    Element Should Not Be Visible  css=${no_categories_el}
    Page Should Contain Element  css=${category_el}

Should not show injected search categories
    Go to  ${EXPLORE_PAGE}#c[]=<script>alert('XSS');</script>
    Element Should Be Visible  css=${no_categories_el}
    Page Should Not Contain Element  css=${category_el}