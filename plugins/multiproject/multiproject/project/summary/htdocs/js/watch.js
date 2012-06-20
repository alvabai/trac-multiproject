/**
 * File contains the functionality related to project watching/following.
 * It makes ajax requests to REST API to retrieve the status and binding the buttons accordingly.
 */
(function($, window, multiproject) {
    $(document).ready(function(){
        var watch_form = $('form.watch');

        // Bind actions on each form buttons
        $.each(watch_form, function(idx, box) {
            box = $(box);
            var rest_url = box.find('input[name="resturl"]:first').attr('value');
            var watch = box.find('input[name="watch"]');
            var unwatch = box.find('input[name="unwatch"]');

            // Requester to REST API for watching the project
            var watchProject = function(cb) {
                cb = cb || function(){};
                $.get(rest_url, {action:'watch'}, cb);
            };

            // Requester to REST API for unwatching the project
            var unwatchProject = function(cb) {
                cb = cb || function(){};
                $.get(rest_url, {action:'unwatch'}, cb);
            };

            // Callback for updating the status
            var updateWatchStatus = function() {
                // Hide buttons at start
                watch.hide();
                unwatch.hide();

                // Retrieve the project following status and update the UI accordingly
                $.getJSON(rest_url, function(data){
                    // Hide or show buttons
                    watch.toggle(!data.is_watching);
                    unwatch.toggle(data.is_watching);

                    // Update follower count
                    var status_field = box.siblings().filter('p.status:first');
                    if (data.count === 0) {
                        status_field.text('Be first to follow');
                    }
                    else if (data.count === 1 && data.is_watching) {
                        status_field.text('You are already following');
                    }
                    else if (data.count === 1 && !data.is_watching) {
                        status_field.text("One follower. Why don't you?");
                    }
                    else {
                        status_field.text(data.count + " followers");
                    }
                });
            };

            // Bind on watch
            watch.click(function(event){
               event.preventDefault();
               watchProject(updateWatchStatus);
            });

            // Bind on unwatch
            unwatch.click(function(event){
                event.preventDefault();
                unwatchProject(updateWatchStatus);
            });

           // Initialize status
           updateWatchStatus(rest_url);
        });

    });
})(jQuery, window, multiproject);