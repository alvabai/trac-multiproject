/* Put all admin page utility scripts/methods here */

/*------------- Project archive scripts -----------------------*/
function restore(project_archive_id) {
    $('#archived_projects').load("?restore=" + project_archive_id);
}
function remove(project_archive_id) {
    if(confirm("This will remove project for good. Are you sure?")) {
        $('#archived_projects').load("?remove=" + project_archive_id);
    }
}
function remove_expired() {
    $('#archived_projects').load("?remove_expired");
}

/**/