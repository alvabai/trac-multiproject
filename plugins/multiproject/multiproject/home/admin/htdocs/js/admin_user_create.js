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

    // Callback for generating username
    var update_username = function(event) {
        username.generate([firstname_field.val(), lastname_field.val()], username_field);
    };

    function check_value(event, query, input_field) {
        event.preventDefault();
        input_field.addClass('loading');

        if (check_progress) {
            input_field.removeClass('loading');
            return false;
        }

        check_progress = true;
        input_field.removeClass('ok');
        input_field.removeClass('error');

        var query = query || '';
        var data = {q: query};
        var path = multiproject.req.base_path + "/api/username_or_email_exists";

        var req = $.getJSON(path, data, "json");

        req.done(function(result) {
            if (result === true) {
                input_field.addClass('error');
            }else{
                input_field.addClass('ok');
            };
        });
        req.fail(function( jqxhr, textStatus, error ) {
            var err = textStatus + ', ' + error;
            console.log( "Request Failed: " + err );
        });
        check_progress = false;
        input_field.removeClass('loading');
    };

    // Bind events
    //username_check.click(check_username, 'username');
    username_check.live("click", function(evt){
        if (username_field.val() == "") {
            alert("username missing.");
        }else{
            check_value(evt, username_field.val(), username_field);
        }
    });
    email_check.live("click", function(evt){
        if (email_field.val() == "") {
            alert("email missing.");
        }else{
           check_value(evt, email_field.val(), email_field);
        }
    });
    firstname_field.keyup(update_username);
    lastname_field.keyup(update_username);
});