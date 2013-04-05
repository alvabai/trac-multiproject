$(document).ready(function () {

        // Bind confirmation on button click
        $('form[name="project-remove"] input.confirm').click(function(event){
            // Carry out the default action is true is returned
            return confirm('Are you sure you want to remove project?');
        })
    }
);

/* admin_tags.html */
function selectTag(obj)
{
	document.getElementById('tag_input').value = obj.innerHTML;
}

/* admin_usergroups.html */
function username(name) {
    $('#sg_subject').val(name)
}
function decline_membership(name) {
    $('#decline_user').val(name)
    $('#membership_form').submit()
}