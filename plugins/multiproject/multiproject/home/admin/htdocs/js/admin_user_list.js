/**
 * Javascript functionality specific to admin_user_list.html
 */
(function($, window, undefined) {
    var multiproject = window.multiproject;

    $(document).ready(function(){
        // User autocomplete
        var element = $('input#usersearch');
        var userfield = new multiproject.ui.UserField(element, {minLength: 0, status: ['active', 'expired', 'inactive', 'blocked', 'disabled']});

        // Instructions for Transparency how to render fields
        var directives = {
            username: {
                text: function(element) {
                    return this.firstname + ' ' + this.lastname + ' (' + this.username + ')';
                },
                href: function(element) {
                    return multiproject.req.base_path  + '/admin/users/manage?username=' + this.username;
                }
            },
            expires: {
                text: function(element) {
                    return this.expires ? new Date(Date.parse(this.expires)).toDateString() : '';
                }
            }
        };

        // On select, open user edit
        userfield.onSelect = function(event, ui) {
            element.addClass('loading');
            window.location = multiproject.req.base_path  + "/admin/users/manage?username=" + ui.item.username;
        };
        // Modify request
        userfield.onRequest = function (request, response) {
            // Show loader class until response is shown
            element.addClass('loading');
            var keyword = element.val();
            var status = $('select#status option:selected').attr('name');
            var auth = $('select#auth option:selected').attr('name');
            // Make AJAX request to fetch users
            $.getJSON(multiproject.req.base_path + "/api/user/list", {
                q:keyword, field:'id,username,firstname,lastname,email,mobile', status:status, auth:auth, perm:'USER_MODIFY'}, function(data){
                // Always return empty: we don't need autocomplete in this case but render the table instead
                response({});
                $('tbody.users').render(data, directives);

                element.removeClass('loading');
            });
        };

        // Render field, run initial search and move focus to it
        userfield.render();
        element.autocomplete('search');
        element.focus();

        // Run autocomplete also when selection is changed
        $('select#status').change(function(){ element.autocomplete('search'); });
        $('select#auth').change(function(){ element.autocomplete('search'); });
    });
})(jQuery, window);
