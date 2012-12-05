/* This file contains the javascript specific to multiproject_admin_backup.html template */
(function($, window, undefined) {
    var multiproject = window.multiproject;
    $(document).ready(function(){
        // Ask confirmation when button with confirm class is pressed
        var confirm = $('input.confirm');
        var cbox = multiproject.ui.ConfirmationBox(confirm.attr('alt'));
        confirm.click(function(event){
            // Return true / false to run the default action (NOTE: open can also return undefined)
            return cbox.open(event) === true;
        });
    });
})(jQuery, window);