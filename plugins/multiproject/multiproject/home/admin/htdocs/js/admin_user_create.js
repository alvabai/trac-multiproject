$(document).ready(function(){
    var username_check = $('a#check');
    var email_check = $('a#checkEmail');
    var username_field = $('input#username');
    var email_field = $('input#email');
    var firstname_field = $('input#first');
    var lastname_field = $('input#last');
    var check_progress = false;

    // Generate default username from first and last name
    var username = multiproject.ui.UserNameField(username_field);
    var email_element = multiproject.ui.UserNameField(email_field);

    // Callback for checking username conflict
    function check_value(event, db_field, input_element, input_field) {
        event.preventDefault();
        input_field.addClass('loading');

        if (check_progress) {
            input_field.removeClass('loading');
            return false;
        }

        check_progress = true;
        input_element.checkConflict(function(result){
            input_field.removeClass('ok');
            input_field.removeClass('error');
            if (result) {
                input_field.addClass('error');
            }
            else {
                input_field.addClass('ok');
            }
            check_progress = false;
            input_field.removeClass('loading');
        }, db_field, input_field);
    };

    // Callback for generating username
    var update_username = function(event) {
        username.generate([firstname_field.val(), lastname_field.val()], username_field);
    };

    // Bind events
    //username_check.click(check_username, 'username');
    username_check.live("click", function(evt){
        if (username_field.val() == "") {
            alert("username missing.");
        }else{
        check_value(evt, 'username', username, username_field);            
        }
    });
    email_check.live("click", function(evt){
        if (email_field.val() == "") {
            alert("email missing.");
        }else{
            check_value(evt, 'email', email_element, email_field);
        }
    });
    firstname_field.keyup(update_username);
    lastname_field.keyup(update_username);
});