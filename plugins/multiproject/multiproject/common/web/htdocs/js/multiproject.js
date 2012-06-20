/**
 * This file contains the Multiproject specific functions and objects.
 * They all are located in multiproject namespace.
 *
 */
(function($, window, undefined) {
    // Extend multiproject object
    var multiproject = window.multiproject || {};
    multiproject.ui = {};
    multiproject.api = {};

    // Register jQuery plugins into multiproject namespace
    $.fn.multiproject = $.fn.multiproject || {};

    /**
     * UserField: Autocomplete for username
     *
     * @param {jQuery Object} element input field element
     *
     * @example
     * var userfield = new multiproject.ui.UserField($('input#userfield'));
     * userfield.onSelect = function(event, ui) {
     *     alert(ui.item.username);
     * };
     * userfield.render();
     *
     * @returns multiproject.ui.UserField
     * @class
     */
    multiproject.ui.UserField = function (element, opts) {
        this.opts = opts || {};
        var self = this;

        /**
         * Callback for making a request. Does the AJAX request to backend
         * @param request
         * @param response
         */
        this.onRequest = function (request, response) {
            // Show loader class until response is shown
            element.addClass('loading');
            var keyword = element.val();
            // Make AJAX request to fetch users
            $.getJSON(multiproject.req.base_path + "/userautocomplete",
                {q: keyword, field: 'id,username,firstname,lastname,email'}, function (data) {
                response(data);
                element.removeClass('loading');
            });
        };

        /**
         * Callback when item is focused: Before focus is moved to an item (not selecting),
         * ui.item refers to the focused item.
         * @param event
         * @param ui
         */
        this.onFocus = function(event, ui) {
            element.val(ui.item.username);
            return false;
        };

        /**
         * Callback for item rendering
         * @param ul
         * @param item
         */
        this.onRender = function(ul, item){
            return $("<li></li>")
                .data( "item.autocomplete", item )
                .append("<a><strong>" + item.firstname + " " + item.lastname + "</strong><br/>" + item.username + " - " + item.email + "</a>")
                .appendTo(ul);
        };

        /**
         * Callback for making the selection
         * @param event
         * @param ui
         */
        this.onSelect = function(event, ui) {
            // TODO: Modify in your template as you like
            return true;
        };

        /**
         * Callback for change event
         * @param event
         * @param ui
         */
        this.onChange = function(event, ui) {
            // TODO: Modify in your template as you like
            return true;
        };

        /**
         * Constructs the autocomplete field with the callbacks and options provided
         * @param {Object} opts Options
         */
        this.render = function(opts) {
            // Set and extend autocomplete options
            opts = opts || {};
            var opt_defaults = {source:self.onRequest, minLength:2, focus:self.onFocus, select:self.onSelect, change:self.onChange};
            opts = $.extend(opt_defaults, opts);

            element.autocomplete(opts);
            element.data("autocomplete")._renderItem = self.onRender;
        };

        return this;
    };

    /**
     * Class for managing the usernames
     *
     * @param {jQuery Object} element
     * @class
     */
    multiproject.ui.UserNameField = function(element) {
        var self = this;
        self.username = '';
        self.element = element;

        /**
         * Generates safe name from given words and places the value to element
         * @param {Array} words List of words
         * @returns {String} Possible username
         */
        this.generate = function(words) {
            var parts = [];

            if (typeof words === 'String') {
                words = new Array(words);
            }

            // Construct username word by word
            $.each(words, function(key, word){
                if (word.trim().length > 0) {
                    parts.push(self._safeString(word));
                }
            });
            self.username = parts.join('.');

            // Set value to element and return it back as well
            $(self.element).val(self.username);
            return self.username;
        };

        /**
         * Function for checking if the given username conflicts
         * @param {String} username
         * @param {function} callback
         */
        this.checkConflict = function(callback) {
            var result = false;
            var username = self.element.val();

            $.getJSON(multiproject.req.base_path + "/userautocomplete", {q:username, fields:'username'}, function(data){
                for(var entry in data) {
                    if (data[entry].username === username) {
                        result = true;
                        break;
                    }
                }
                callback(result);
            });
        };

        /**
         * Replace unwanted characters
         * @param str
         * @return {String} safe string
         */
        this._safeString = function(str) {
            str = str.replace(" ", "_");
            str = str.replace(":", "");
            str = str.replace("%", "");
            return str.toLowerCase();
        };

        return this;
    };

    /**
     * Class for asking configuration from the user
     *
     * @param {String} msg Message to show
     * @class
     */
    multiproject.ui.ConfirmationBox = function(msg) {
        var self = this;
        self.msg = msg;

        /**
         * Opens the confirmation box
         * @return true on confirm, false on cancel (handy for executing the default event)
         */
        this.open = function() {
            // Use alert for now
            if (window.confirm(self.msg)) {
                self.onConfirm();
                return true;
            } else {
                self.onCancel();
                return false;
            }
        };

        this.onConfirm = function() {
            // To be overwritten
            return true;
        };

        this.onCancel = function() {
            // To be overwritten
            return false;
        };

        return this;
    };

    /**
     *
     * @param channelid
     * @return {*}
     * @constructor
     */
    multiproject.api.NotificationSystem = function() {
        var self = this;
        var channelid = "channel1";
        self.juggernaut = undefined;
        self.callbacks = [];

        /**
         * Juggernaut returns string but we're sending json in it:
         * this callback generator is used to parse JSON string into JSON and pass it for the callback
         * @param callback
         * @return {Function}
         */
        this.callbackParser = function(callback) {
            var cb = function(jsonstr) {
                var json = $.parseJSON(jsonstr);
                return callback(json);
            };
            return cb;
        };

        /**
         * Subscribes to channel message. Provided callback is invoked
         * message message is received
         * @param callback
         */
        this.subscribe = function(callback) {
            // TODO: How to get channel ids?
            if (typeof(self.juggernaut) !== 'undefined') {
                self.juggernaut.subscribe(channelid, self.callbackParser(callback));
            }
            else {
                self.callbacks.push(callback);
            }
        };

        /**
         * Post message to channel
         * @param {Object} receiver: {receiver_id:<id>} or {project_id:<id>}
         * @param {String} msg: Message to send
         * @param callback: Optional callback to execute after successful posting
         */
        this.postMessage = function(receiver, msg, callback) {
            callback = callback || function(){};
            // form token
            var ftoken = $.cookie('trac_form_token');
            var data = $.extend({content: msg, '__FORM_TOKEN': ftoken}, receiver);

            $.ajax({
                url: multiproject.req.base_path + '/api/message/post',
                data:data,
                dataType: 'application/json',
                type: 'POST',
                success: callback
            });
        };

        /**
         * Retrieve messages
         * @param callback
         */
        this.getMessages = function(callback) {
            $.getJSON(multiproject.req.base_path + "/api/message/list", {}, callback);
        };

        // Load juggernaut js resource
        $.ajax({
            url: multiproject.conf.juggernaut_js,
            dataType: "script",
            cache: true,
            async: false,
            success: function(xhr) {
                // Initiate Juggernaut from the resource objects
                self.juggernaut = new Juggernaut;
                // Register callbacks if already set and empty list
                $.each(self.callbacks, function(key, callback) {
                    self.juggernaut.subscribe(channelid, self.callbackParser(callback));
                });
                self.callbacks = [];
            }
        });

        return this;
    };

    /**
     *
     * @constructor
     */
    multiproject.api.Users = function() {
        /**
         * Retrieve users from REST API
         * @param {String} query for filtering results, from the fields defined with fields. Example: "Adam"
         * @param {Array} fields Fields to retrieve
         * @param callback Callback to execute once the results are found. JSON data is passed to callback.
         */
        this.getUsers = function(query, fields, callback) {
            fields = fields || ['id', 'username', 'firstname', 'lastname', 'email'];
            var data = {q:query, field:fields.join(',')};

            // Make AJAX request to fetch users
            $.getJSON(
                multiproject.req.base_path + "/api/user/list",
                data,
                callback
            );
        };

        /**
         * Retrieve data
         * @param username
         * @param userid
         */
        this.getUser = function(query, callback) {
            // Make AJAX request to fetch user
            $.getJSON(
                multiproject.req.base_path + "/api/user",
                query,
                function(json) {
                    var user = new multiproject.api.User(json);
                    return callback(user);
                }
            );
        };
    };

    /**
     *
     * @param data
     * @constructor
     */
    multiproject.api.User = function(data) {
        this.id = data.id || 0;
        this.username = data.username || 'anonymous';
        this.mail = data.mail || '';

        /**
         * Returns URL to user avatar
         */
        this.avatar_url = function(){

        };

        return this;
    };

    /**
     * jQuery plugin: UserProfileBox
     *
     * @example
     * $('div.user').UserProfileBox();
     * $('div.user').UserProfileBox({html:'<div class="mybox">custom</div>>'});
     *
     * @param opts
     * @return {*}
     * @constructor
     */
    $.fn.UserProfileBox = function(opts) {
        var self = this;
        var placeholder = '<div class="profilebox"><div class="wrapper loading"><div class="info-wrapper"></div></div></div>';

        // Close box and remove changes
        self.closeProfileBox = function(self, box, clicked){
            box.remove();
            // Reset HTML
            box = $(options.placeholder);
        };

        // Rendering profile box and bind actions to it
        self.renderProfileBox = function(self, box, clicked) {
            // If box is already visible, skip this
            if (box.is(':visible')) {
                return true;
            }

            // Load ready-rendered profile box
            var user = options.usercb(clicked);
            box.load(multiproject.req.base_path + '/user/' + user.username.trim() + '/profilebox');

            // Create box html to body and position it next to element
            box.appendTo('body');
            box.css('left', clicked.offset().left).css('top', clicked.offset().top + clicked.height());

            // Bind action for elements match with div.close
            box.find('div.close').click(function(event){ return self.closeProfileBox(box, clicked); });
        };

        // Callback for bound events
        self.toggleProfileBox = function(self, box, clicked){
            // Close if visible
            if (box.is(':visible')) {
                self.closeProfileBox(self, box, clicked);
            }
            // Show if missing
            else {
                self.renderProfileBox(self, box, clicked);
            }
        };

        // Update options, if given
        var defaults = {
            cb: function(data){},
            placeholder: placeholder,
            events: {'click':'toggleProfileBox'},
            usercb: function(clicked){
                // Callback for retrieving user id or name
                // Expects to get object like: {id:123} or {username:'username'}
                // This default implementation looks for format: Firstname Lastname (accountname)
                // and defaults to 'accountname'
                var txt = clicked.text();
                var result = txt.match(/\(([^)]*)\)/);
                // If no match is found, expect the value be username
                if (result === null) {
                    return {username:txt};
                }
                return {username:result[1]};
            }
        };
        var options = $.extend(defaults, opts || {});
        var box = $(options.placeholder);

        // Bind global closing actions: click outside or press ESC
        $(document).keyup(function(event){
            // Close box on ESC
            if (event.keyCode === 27) {
                self.closeProfileBox(self, box, this);
            }
        });
        $(document).click(function(event){
            if (box.has(event.target).length === 0){
                self.closeProfileBox(self, box, this);
            }
        });

        // Return jQuery chain-ability
        return this.each(function(){
            // If multiproject object is not available, skip this
            if (typeof(multiproject) === 'undefined' || typeof(multiproject.req) === 'undefined') {
                return false;
            }

            // Filter out the elements that already are profilebox links
            var clicked = $(this);

            // If descendant has a link or the content is empty, skip it
            if (clicked.has('a').length > 0 || clicked.text().trim().length === 0) {
                return true;
            }

            // Wrap inside an anchor
            clicked.wrapInner('<a href="#" class="profilebox-link"></a>');

            // Bind all the provided events to action
            $.each(options.events, function(eventName, callBack){
                clicked.unbind(eventName);
                clicked.bind(eventName, function(event){
                    event.preventDefault();
                    event.stopPropagation();
                    if (typeof(callBack) === 'string') {
                        self[callBack](self, box, clicked);
                    }
                    else {
                        callBack(self, box, clicked);
                    }
                });
            });
       });
    };

})(jQuery, window);

// Add string trim to IE7
String.prototype.trim=function(){return this.replace(/^\s\s*/, '').replace(/\s\s*$/, '');};
