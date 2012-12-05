/**
 * Javascript specific to messaging listing:
 * Opens the multiproject.UserMessageBox when a.messages-list link
 * is clicked.
 */
(function($, window, undefined) {
    $(document).ready(function(){
        $('a.messages').UserMessagesBox();
    });
})(jQuery, window);
