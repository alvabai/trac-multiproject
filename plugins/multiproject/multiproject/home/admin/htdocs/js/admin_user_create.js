$(document).ready(function(){
    var username_check = $('a#check');
    var username_field = $('input#username');
    var firstname_field = $('input#first');
    var lastname_field = $('input#last');
    var check_progress = false;

    // Generate default username from first and last name
    var username = multiproject.ui.UserNameField(username_field);

    // Callback for checking username conflict
    var check_username = function(event) {
        event.preventDefault();
        username_field.addClass('loading');

        if (check_progress) {
            username_field.removeClass('loading');
            return false;
        }

        check_progress = true;
        username.checkConflict(function(result){
            username_field.removeClass('ok');
            username_field.removeClass('error');
            if (result) {
                username_field.addClass('error');
            }
            else {
                username_field.addClass('ok');
            }
            check_progress = false;
            username_field.removeClass('loading');
        });
    };

    // Callback for generating username
    var update_username = function(event) {
        username.generate([firstname_field.val(), lastname_field.val()]);
    };

    // Bind events
    username_check.click(check_username);
    firstname_field.keyup(update_username);
    lastname_field.keyup(update_username);
});