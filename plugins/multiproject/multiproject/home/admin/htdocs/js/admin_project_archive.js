/* This file contains the javascript specific to multiproject_admin_project_archive.html template */
(function($, window, multiproject, undefined) {
    $(document).ready(function(){
        // Ask confirmation when button with confirm class is pressed
        $('input.confirm').click(function(event){
            // Read msg from alt property and return true / false to run the default action
            var cbox = multiproject.ui.ConfirmationBox($(this).attr('alt'));
            return cbox.open();
        });
    });
})(jQuery, window, multiproject);