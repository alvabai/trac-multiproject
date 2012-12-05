/**
 * Javascript functionality specific to message group macro
 */
(function($, window, undefined) {
    var multiproject = window.multiproject || {};
    var users = new multiproject.api.Users();
    var currentUser;
    var filter = $('input#filter');
    var filterDelay = 500;
    var minFilterLength = 3;
    var filterQuery = '';

    var renderRecipients = function(message) {
        var recipients = [];

        // NOTE: Each is synchronous
        $.each(message.recipients, function(key, uid){
            users.getUser({id: uid}, function(user){
                // Skip the current user for listing
                if (user.id !== currentUser.id) {
                    recipients.push(user.displayName);
                }
            });
        });

        return '<a class="messages-dialog" href="#group_id=' + message.group.id +'">' + recipients.join(', ') + '</a>';
    };

    // Instructions for Transparency how to render fields
    // NOTE: Name of the element placeholder (id/class/etc) cannot be same as name of the sub-object
    var renderDirectives = {
        text: {html: function(message) { return this.content; }},
        participants: {html: function(message) { return this.recipients ? renderRecipients(this) : "unknown"; }},
        posted: {text: function(message) { return this.created ? multiproject.formatDate(new Date(Date.parse(this.created))) : ''; }}
    };

    var getMessages = function(opts) {
        opts.query = opts.query || '';
        opts.limit = opts.limit || 5;
        opts.callback = opts.cb || function() { };

        filter.addClass('loading');
        $.getJSON(
            multiproject.req.base_path + "/api/message/list",
            {q: opts.query, limit: opts.limit},
            function(messages) {
                filter.removeClass('loading');
                return opts.callback(messages);
            }
        );
    };

    var renderMessages = function(messages) {
        $('tbody.messagegroups').render(messages, renderDirectives);
    };

    var invokeFilter = function() {
        filterQuery = filter.val();
        if (filterQuery.length >= minFilterLength || filterQuery.length === 0) {
            getMessages({query: filterQuery, cb: renderMessages});
        }
    };

    $(document).ready(function(){
        var handler;
        // Set and reset filter handler on every keystroke: until filterDelay is reached
        filter.keyup(function(event) {
            if (handler) {
                window.clearTimeout(handler);
            }
            handler = window.setTimeout(invokeFilter, filterDelay);
        });

        // Do initial query
        users.getCurrentUser(function(user){
            currentUser = user;
            getMessages({query: '', limit: 5, cb: renderMessages});
        });
    });
})(jQuery, window);
