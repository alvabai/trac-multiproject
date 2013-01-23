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
            var users = multiproject.api.Users();

            // Make AJAX request to fetch users
            users.queryUsers({query: username, fields: ['username'], limit:40, cb: function(data){
                // Iterate all the results and check if there are users with same username
                for(var entry in data) {
                    if (data[entry].username === username) {
                        result = true;
                        break;
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
     * Messaging dialog
     * @return {*}
     * @constructor
     * @example
     *
     * var dialog = new multiproject.ui.MessageDialog();
     * dialog.open();
     *
     */
    multiproject.ui.MessageDialog = function(opts) {
        var self = this;
        self.opts = {};
        self.mapi = multiproject.api.Messages();
        self.users = multiproject.api.Users();
        self.currentUser = undefined;
        self.currentGroup = {id: 0, recipients: []};
        self.currentLimit = 10;
        self.ns = multiproject.api.NotificationSystem();
        self.jstorage = $.jStorage;

        var messageTemplate =
            '<div class="message">' +
                '<div class="user"></div>' +
                '<div class="created"></div>' +
                '<div class="actions"></div>' +
                '<div class="text"></div>' +
            '</div>';

        // Instructions for Transparency how to render fields
        // NOTE: Name of the element placeholder (id/class/etc) cannot be same as name of the sub-object
        var renderDirectives = {
            text: {html: function(message) { return this.content; }},
            user: {text: function(message) { return this.sender ? this.sender.username : "unknown"; }},
            created: {text: function(message) { return this.created ? multiproject.formatDate(new Date(Date.parse(this.created))) : ''; }},
            actions: {html: function(message) {
                var removeMessage = '';
                // Add notification removal link if message has any
                if (this.notifications && this.notifications.length > 0) {
                    removeMessage += '<a href="#message_id=${id}" class="message-reset-notification" title="Mark message as read">ok</a>';
                }
                removeMessage += '<a href="#message_id=${id}" class="message-remove" title="Hide message, others will still see it">x</a>';
                return multiReplace(removeMessage, {id: this.id});
            }}
        };

        // Shows status from message posting in button label
        var showPostStatus = function(msg, timeout) {
            timeout = timeout || 1000;
            var msgArea = self.element.find('form#messages-send textarea:first');
            var placeholder = "Say something";
            setTimeout(function() {
                msgArea.attr('placeholder', placeholder);
            }, timeout);
            msgArea.attr('placeholder', placeholder);
            //button.val(msg);
        };

        // Send message callback
        var sendMessage = function(){
            var field = self.element.find('form#messages-send textarea:first');
            var message = field.val();

            // If empty, skip event
            if (typeof(message) === 'undefined' || message.length === 0) {
                return false;
            }

            var onSuccess = function() {
                // Remove the loading flag already after posting because we can't guarantee
                // the notification about new message gets received
                field.removeClass('loading');
                field.val("").focus();
            };

            var onError = function() {
                field.removeClass('loading');
                field.addClass('error');
            };

            // Send message using JS API
            field.removeClass('error');
            field.addClass('loading');
            self.mapi.postMessage({id: self.currentGroup.id}, message, onSuccess, onError);
        };

        // Initialize sending button in a dialog
        var initSendButton = function() {
            // Send message with button click
            self.element.find('form#messages-send input[type="submit"]').click(function(event){
                event.preventDefault();
                sendMessage();
            });
            // Send message with ctrl+enter
            $('form#messages-send textarea').keydown(function (event) {
                if (event.ctrlKey && event.keyCode === 13) {
                    event.preventDefault();
                    sendMessage();
                }
            });
        };

        /**
         * Render list of messages
         * @param json
         */
        var listMessages = function(json){
            // Store for internal use
            self.currentMessageList = json;

            // Show messages descending order (chat style): latest last
            json.reverse();

            // Hide/reveal get more messages link if the count is smaller than limit
            $('a.message-more').toggle(json.length >= self.currentLimit);

            // Ensure the old data gets removed: Remove the old data from Transparency cache and from DOM
            $('div.messagelist').render([], renderDirectives);
            $('div.messagelist *').remove();

            // Render data
            $('div.messagelist').render(json, renderDirectives);

        };

        /**
         * Callback function to invoke when notification is received
         * @param notification
         */
        var onNotification = function(notification) {
            multiproject.log('Received notification: ' + notification.type + ' ' + notification.id, 'info');

            // Load the actual message with notification info
            if (notification.type === 'message') {
                self.mapi.getMessage(notification.id, onMessage);
            }
            else if (notification.type === 'messagegroup') {
                self.mapi.getMessageGroup({group_id: notification.id}, onMessageGroupChange);
            }
        };

        /**
         * Subscribes to notifications
         * @param {object} notification: Notification in JSON format:
         *
         *   {type:'typename', action:'actionname': id:contentid, content:'notification content'}
         *
         */
        var initNotifications = function(channels) {
            // First, unsubscribe to existing channels
            self.ns.unsubscribe();

            multiproject.log('Subscribe to: ' + channels.join(','), 'DEBUG');

            // Subscribe to defined channels
            self.ns.subscribe(channels, function(notification){
                // NOTE: Empty notifications can be sent to inform clients to update their status
                if (!notification || !notification.id) {
                    return false;
                }

                onNotification(notification);
            });
        };

        /**
         * Bind message dialog specific events
         */
        var bindEvents = function() {
            // Bind events to messages: remove message
            $(document).undelegate('a.message-remove', 'click');
            $(document).delegate('a.message-remove', 'click', function(event){
                var messageElement = $(this).parentsUntil('div.message').parent();
                var link_href = this.attributes.href.value;
                var messageIdMatch = link_href.match(/message_id=(\d+)/);
                if (messageIdMatch !== null) {
                    // Give feed back right away
                    messageElement.addClass('removed');
                    removeMessage({id: messageIdMatch[1]}, function(){
                        // Fake the removal by removing the element
                        messageElement.hide();
                    });

                    // NOTE: Backend will take care of reseting the notification for removed messages
                }
            });
            // Bind events to messages: acknowledge notification
            $(document).undelegate('a.message-reset-notification', 'click');
            $(document).delegate('a.message-reset-notification', 'click', function(event){
                var link = $(this);
                var messageElement = link.parentsUntil('div.message').parent();
                var link_href = this.attributes.href.value;
                var messageIdMatch = link_href.match(/message_id=(\d+)/);
                if (messageIdMatch !== null) {
                    // Give feed back right away
                    link.addClass('removed');

                    // Send info to backed
                    self.mapi.markMessagesRead({message_id: messageIdMatch[1]}, function(){
                        link.hide();
                    });
                }
            });

            // Store message in local storage when focus is losed: message can be restored after reloading
            $(document).undelegate('form#messages-send textarea#content', 'blur');
            $(document).delegate('form#messages-send textarea#content', 'blur', function(event){
                self.setState({message: $(this).val()});
            });

            // Bind event click for getting more events
            $(document).undelegate('a.message-more', 'click');
            $(document).delegate('a.message-more', 'click', function(event){
                var moreLink = $(this);
                event.preventDefault();

                // Set loading flag to link
                moreLink.addClass('loading');

                // Increase the limit to get more messages, update the list and scroll back to current location
                self.currentLimit += 20;
                var currentPosition = $('div.messagearea')[0].scrollHeight;

                // Get messages
                self.mapi.getMessages({group: self.currentGroup, limit: self.currentLimit, cb: function(messages) {
                    // Remove loading flag
                    moreLink.removeClass('loading');

                    // Hide link on click and show it again if content is found
                    moreLink.hide();

                    // If more messages was found
                    if (!self.currentMessageList || self.currentMessageList.length !== messages.length) {
                        listMessages(messages);
                        // Scroll back to current position (from the bottom)
                        $('div.messagearea').scrollTop($('div.messagearea')[0].scrollHeight - currentPosition);

                        // Show the link again if new messages were really found
                        moreLink.show();
                    }
                }});
            });

            // Update group title after the change or after Enter press
            $(document).undelegate('input#group-name', 'change keydown');
            $(document).delegate('input#group-name', 'change keydown', function(event){

                // In keyup events, handle only enter presses
                if (event.type === 'keydown' && event.keyCode !== 13) {
                    return true;
                }
                event.preventDefault();

                var inputField = $(this);
                inputField.addClass('loading');

                self.currentGroup.title = $(this).val();
                self.mapi.updateMessageGroup(self.currentGroup, function(group){
                    inputField.removeClass('loading')
                });

                return false;
            });

            // On Leave click: remove from recipients, delete all messages and close dialog
            $(document).undelegate('form#messages-send input[name="leave"]', 'click');
            $(document).delegate('form#messages-send input[name="leave"]', 'click', function(event){
                event.preventDefault();

                // Hide all the messages for the user
                var deleteAll = function(){
                    // Immediate feedback
                    self.element.find('div.message').addClass('removed');

                    self.mapi.deleteMessages(self.currentGroup, function(){
                        // Remove current user from group if still
                        if ($.inArray(self.currentUser.id, self.currentGroup.recipients) !== -1) {
                            self.currentGroup.recipients = filterIntArray(self.currentGroup.recipients, self.currentUser.id);
                            self.mapi.updateMessageGroup(self.currentGroup, function(group){});
                        }
                        // Close the dialog
                        self.close();
                    });
                };

                var confirm = multiproject.ui.ConfirmationBox('Leave topic completely?');
                confirm.open(event, deleteAll);

                return false;
            });

            // On Mark all click: mark
            $(document).undelegate('form#messages-send input[name="mark"]', 'click');
            $(document).delegate('form#messages-send input[name="mark"]', 'click', function(event){
                event.preventDefault();
                var markAllRead = function(){
                    self.mapi.markMessagesRead({group_id: self.currentGroup.id}, function(response){
                        // Hide flags in message area
                        self.element.find('a.message-reset-notification').hide();
                    });
                };

                var confirm = multiproject.ui.ConfirmationBox('Mark all messages within this topic read?');
                confirm.open(event, markAllRead);
                return false;
            });
        };

        // Initiate autocomplete fields once dialog is opened
        var initAddRecipientField = function() {
            // Initiate autocomplete field
            var userfield = new multiproject.ui.UserField($('input#add-recipient'));

            // On select, fetch the messages
            userfield.onSelect = function(event, ui) {
                // Get and set user id
                var recipient_id = ui.item.id;

                // Update recipient list if user is not already there
                if ($.inArray(parseInt(recipient_id), self.currentGroup.recipients) === -1) {
                    self.currentGroup.recipients.push(recipient_id);
                    self.mapi.updateMessageGroup(self.currentGroup, selectRecipient);
                }

                // Clear the field
                userfield.clear();
                return false;
            };

            // Clear recipient selection when field is clicked
            userfield.onClick = function(event){
                event.preventDefault();
                userfield.clear();
                return false;
            };
            userfield.render();
        };

        /**
         * Scrolls down the message list
         */
        var scrollDown = function() {
            $('div.messagearea').scrollTop($('div.messagearea')[0].scrollHeight);
        };

        /**
         * Callback for messages
         * @param notification
         */
        var onMessage = function(message) {
            // If message is sent by currently selected recipient or by the user itself, show it in the list right away
            if (message.group.id !== self.currentGroup.id) {
                return false;
            }

            // Hide help placeholder
            self.element.find('div.placeholder').hide();

            // Append place holder in the end of the list and take it back
            var placeholder = $('div.messagelist').append(messageTemplate).children(':last');
            placeholder.render(message, renderDirectives);

            // Scroll down the list where the latest message is shown
            scrollDown();
        };

        /**
         * Callback to execute when group is changed
         * @param group
         */
        var onMessageGroupChange = function(group) {
            self.currentGroup = group;

            // If user is no longer in the recipients, show a dialog
            if ($.inArray(self.currentUser.id, group.recipients) === -1) {
                disableInputs();
            }
            else {
                enableInputs();
            }

            // Update message group name
            if (group.title && group.title.length > 0) {
                $('input#group-name').val(group.title);
            }
            else {
                $('input#group-name').attr('placeholder', 'Topic ' + self.currentGroup.id);
            }

            // Update recipient list
            updateRecipientList(group);
        };

        var removeMessage = function(message, callback) {
            self.mapi.deleteMessage(message, callback);
        };

        var disableInputs = function() {
            self.element.find('input[name="send"]').attr('disabled', 'disabled');
            self.element.find('input#group-name').attr('disabled', 'disabled');
            self.element.find('input#add-recipient').attr('disabled', 'disabled');
            self.element.find('textarea').attr('disabled', 'disabled');
            self.element.find('a.message-recipient-remove').hide();
            self.element.dialog('option', 'title', 'Messages (readonly)');
        };

        var enableInputs = function() {
            self.element.find('input[name="send"]').removeAttr('disabled');
            self.element.find('input#group-name').removeAttr('disabled');
            self.element.find('input#add-recipient').removeAttr('disabled');
            self.element.find('textarea').removeAttr('disabled');
            self.element.find('a.message-recipient-remove').show();
            self.element.dialog('option', 'title', 'Messages');
        };

        /**
         * Helper function to remove specified element from the array
         * @param elements
         * @param element
         * @return {Array}
         */
        var filterIntArray = function(elements, element) {
            return $.map(elements, function(recipient, index){
                if (window.parseInt(recipient) === window.parseInt(element)) {
                    return null;
                }
                return recipient;
            });
        };

        /**
         * Minimalistic template-like string replace
         * @param string
         * @param variables
         * @return {*}
         * @example
         * multiReplace('hello ${target}!', {target: 'world'})
         * // => 'hello world!'
         */
        var multiReplace = function(string, variables) {
            $.each(variables, function(key, value){
                // NOTE: Regexp must be used because of multiple replaces
                string = string.replace(new RegExp('\\${' + key + '}', 'gm'), value);
            });
            return string;
        };

        /**
         * Updates the recipients in the recipient list, leaving out the current user
         * @param {Object} group: Group info
         */
        var updateRecipientList = function(group) {
            self.currentGroup = group;

            // Add into recipient list
            var recipientListRender = {
                'recipient': {html: function(){
                    // Create element with name and removal link
                    var line =
                    '<span class="recipient ${flag}">' +
                        '<span class="user-icon"></span>' +
                        '<span class="user-text">${name}</span>' +
                        '<a href="#user_id=${id}" class="message-recipient-remove">' +
                            '<span class="remove-text">x</span>' +
                        '</a>' +
                    '</span>';
                    line = multiReplace(line, {
                        name: this.displayName,
                        id: this.id,
                        flag: self.currentUser.id === this.id ? 'you' : 'other'
                    });

                    return line;
                }}
            };

            // Shortcut function to adjust dialog contents manually
            var doResize = function() {
                afterResize(undefined, {size: {height: self.element.height(), width: self.element.width()}});
            };

            // Because of async user loading, fetch users first and render after
            if (self.currentGroup.recipients.length > 0) {
                self.users.getUsers({id: self.currentGroup.recipients}, function(users){
                    // Render values into list using Transparency
                    self.element.find('ul.recipients').render(users, recipientListRender);
                    doResize();
                });
            }
            else {
                self.element.find('ul.recipients').render([], recipientListRender);
                doResize();
            }

            // Reset limit
            self.currentLimit = 10;

            // Bind action to recipient removal: delegation needed because elements are created dynamicall
            $(document).undelegate('a.message-recipient-remove', 'click');
            $(document).delegate('a.message-recipient-remove', 'click', function(event){
                event.preventDefault();

                // Read user_id from link
                var user_id_match = this.href.match(/user_id=(\d+)/);
                if (user_id_match !== null) {
                    // Remove the selected user from recipients and update the list
                    var recipientsBefore = self.currentGroup.recipients;
                    self.currentGroup.recipients = filterIntArray(self.currentGroup.recipients, user_id_match[1]);

                    // Get/generate group from recipients
                    if ($(self.currentGroup.recipients).not(recipientsBefore).length == 0 && $(recipientsBefore).not(self.currentGroup.recipients).length == 0) {
                        // No changes
                        multiproject.log('No changes in recipients', 'debug');
                    }
                    else {
                        // NOTE: Update recipient list right away and do not provide a callback for update msg group
                        // we're getting the message group change notification anyway
                        updateRecipientList(self.currentGroup);
                        self.mapi.updateMessageGroup(self.currentGroup);
                    }

                }
                return false;
            });
        };

        /**
         * Callback to execute
         */
        var updateMessageArea = function(group) {
            // Restore the message in textarea if the group is same
            var message = '';
            var state = self.getState();
            // NOTE: Additional checks for FF
            if (typeof state !== 'undefined' && 'group' in state && group.id === state.group.id) {
                message = state.message;
            }
            self.element.find('textarea#content').val(message);
        };

        /**
         * Callback to execute on when new recipient is selected in the dialog
         * @param {Object} group: Group info like {id:123}
         */
        var selectRecipient = function(group) {
            // Update shared variable
            self.currentGroup = group || {id: 0, recipients: [self.currentUser.id]};

            // Get messages for selected group if not empty
            if (self.currentGroup !== 0) {
                self.mapi.getMessages({group: self.currentGroup, cb: function(messages) {
                    // Hide placeholder if
                    if (messages.length > 0) {
                        self.element.find('div.placeholder').hide();
                    }
                    else {
                        self.element.find('div.placeholder').show();
                    }

                    listMessages(messages);
                    // Scroll down the list
                    scrollDown();
                }});
            }

            // Store recipient info in state
            updateMessageArea(self.currentGroup);
            self.setState({group: self.currentGroup, message: ''});
            updateRecipientList(self.currentGroup);

            // Enable disabled input fields
            if ($.inArray(self.currentUser.id, group.recipients) !== -1) {
                enableInputs();

                // Show/Restore get more messages link
                $('a.message-more').show();

                // Focus on message field after selecting the recipient
                var messageField = self.element.find('form#messages-send textarea:first');
                messageField.focus(function(event){
                    messageField.click();
                    return false;
                });
            }
            else {
                disableInputs();
            }
        };

        /**
         * Resize message list after dialog resize
         * @param event
         * @param ui
         */
        var afterResize = function(event, ui) {
            var messageRecipient = self.element.find('div.recipient');
            var messageArea = self.element.find('div.messagearea');
            var messageSend = self.element.find('div.messagesend');
            var addRecipient = self.element.find('input#add-recipient[type="text"]');
            var groupName = self.element.find('input#group-name[type="text"]');

            var dialogHeight = ui.size.height;

            // TODO: Find proper way to calculate
            var heightFactor = 120;

            // Resize content
            messageArea.height(dialogHeight - messageRecipient.height() - messageSend.height() - heightFactor);
            self.element.find('textarea, input#recipient[type="text"]').width(messageArea.width());
            addRecipient.width(addRecipient.parent().width() - 4);
            groupName.width(groupName.parent().width() - $('label[for="group-name"]').width() - 15);

            // Store size also in storage
            self.setState({width: ui.size.width, height: ui.size.height});
        };

        /**
         * Store dialog position and state after move
         * @param event
         * @param ui
         */
        var afterMove = function(event, ui) {
            // Store new position to webstore/cookie
            //self.jstorage.set('msgdialog', {position: [ui.position.left, ui.position.top]});
            self.setState({position: [ui.position.left, ui.position.top]});
        };

        /**
         * Returns the dialog state stored in cookie/webstore
         * @param stateKey
         * @param defaultValue
         * @return {*}
         */
        self.getState = function(stateKey, defaultValue) {
            var win = $(window);
            var defaults = {
                position: [Math.round((win.width() - self.opts.width) / 2), Math.round((win.height() - self.opts.height) / 2)],
                open: false
            };
            var state = $.extend(defaults, (self.jstorage.get('msgdialog') || {}));

            if (typeof stateKey !== 'undefined') {
                return state[stateKey] || defaultValue;
            }
            return state || defaultValue;
        };

        /**
         * Stores the state to webstore/cookie. The state can be only partial: it get's merged with the values
         * already stored in the state.
         * @param state {position: [x,y], recipient:, open: bool}
         */
        self.setState = function(state) {
            state = state || {};
            state = $.extend(self.getState(), state);
            self.jstorage.set('msgdialog', state);
        };

        /**
         * Returns the dialog position
         * @return {Object} position
         */
        self.getPosition = function() {
            return self.element.dialog('option', 'position');
        };

        /**
         *
         * @param position
         * @return {*}
         */
        self.setPosition = function(position) {
            self.setState({position: position});
            return self.element.dialog('option', 'position', position);
        };

        /**
         * Method for closing the dialog
         */
        self.close = function() {
            if (typeof(self.ns) !== 'undefined') {
                self.ns.unsubscribe();
            }
            self.element.remove();
            self.setState({open: false});
        };

        /**
         * Opens the dialog
         * @param {Object} group: Optional group information. If empty, the currentGroup selection is reset
         * @param {Function} cb: Callback to execute after the dialog is opened
         */
        self.open = function(group, cb) {
            cb = cb || function(){};
            var state = self.getState();
            self.opts = $.extend(self.opts, state);

            // Open dialog by retrieving data/HTML from backend
            // and restore the state (position, size, recipient, message etc.)
            var loadDialog = function(group) {

                $.ajax({
                    url: multiproject.req.base_path + '/message/dialog',
                    data: {},
                    dataType: 'html',
                    success: function(data) {
                        self.element.html(data);

                        initAddRecipientField();
                        initSendButton();
                        selectRecipient(group);
                        onMessageGroupChange(group);

                        // Update state
                        self.setState({open: true});

                        // Manually execute resize callback to get content properly aligned
                        afterResize(undefined, {size: {height: state.height, width: state.width}});

                        // TODO: Parameters to pass?
                        cb();
                    }
                });

                // Open the dialog right away (contents will be updated after ajax request completes
                self.element.dialog(self.opts);
            };

            // NOTE: Load current user in object variable - not necessary needed by dialog
            self.users.getCurrentUser(function(user){
                // Store as shared variable
                self.currentUser = user;

                // Initialize current group
                self.currentGroup.recipients.push(user.id);

                // No group / create new group
                if (typeof group === 'undefined') {
                    self.mapi.createMessageGroup({recipients: [self.currentUser.id]}, function(group){
                        loadDialog(group);
                    });
                }
                // Open existing group: loads messages, updates listing etc.
                else {
                    loadDialog(group);
                }

                // Subscribe to new message from recipient specific channel
                initNotifications([self.ns.generateChannelName({user_id: self.currentUser.id})]);

                // Bind message dialog related events
                bindEvents();
            });

        };


        // Handle options
        var win = $(window);
        self.opts = $.extend({
            zIndex: 400,
            width: 400,
            height: 500,
            minWidth: 350,
            minHeight: 350,
            close: self.close,
            title: 'Messages',
            resizeStop: afterResize,
            dragStop: afterMove
        }, (opts || {}));

        // Create placeholders for dialogs in document
        // TODO: A better way to do this?

        // Messages dialog
        self.element = $('div#messages-dialog');
        if (self.element.size() !== 1) {
            self.element.remove();
            self.element = $('body').append('<div id="messages-dialog"></div>').find('div#messages-dialog:first');
        }

        return self;
    };




    /**
     * JavaScript API for subscribing notification service built on top of Juggernaut.
     * Juggernaut resources loaded once NotificationSystem.subscribe() is invoked.
     * The URL of the Juggernaut application.js is defined in MultiProject configuration:
     *
     * - juggernaut_secure: true / false
     * - juggernaut_host: host name or ip to juggernaut service / where application.js is
     * - juggernaut_port: port to juggernaut service
     *
     * @return {*}
     * @constructor
     * @example
     *
     * ns = new multiproject.api.NotificationSystem();
     * // TIP: You can use generateChannelName(obj) function to generate names
     * ns.subscribe(['ch1', 'ch2'], function(notification){
     *     // Notification is in JSON format
     *     window.alert("Received notification: " + notification)
     * });
     *
     */
    multiproject.api.NotificationSystem = function() {
        var self = this;
        self.juggernaut = undefined;
        self.channels = [];

        /**
         * Loads juggernaut resource from remote application.js
         * @param callback: Callback to execute once Juggernaut is loaded
         */
        var loadJuggernaut =  function(callback) {
            callback = callback || function(){};

            // Generate and get appropritate defaults
            var juggernaut_url = multiproject.getUrl({
                secure: multiproject.conf.juggernaut_secure,
                host: multiproject.conf.juggernaut_host,
                port: multiproject.conf.juggernaut_port,
                path: 'application.js'
            });

            // Load juggernaut js resource
            $.ajax({
                url: juggernaut_url.url,
                dataType: "script",
                cache: true,
                async: false,
                success: function(xhr) {
                    // Initiate Juggernaut from the resource objects
                    // NOTE: javascript objects are in local namespace after loading
                    if (typeof(Juggernaut) !== 'undefined') {
                        // Enable flash based solution for non-websocket capable browsers
                        window.WEB_SOCKET_SWF_LOCATION = juggernaut_url.url.replace('application.js', 'WebSocketMain.swf');
                        self.juggernaut = new Juggernaut({
                            secure: juggernaut_url.secure,
                            port: juggernaut_url.port,
                            reconnect: false, // <- reconnect when timed out?
                            transports: multiproject.conf.juggernaut_transports
                        });

                        // Juggernaut is loaded, user can start subscribing channels etc.
                        callback(self.juggernaut);
                    }
                }
            });
        };

        /**
         * Juggernaut returns string but we're sending json in it:
         * this callback generator is used to parse JSON string into JSON and pass it for the callback
         * @param callback
         * @return {Function}
         */
        this.callbackParser = function(callback) {
            callback = callback || function(){};
            return function(jsonstr) {
                // If data is already JSON
                if (typeof(jsonstr) === 'object') {
                    return callback(jsonstr);
                }

                var json = $.parseJSON(jsonstr);
                return callback(json);
            };
        };

        /**
         * Subscribes to channel message. Provided callback is invoked
         * message message is received
         * @param {Array} channels to listen
         * @param callback
         */
        this.subscribe = function(channels, callback) {
            if (typeof(self.juggernaut) !== 'undefined') {
                self.channels = self.channels.concat(self.channels, channels);
                self.juggernaut.subscribe(channels, self.callbackParser(callback));
            }
            else {
                // Put subscription into callbacks variable where they are read once Juggernaut is loaded
                loadJuggernaut(function(juggernaut){
                    self.channels = self.channels.concat(self.channels, channels);
                    juggernaut.subscribe(channels, self.callbackParser(callback));
                });
            }
        };

        /**
         * Un-subscribe notifications.
         * @param {Array} channels: Channels to unsubscribe to. If empty, all the already subscribed channels are un-subscribed.
         */
        this.unsubscribe = function(channels) {
            channels = channels || self.channels;

            // Update the internal channel list
            var updated_channels = [];
            $.each(channels, function(index, channel){
                if ($.inArray(channel, channels)) {
                    updated_channels.push(channel);
                }
            });

            if (typeof(self.juggernaut) !== 'undefined' && channels.length > 0) {
                self.juggernaut.unsubscribe(channels);
                multiproject.log('Unsubscribed from: ' + channels, 'info');
            }

            if (updated_channels.length > 0) {
                multiproject.log('Subscribed channels: ' + channels, 'info');
            }
            self.channels = updated_channels;
        };

        /**
         * Retrieve received/missed notifications and execute given
         * callback for them
         *
         * @param {String} initiator: Username who initiated the notification. Can be left as empty
         * @param {Bool} reset: Reset the notifications after fetching. Defaults to false
         * @param {function} cb: Callback to execute. An array of notifications objects is passed to callback
         */
        this.getNotifications = function(opts) {
            opts.initiator = opts.initiator || '';
            opts.type = opts.type || '';
            opts.reset = opts.reset || false;
            opts.cb = opts.cb || function(){};

            var users = new multiproject.api.Users();
            users.getCurrentUser(function(user) {
                $.getJSON(multiproject.req.base_path + "/api/notification/list", {
                    user_id: user.id,
                    reset: opts.reset.toString(),
                    type: opts.type,
                    initiator: opts.initiator
                }, opts.cb);
            });
        };

        /**
         * Get and optionally reset the notification
         * @param {Object} opts:
         * - id: Id of the content type where notification was sent about
         * - type: Type of the content where notification was sent about
         * - reset: true / false
         * - cb: Callback to execute
         * @example
         * getNotification({id:2, type: 'message', reset: true, cb: function(notification)})
         */
        this.getNotification = function(opts) {
            opts.cb = opts.cb || $.noop();
            var users = new multiproject.api.Users();
            users.getCurrentUser(function(user) {
                $.getJSON(multiproject.req.base_path + "/api/notification", {
                    id: opts.id,
                    reset: opts.reset.toString(),
                    type: opts.type,
                    initiator: opts.initiator
                }, opts.cb);
            });
        };

        /**
         * Returns the name of the channel based on given params
         */
        this.generateChannelName = function(data) {
            // TODO: No longer needed?
            if (typeof(data) === 'object') {
                if ('user_id' in data) {
                    return 'uid-' + data.user_id;
                }
            }

            return 'global';
        };

        return this;
    };

    /**
     * JavaScript API for accessing messages
     * @constructor
     */
    multiproject.api.Messages = function() {
        var self = this;
        var callGroup = function(opts, action) {
            action = action || 'view';
            opts.cb = opts.cb || function(){};
            opts.title = opts.title || '';
            opts.recipients = opts.recipients || [];

            multiproject.log('Message group ' + action + ': ' + (opts.id || opts.group_id), 'debug');

            // NOTE: If value is unidentified, the key is left out from query
            $.getJSON(multiproject.req.base_path + "/api/message/group", {
                    recipients: opts.recipients.join(','),
                    group_id: opts.group_id || opts.id,
                    id: opts.id || opts.group_id,
                    action:action, title:
                    opts.title
                },
                function(group) {
                    opts.cb(group);
                }
            );
        };

        /**
         * Post message to channel
         * @param {Object} group: Message group like {id: 123}
         * @param {String} msg: Message to send
         * @param callback: Optional callback to execute after successful posting
         */
        this.postMessage = function(group, msg, callback, error) {
            callback = callback || function(){};
            error = error || function(jqXHR, textStatus, errorThrown){
                multiproject.log('Error in ajax request: ' + textStatus + '(' + jqXHR.status + ')');
                callback({}, textStatus, jqXHR);
            };
            // Read form validation token from users cookie for post requests
            var ftoken = $.cookie('trac_form_token');
            var data = {content: msg, '__FORM_TOKEN': ftoken, group_id: group.id};

            multiproject.log('Sending message to group ' + group.id);

            $.ajax({
                url: multiproject.req.base_path + '/api/message/post',
                data: data,
                dataType: 'json',
                type: 'POST',
                success: callback,
                error: error
            });
        };

        /**
         * Retrieve messages asynchronously
         * @param {Object} opt:
         * - group: Message group like {id: 123}
         * - limit: Number of messages to retrieve
         * - cb: Optional callback to run once messages are retrieve
         */
        this.getMessages = function(opt) {
            opt.cb = opt.cb || $.noop();
            opt.limit = opt.limit || 10;

            var params = {group_id: opt.group.id, limit: opt.limit};
            $.getJSON(multiproject.req.base_path + "/api/message/list", params, opt.cb);
        };

        /**
         * Retrieve messages asynchronously
         * @param {object} recipient: recipient_id or project_id
         * @param {function} callback: Callback to run once messages are retrieve
         * @example
         * // Message format
         * {
         * id: 123,
         * content: 'My message to you',
         * sender: {id: 532, username: 'myaccount'},
         * recipients: [{400, username: 'youraccount'}, ]
         * }
         */
        this.getMessage = function(message_id, callback) {
            multiproject.log('Getting message: ' + message_id, 'debug');
            var users = new multiproject.api.Users();
            $.getJSON(multiproject.req.base_path + "/api/message", {message_id: message_id}, function(message) {
                users.getCurrentUser(function(user) {
                    message.sender.avatar_url = user.avatar_url;
                    callback(message);
                });
                self.callbacks = [];
            });
        };

        /**
         * Get message group info based on recipients
         * @param {Object} opts: Parameter options:
         * - recipients: Array of user ids (optional: either recipients or group_id needs to be provided)
         * - group_id: Group id as in integer (optional: either recipients or group_id needs to be provided)
         * - callback: Callback to execute after fetching the data. The group is passed as to callback
         */
        this.getMessageGroup = function(opts, callback) {
            opts.cb = opts.cb || callback;
            callGroup(opts, "view");
        };

        /**
         * Update existing message group recipient info using opts parameters:
         * - group_id: Message group id
         * - recipients: List of recipient ids
         * @param opts
         */
        this.updateMessageGroup = function(opts, callback) {
            opts.cb = opts.cb || callback;
            callGroup(opts, "update");
        };

        /**
         * Create message group from the recipients using opts parameters:
         * - group_id: Message group id
         * - recipients: List of recipient ids
         * @param opts
         */
        this.createMessageGroup = function(opts, callback) {
            opts.cb = opts.cb || callback;
            callGroup(opts, "create");
        };

        /**
         * Delete (hide) message
         * @param message
         * @param callback
         */
        this.deleteMessage = function(message, callback) {
            $.getJSON(multiproject.req.base_path + "/api/message/delete",
                {message_id: message.id},
                callback
            );
        };

        /**
         * Delete (hide) all message in a group
         * @param group
         * @param callback
         */
        this.deleteMessages = function(group, callback) {
            $.getJSON(multiproject.req.base_path + "/api/message/delete",
                {group_id: group.id},
                callback
            );
        };

        /**
         * Mark one or all group messages read
         * @param {Object} opts: Parameters group_id or message_id expected. Example: {group_id: 123}
         * @param {Function} callback: Callback to execute afterwards. JSON response is provided to callback
         */
        this.markMessagesRead = function(opts, callback) {
            multiproject.log('Marking messages read', 'info');
            $.getJSON(multiproject.req.base_path + "/api/message/markread",
                opts,
                callback
            );
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
            box.load(multiproject.req.base_path + '/user/' + user.username.trim() + '/profilebox', function(){
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
     * jQuery plugin: UserMessagesList
     * Shows the list of message groups
     *
     * @example
     * $('div.user').UserMessagesBox();
     * $('div.user').UserMessagesBox({html:'<div class="mybox">custom</div>>'});
     *
     * @param opts
     * @return {*}
     * @constructor
     */
    $.fn.UserMessagesBox = function(opts) {
        var self = this;
        var placeholder = '<div class="messagesbox"><div class="wrapper loading"><div class="info-wrapper"></div></div></div>';
        var defaults = {
            events: {
                click: 'toggleMessagesBox'
                /*
                mouseover: function(self, box, clicked) {
                    self.openMessagesBox(self, box, clicked);
                    // Bind mouse out for box
                    box.unbind('mouseout');
                    box.bind('mouseout', function(event){
                        // Close profilebox if event coming outside of the box
                        var contains = $.contains(this, event.relatedTarget);
                        if (contains === false || contains === 0) {
                            self.closeMessagesBox(self, box, clicked);
                        }
                    });
                },
                mouseout: function(self, box, clicked) {
                    var epos = multiproject.getPosition(self.event);
                    var boxpos = box.offset();

                    // Fire event only if does not happen next to box
                    if (Math.abs(boxpos.top - epos.top) >= (clicked.height() / 2)) {
                        self.closeMessagesBox(self, box, clicked);
                    }
                }
                */
            },
            placeholder: placeholder
        };
        var options = $.extend(defaults, (opts || {}));
        var box = $(options.placeholder);

        // Close box and remove changes
        self.closeMessagesBox = function(self, box, clicked){
            box.remove();
            $('div.messagesbox').remove();
        };

        // Rendering profile box and bind actions to it
        self.openMessagesBox = function(self, box, clicked) {
            // If box is already visible, skip this

            // FIXME: :visible sometimes returns false even if it is visible => additional length check
            if (box.is(':visible') || $('div.messagesbox').length !== 0) {
                return true;
            }

            // Load ready-rendered profile box and show it once done
            box.load(multiproject.req.base_path + '/message/list', function(){
                // Bind action for elements match with div.close
                box.find('div.close').click(function(event){
                    return self.closeMessagesBox(self, box, clicked);
                });
            });

            // Create box html to body and position it next to element
            box.html($(placeholder).find('.wrapper'));
            box.appendTo('body');
            box.css('left', clicked.offset().left).css('top', clicked.offset().top + clicked.height());
        };

        // Callback for bound events
        self.toggleMessagesBox = function(self, box, clicked){
            // Close if visible
            // FIXME: :visible sometimes returns false even if it is visible => additional length check
            if (box.is(':visible') || $('div.messagesbox').length !== 0) {
                self.closeMessagesBox(self, box, clicked);
            }
            // Show if missing
            else {
                self.openMessagesBox(self, box, clicked);
            }
        };

        // Bind global closing actions: click outside or press ESC
        $(document).bind('click keydown', function(event){
            if (event.type === 'click') {
                self.closeMessagesBox(self, box, this);
                return true;
            }
            else if (event.type === 'keydown' && event.keyCode === 27) {
                self.closeMessagesBox(self, box, this);
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
    return check;
});

//Project identifier automatically inserted

$('#prj_long_name').live("keyup", function(){
    var prj_name = $(this).val();
    prj_name = $.trim(prj_name.toLowerCase().replace(new RegExp(" ", "g"), "_").replace(new RegExp("ä", "g"), "a").replace(new RegExp("å", "g"), "a").replace(new RegExp("ö", "g"), "o"));
    $('#prj_short_name').val(prj_name);
});