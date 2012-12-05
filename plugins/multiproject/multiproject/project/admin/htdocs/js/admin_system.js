/* This file contains the javascript specific to admin_system.html template */
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
