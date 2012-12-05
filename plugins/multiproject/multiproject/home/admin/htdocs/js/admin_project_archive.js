/* This file contains the javascript specific to multiproject_admin_project_archive.html template */
(function($, window, undefined) {
    var multiproject = window.multiproject;
    $(document).ready(function(){
        // Ask confirmation when button with confirm class is pressed
        var confirm = $('input.confirm');
        var cbox = multiproject.ui.ConfirmationBox();
        confirm.click(function(event){
            // Read msg from alt property and return true / false to run the default action
            cbox.msg = $(this).attr('alt');
            return cbox.open(event) === true;
        });
    });
})(jQuery, window);