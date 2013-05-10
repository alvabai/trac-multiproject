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
     * Simple cross-platform log facility
     * @param {Object}
     */
    multiproject.log = function(msg, level) {
        logLevels = {'debug':0, 'info':1, 'warning':2, 'error':3};
        showLogLevel = window.showLogLevel || 'debug';
        level = (level || 'debug').toLowerCase();

        if (typeof(window.console) === 'object' && level in logLevels && logLevels[level] >= logLevels[showLogLevel]) {
            window.console.log((level.toUpperCase() + ': ').rpad(8) + msg);
        }
    };

    // Formats the given date in human readable format
    var dateFormatter = function(date) { return date.toDateString(); };
    var dateFormats = {
        // Less than 24h
        86400: function(date) {
            // NOTE: getMinutes returns the value 0-59 -> do zero padding
            var minutes = String('0' + date.getMinutes()).slice(-2);
            if (date.getDay() === new Date().getDay()) {
                return date.getHours() + ':' + minutes;
            }
            return 'Yesterday ' + date.getHours() + ':' + minutes;
        },
        // Less tha 48h
        172800: function(date) { return 'Yesterday ' + date.getHours() + ':' + String('0' + date.getMinutes()).slice(-2); },
        // Less than 7 days
        604800: function(date) { return date.toDateString(); }
    };
    /**
     * Formats the javascript date objects into human readable format
     * @param {Date} date
     * @return {String} formatted date
     */
    multiproject.formatDate = function(date) {
        // IE8 has limited date parsing support, thus, this can be NaN
        if (isNaN(date)) {
            return '';
        }

        var now = new Date();
        var diff = (now.getTime() - date.getTime()) / 1000; // Value is in milliseconds
        $.each(dateFormats, function(maxdiff, formatter){
            if (diff < window.parseInt(maxdiff)) {
                dateFormatter = formatter;
                return false;
            }
        });
        return dateFormatter(date);
    };

    /**
     * Helper function to retrieve event position in browser compatible way
     * @param event
     * @return {Object}
     */
    multiproject.getPosition = function(event) {
        event = event || window.event;
        var posx = 0;
        var posy = 0;

        if (event.pageX || event.pageY) {
            posx = event.pageX;
            posy = event.pageY;
        }
        else if (event.clientX || event.clientY) {
            posx = event.clientX + document.body.scrollLeft + document.documentElement.scrollLeft;
            posy = event.clientY + document.body.scrollTop + document.documentElement.scrollTop;
        }

        return {left: posx, top: posy};
    };

    /**
     * Generates valid url based on given parameters.
     * If some of the parameters are not given, they are defaulted to current location
     * @param {Object} opts: Url elements like: {host: 'localhost', port: 443, secure: true, path: 'foo'}
     * @return {Object} Generated URL along with separate URL elements
     */
    multiproject.getUrl = function(opts) {
        opts = opts || {};

        var secure = false;
        if (opts.secure !== undefined) {
            secure = opts.secure;
        }

        if (secure === true) {
            opts.protocol = 'https:';
            opts.port = 443;
        }

        var host = window.location.host || 'localhost';
        if (opts.host && opts.host !== '') {
            host = opts.host;
        }

        var protocol = opts.protocol || window.location.protocol;
        var default_ports = {'http:': 80, 'https:': 443};

        // Port is empty if in default port (both http/https). Check protocol instead
        var port = default_ports[protocol];
        if (opts.port && opts.port !== 0) {
            port = opts.port;
        }

        var path = opts.path || '';

        // Add missing colon
        if (protocol.charAt(protocol.length-1) !== ':') {
            protocol += ':';
        }

        if (protocol === 'https:') {
            secure = true;
        }

        return {
            url: protocol + '//' + host + ':' + port + '/' + path,
            protocol: protocol,
            port: port,
            host: host,
            path: path,
            secure: secure

        };
    };

    /**
     * Extend jQuery to have session storage based caching for JSON requests.
     * Caching is implemented/provided by jStorage library.
     *
     * @example
     * $.getCachedJSON('key', 'http://server.com/path', {foo:'bar'}, function(json){
     *   alert('cached json:' + json);
     * });
     *
     */
    $.getCachedJSON = function(ckey, url, data, success, error, complete) {
        // Cache results using jStorage
        var storage = $.jStorage;
        if (storage) {
            var value = storage.get(ckey, null);
            if (value) {
                return success(value);
            }
        }
        // Default error handler
        error = error || function(jqXHR, textStatus, errorThrown){
            multiproject.log('Error in ajax request: ' + textStatus + '(' + jqXHR.status + ')');
            success({}, textStatus, jqXHR);
        };
        complete = complete || function(){};

        // Alternative
        $.ajax({
            url: url,
            dataType: 'json',
            data: data,
            success: function(data, textStatus, jqXHR){

                // Store output in session storage
                if (storage) {
                    storage.set(ckey, data);
                }

                // Call the success callback
                success(data, textStatus, jqXHR);
            },
            complete: complete,
            error: error
        });
    };

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
        var self = this;
        self.element = element;
        self.opts = undefined;

        /**
         * Callback for making a request. Does the AJAX request to backend
         * @param request
         * @param response
         */
        self.onRequest = function (request, response) {
            // Show loader class until response is shown
            self.element.addClass('loading');

            var keyword = self.element.val();

            var users = multiproject.api.Users();
            var fields = ['id', 'username', 'firstname', 'lastname', 'email'];

            // Use users api to fetch users
            users.queryUsers({query: keyword, fields: fields, limit: self.opts.limit, status: self.opts.status, cb: function(data){
                self.element.removeClass('loading');
                response(data);
            }});
        };

        /**
         * Callback when item is focused: Before focus is moved to an item (not selecting),
         * ui.item refers to the focused item.
         * @param event
         * @param ui
         */
        this.onFocus = function(event, ui) {
            self.element.val($.trim(ui.item.username));
            return false;
        };

        /**
         * Callback for item rendering
         * @param ul
         * @param item
         */
        self.onRender = function(ul, item){
            return $("<li></li>")
                .data( "item.autocomplete", item )
                .append(
                    "<a><strong>" + String((item.firstname || '') + " " + (item.lastname || '')).trim() + "</strong>" +
                    "<br/>" + (item.username || '') + "</a>")
                .appendTo(ul);
        };

        /**
         * Callback for making the selection
         * @param event
         * @param ui
         */
        self.onSelect = function(event, ui) {
            // TODO: Override if needed
            $(this).val(ui.item.username);
            return false;
        };

        /**
         * Callback to execute when field is clicked
         * @param {function} cb
         */
        self.onClick = function(event) {
            // TODO: Override if needed
        };

        /**
         * Callback for change event
         * @param event
         * @param ui
         */
        self.onChange = function(event, ui) {
            // TODO: Override if needed
            return false;
        };

        /**
         * Clears the current value
         */
        self.clear = function() {
            self.element.val("");
        };

        /**
         * Constructs the autocomplete field with the callbacks and options provided
         * @param {Object} opts Options
         */
        self.render = function() {
            // Set and extend autocomplete options
            // Bind events
            self.opts.source = self.onRequest;
            self.opts.change = self.onChange;
            self.opts.select = self.onSelect;
            self.opts.focus = self.onFocus;

            self.element.autocomplete(self.opts);
            self.element.data("autocomplete")._renderItem = self.onRender;
            self.element.click(this.onClick);
        };

        // Handle options
        var opt_defaults = {
            minLength: 2,
            fields: ['id', 'username', 'firstname', 'lastname'],
            // States: active, inactive, banned, disabled, expired
            status: ['active'],
            limit: 10
        };
        self.opts = $.extend(opt_defaults, (opts || {}));

        return self;
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
        this.generate = function(words, input_field) {
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
            $(input_field).val(self.username);
            return self.username;
        };

        /**
         * Function for checking if the given username conflicts
         * @param {String} username
         * @param {function} callback
         */
        this.checkConflict = function(callback, db_field, input_field) {
            var result = false;
            var username = input_field.val();
            var users = multiproject.api.Users();

            // Make AJAX request to fetch users
            users.queryUsers({query: username, fields: [db_field], limit:40, cb: function(data){
                // Iterate all the results and check if there are users with same username
                for(var entry in data) {
                    if(db_field == 'username'){
                        if (data[entry].username === username) {
                            result = true;
                            break;
                        }
                    }
                    else {
                        if (data[entry].email === username) {
                            result = true;
                            break;
                        }   
                    }
                }
                callback(result);
            }});
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
     * @example
     * var cbox = new multiproject.ui.ConfirmationBox("Are you really sure?");
     * // NOTE: Do not place confirmation box initialization inside the action because
     * // box needs to store it's state
     * $('input#mybutton').click(function(event){
     *    // return true / false to execute the default action
     *    // NOTE: open returns undefined for the first time because of asynchronous execution model
     *    return cbox.open(event) === true;
     * });
     *
     */
    multiproject.ui.ConfirmationBox = function(msg) {
        var self = this;
        self.confirmed = this.confirmed; // This will return undefined for the first time
        self.event = undefined;
        self.msg = msg || 'Are you sure?';

        /**
         * Opens the confirmation box
         * @return undefined when undecided, true on confirm, false on cancel (handy for executing the default event)
         */
        this.open = function(event, onConfirm, onCancel) {
            self.event = event;
            onConfirm = onConfirm || function(){};
            onCancel = onCancel || function(){};

            // If confirmation is already requested
            if (typeof self.confirmed !== 'undefined') {
                var result = self.confirmed;
                self.confirmed = undefined;
                return result;
            }
            // Otherwise, prevent default action and do confirmation
            else {
                self.event.preventDefault();
            }

            // Create element what to show as dialog
            var box = $(document.createElement('div'));
            box.text(self.msg);
            box.attr('id', 'confirmbox');
            box.dialog({
                resizable: false,
                height:140,
                title: 'Confirmation',
                modal: true,
                buttons: {
                    Confirm: function() {
                        onConfirm(self.event, box);

                        $(this).dialog("close");
                        box.remove();
                        // Fire same event again: this time with flag set
                        self.confirmed = true;
                        self.event.currentTarget[self.event.type]();
                    },
                    Cancel: function() {
                        onCancel(self.event, box);

                        $(this).dialog("close");
                        box.remove();
                        // Fire same event again: this time with flag set
                        self.confirmed = false;
                        self.event.currentTarget[self.event.type]();
                    }
                }
            });
            return self.confirmed;
        };

        return this;
    };

    multiproject.ui.NotifyBox = function(msg, title) {
        var self = this;
        self.msg = msg;
        self.title = title || 'Notification';

        /**
         * Opens the confirmation box
         * @return undefined when undecided, true on confirm, false on cancel (handy for executing the default event)
         */
        self.open = function() {
            // Create element what to show as dialog
            var box = $(document.createElement('div'));
            box.text(self.msg);
            box.attr('id', 'notifybox');
            box.dialog({
                resizable: false,
                height: 140,
                title: self.title,
                modal: true,
                buttons: {
                    OK: function() {
                        $(this).dialog("close");
                        box.remove();
                    }
                }
            });
        };

        return this;
    };

    /**
     *
     * @constructor
     */
    multiproject.api.Users = function() {
        var self = this;

        /**
         * Retrieve users from REST API
         * @param {Object} options
         * - query: String query to match with the field values
         * - fields: Array of fields to include in query (and results)
         * - limit: Limit to number of entries. Defaults to 10 (also backend has it's max limits)
         * - callback: Function to execute once the data is retrieved. The users JSON is passed to function
         * @param {String} query for filtering results, from the fields defined with fields. Example: "Adam"
         * @param {Array} fields Fields to retrieve
         * @param callback Callback to execute once the results are found. JSON data is passed to callback.
         */
        self.queryUsers = function(opts) {
            opts = opts || {};
            var query = opts.query || '';
            var fields = opts.fields || ['id', 'username', 'firstname', 'lastname', 'email'];
            var limit = opts.limit || 10;
            var callback = opts.cb || function(){};
            var status = opts.status || ['active'];

            var data = {
                q: query,
                limit: limit,
                field: fields.join(','),
                status: status.join(',')
            };
            // Make AJAX request to fetch users
            $.getJSON(
                multiproject.req.base_path + "/api/user/list",
                data,
                callback
            );
        };

        /**
         * Get user info based on given id or username
         * @param {Object} query: User id or username in object format: {id:123} or {username:"accountname"}
         * @param {function} callback: Function to call once the data is retrieved. The user data is passed to function.
         */
        self.getUser = function(query, callback) {
            var ckey = 'user-' + (query.id || query.username);

            // Make AJAX request to fetch user
            $.getCachedJSON(
                ckey,
                multiproject.req.base_path + "/api/user",
                query,
                function(json) {
                    var user = new multiproject.api.User(json);
                    return callback(user);
                }
            );
        };


        /**
         * Get users with exact ids or names
         * @param {Object} where: Array of user ids or names: {id:[]}
         * @param {Function} callback
         */
        self.getUsers = function(where, callback) {
            var users = [];
            var query = {};
            var field;
            var values;
            callback = callback || $.noop();

            if (where.id) {
                field = 'id';
            }
            else if (where.name) {
                field = 'name';
            }
            else {
                throw 'Either id or name must be provided';
            }

            // If only value is given, make it an array
            values = where[field];
            if (!$.isArray(values)) {
                values = [values];
            }

            // Iterate values and load user by user and put result in array
            $.each(values, function(index, value){
                query[field] = value;
                self.getUser(query, function(user){
                    users.push(user);
                    // Execute callback after every user: it should handle sequental invokes
                    callback(users);
                });
            });
        };

        /**
         * Returns the current user object
         * @param callback: Function to execute once user is retrieved, user object is passed to the function
         */
        self.getCurrentUser = function(callback) {
            self.getUser({username: multiproject.req.authname}, callback);
        };

        return self;
    };

    /**
     *
     * @param data
     * @constructor
     *
     */
    multiproject.api.User = function(data) {
        // NOTE: This object is serialized, thus no functions will be available after de-serializing
        this.id = data.id || 0;
        this.username = data.username || 'anonymous';
        this.mail = data.mail || '';
        this.displayName = data.displayname;
        this.firstname = data.firstname;
        this.lastname = data.lastname;

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
        };

        // Rendering profile box and bind actions to it
        self.openProfileBox = function(self, box, clicked) {
            // If box is already visible, skip this
            if (box.is(':visible')) {
                return true;
            }

            // Load ready-rendered profile box and show it once done
            var user = options.usercb(clicked);
            var user_name = user.username.trim().replace(" ", "%20");
            var probox_url = multiproject.req.base_path + '/user/' + user_name + '/profilebox';
            box.load(probox_url, function(){
                // Bind action for elements match with div.close
                box.find('div.close').click(function(event){ return self.closeProfileBox(box, clicked); });
            });

            // Create box html to body and position it next to element
            box.html($(placeholder).find('.wrapper'));
            box.appendTo('body');
            box.css('left', clicked.offset().left).css('top', clicked.offset().top + clicked.height());
        };

        // Callback for bound events
        self.toggleProfileBox = function(self, box, clicked){
            // Close if visible
            if (box.is(':visible')) {
                self.closeProfileBox(self, box, clicked);
            }
            // Show if missing
            else {
                self.openProfileBox(self, box, clicked);
            }
        };

        // Update options, if given
        var defaults = {
            cb: function(data){},
            placeholder: placeholder,
            events: {
                click: 'toggleProfileBox'
                /*
                mouseover: function(self, box, clicked) {
                    self.openProfileBox(self, box, clicked);
                    // Bind mouse out for box
                    box.unbind('mouseout');
                    box.bind('mouseout', function(event){
                        // Close profilebox if event coming outside of the box
                        var contains = $.contains(this, event.relatedTarget);
                        if (contains === false || contains === 0) {
                            self.closeProfileBox(self, box, clicked);
                        }
                    });
                },
                mouseout: function(self, box, clicked) {
                    var epos = multiproject.getPosition(self.event);
                    var boxpos = box.offset();

                    // Fire event only if does not happen next to box
                    if (Math.abs(boxpos.top - epos.top) >= (clicked.height() / 2)) {
                        self.closeProfileBox(self, box, clicked);
                    }
                }
                */
            },
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
        $(document).bind('click keydown', function(event){
            if (event.type === 'click') {
                self.closeProfileBox(self, box, this);
            }
            else if (event.type === 'keydown' && event.keyCode === 27) {
                self.closeProfileBox(self, box, this);
            }
            return true;
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

                    // Ensure the event is available
                    self.event = event;

                    // Fire event only it happens clearly outside

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

    /**
     * jQuery plugin: SiteAdminBox
     * Shows the site admin links
     *
     * @param opts
     * @return {*}
     * @constructor
     */
    $.fn.SiteAdminBox = function(opts) {
        var self = this;
        var placeholder = '<div class="siteadminbox"><div class="wrapper loading"><div class="info-wrapper"></div></div></div>';
        var defaults = {
            events: {
                click: 'toggleSiteAdminBox'
            },
            placeholder: placeholder
        };
        var options = $.extend(defaults, (opts || {}));
        var box = $(options.placeholder);

        // Close box and remove changes
        self.closeSiteAdminBox = function(self, box, clicked){
            box.remove();
            $('div.siteadminbox').remove();
        };

        // Rendering profile box and bind actions to it
        self.openSiteAdminBox = function(self, box, clicked) {
            // If box is already visible, skip this

            // FIXME: :visible sometimes returns false even if it is visible => additional length check
            if (box.is(':visible') || $('div.siteadminbox').length !== 0) {
                return true;
            }

            // Load ready-rendered profile box and show it once done
            box.load(multiproject.req.base_path + '/siteadmin/list', function(){
                // Bind action for elements match with div.close
                box.find('div.close').click(function(event){
                    return self.closeSiteAdminBox(self, box, clicked);
                });
            });

            // Create box html to body and position it next to element
            box.html($(placeholder).find('.wrapper'));
            box.appendTo('body');
            box.css('left', clicked.offset().left).css('top', clicked.offset().top + clicked.height());
        };

        // Callback for bound events
        self.toggleSiteAdminBox = function(self, box, clicked){
            // Close if visible
            // FIXME: :visible sometimes returns false even if it is visible => additional length check
            if (box.is(':visible') || $('div.siteadminbox').length !== 0) {
                self.closeSiteAdminBox(self, box, clicked);
            }
            // Show if missing
            else {
                self.openSiteAdminBox(self, box, clicked);
            }
        };

        // Bind global closing actions: click outside or press ESC
        $(document).bind('click keydown', function(event){
            if (event.type === 'click') {
                self.closeSiteAdminBox(self, box, this);
                return true;
            }
            else if (event.type === 'keydown' && event.keyCode === 27) {
                self.closeSiteAdminBox(self, box, this);
            }
            return true;
        });

        // Return jQuery chain-ability
        return this.each(function(){
            var clicked = $(this);

            // Bind all the provided events to action
            $.each(options.events, function(eventName, callBack){
                clicked.unbind(eventName);
                clicked.bind(eventName, function(event){
                    event.preventDefault();
                    event.stopPropagation();

                    // Ensure the event is available
                    self.event = event;

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
String.prototype.rpad=function(length, pad){
    pad = pad || ' ';
    return (this + new Array(length + 1).join(pad)).slice(0, length);
};

//Frontend check for project creation

$(".create_project_form").live("submit", function(){
    var check = true;

    if($('#prj_long_name').val().length < 2 || $.trim($('#prj_long_name').val()) == ""){
        check = false;
        alert("Project name must be 2 characters long");
    }
    else if(!$('#prj_short_name').val().match(/^[a-zA-Z0-9_-]*$/)){
        check = false;
        alert("Identifier should not contain scandic chars or spaces");
    }
    else if($('#prj_short_name').val().length < 2 || $.trim($('#prj_short_name').val()) == ""){
        check = false;
        alert("Identifier must be 2 characters long");
    }
    else if($('#prj_description').val().length < 8 || $.trim($('#prj_description').val()) == ""){
        check = false;
        alert("Project description must be 8 characters long");
    }
    else if($("#vcs_name").val().length < 3){
        check = false;
        alert("Repository name must be 3 characters long.");
    }
    else if(!$('#vcs_name').val().match(/^[a-zA-Z0-9_-]*$/)){
        check = false;
        alert("Repository name contains special chars!"+
        "Only alphanumerical, underscore and hyphen allowed.");
    }
    else if($('#vcs_name').val() == "git" || $('#vcs_name').val() == "hg" || $('#vcs_name').val() == "svn"){
        check = false;
        alert("Git, svn and hg are reserved values.");
    }
    return check;
});

//Project identifier automatically inserted

$('#prj_long_name').live("keyup", function(){
    var prj_name = $(this).val();
    prj_name = $.trim(prj_name.toLowerCase().replace(new RegExp(" ", "g"), "_").replace(new RegExp("ä", "g"), "a").replace(new RegExp("å", "g"), "a").replace(new RegExp("ö", "g"), "o"));
    $('#prj_short_name').val(prj_name);
    $('#vcs_name').val(prj_name);
});

$("#signOut").live("click", function(){
    $.removeCookie('trac_form_token', { path: '/home' });
});

//Add new ticket link to ticket tab
(function($, window, undefined) {
  $(document).ready(function(){ 
    var url = window.location.href;
    var location = url.split("/")[4];
    if (location == "ticket"){
      $("#ctxtnavitems ul .first").after("<li>|</li><li><a href=\"../newticket\">New ticket</a></li>");
    }
    if($("table.trac-clause").children().length > 2){
        //Remove display none if more than default setting in advanced filter
        $("#foldingtitle").removeClass('closed').addClass('open');
        $("#folding").css('display', 'block');
    }
  });
})(jQuery, window);
