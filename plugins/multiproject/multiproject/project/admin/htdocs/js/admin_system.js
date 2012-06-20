/* This file contains the javascript specific to admin_system.html template */
$(document).ready(function(){
    // Ask confirmation when button with confirm class is pressed
    $('input.confirm').click(function(event){
        // Read msg from alt property and return true / false to run the default action
        var cbox = multiproject.ui.ConfirmationBox($(this).attr('alt'));
        return cbox.open();
    });
});
