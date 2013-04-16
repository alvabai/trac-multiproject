$("#add_new_repository").live("submit", function(){
    check = true;
    if($("#add_repository_name").val().length < 3){
        check = false;
        alert("Repository name must be 3 characters long.");
    }
    else if(!$('#add_repository_name').val().match(/^[a-zA-Z0-9_-]*$/)){
        check = false;
        alert("Repository name contains special chars!"+
        "Only alphanumerical, underscore and hyphen allowed.");
    }
    else if($('#add_repository_type').val() == ""){
        check = false;
        alert("Repository type must be chosen.")
    }
    return check;
});

(function($, window, undefined) {
    var multiproject = window.multiproject;
    $(document).ready(function(){
        // Ask confirmation when button with confirm class is pressed
        var confirm = $('input.confirm');
        var cbox = new multiproject.ui.ConfirmationBox(confirm.attr('alt'));
        confirm.click(function(event){
            // Read msg from alt property and return true / false to run the default action
            return cbox.open(event) === true;
        });
    });
})(jQuery, window);