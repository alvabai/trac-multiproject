(function($, window, undefined) {
    $(document).ready(function(){
        var content = {
        action: 'timeline_events' };

        $.ajax({
            url: document.URL,
            data: content,
            type: 'GET',
            success: function(response) {
                $("#project_summary_timeline_container").html(response);
            },
            error: function(response) {
                $("#project_summary_timeline_container").html(
                    "<h2>Error</h2><p>Error in background system.</p>"
                    );
            }
        });
    });
})(jQuery, window);