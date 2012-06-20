/* This file contains the javascript specific to multiproject_admin_backup.html template */
(function($, window, multiproject, undefined) {
    $(document).ready(function(){
        // Post separate form on click
        $('a.request').click(function(event) {
            event.preventDefault();
            $("#merge_request_form").submit();
        });
    });
})(jQuery, window, multiproject);