/**
 * Javascript specific to messaging dialog:
 * Opens the multiproject.MessageDialog when a.messages-dialog link
 * is clicked.
 */
(function($, window, undefined) {
    var multiproject = window.multiproject || {};
    var users = new multiproject.api.Users();
    var messages = new multiproject.api.Messages();

    $(document).ready(function(){
        var dialog = new multiproject.ui.MessageDialog();

        // Bind click action to all links (also the generated ones)
        $(document).undelegate('a.messages-dialog', 'click');
        $(document).delegate('a.messages-dialog', 'click', function(){
            // Take the optional recipient information from the link href:
            // #recipient_id=<num> or #project_id=<num>
            var recipient = {};
            var link_href = this.attributes.href.value;
            var group_id_match = link_href.match(/group_id=(\d+)/);
            var user_id_match = link_href.match(/user_id=(\d+)/);

            // Open the dialog and pre-select the recipient group if set
            if (group_id_match !== null) {
                messages.getMessageGroup({group_id: group_id_match[1], cb: function(group){
                    dialog.open(group);
                }});
            }
            // User id parameter: construct the list of recipients and get group id
            else if (user_id_match !== null) {
                users.getCurrentUser(function(user){
                    users.getUser({id: user_id_match[1]}, function(recipient){
                        var recipients = [user.id, recipient.id];
                        messages.createMessageGroup({recipients: recipients, title: recipient.displayName}, function(group){
                            dialog.open(group);
                        });
                    });
                });
            }
            // Otherwise create group
            else {
                dialog.open();
            }
        });

        // On document load, check state and restore the dialog
        if (dialog.getState('open') === true && multiproject.req.authname !== 'anonymous') {
            messages.getMessageGroup({group_id: dialog.getState('group').id}, function(group){
                dialog.open(group);
            });
        }
    });
})(jQuery, window);

