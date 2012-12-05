/**
 * File subscribes itself to push notification channels
 */
(function($, window, undefined) {
    var ns = null;
    var users = null;
    var multiproject = window.multiproject;
    if (typeof multiproject === 'undefined') {
        return false;
    }

    var updateNotificationIndicator = function(notifications) {
        var messagesLink = $('a.messages');
        var indicator = messagesLink.find('.indicator');

        // Remove indicator if there are no unread notifications
        if (notifications.length === 0) {
            return indicator.remove();
        }

        // Add indicator if it is missing
        if (indicator.length === 0) {
            indicator = $('<span/>', {'class': 'indicator'});
            messagesLink.append(indicator);
        }
        // Flash the indicator on update, but only if amount changes
        else if(indicator.text() !== notifications.length.toString()){
            var speed = 200;
            var orgBackground = indicator.css('backgroundColor');
            indicator.animate({backgroundColor: "#fff"}, speed, function(){
               indicator.animate({backgroundColor: orgBackground}, speed);
            });
        }
        indicator.text(notifications.length);
    };

    $(document).ready(function(){
        // Fetch notifications if logged in
        if (multiproject.req.authname !== 'anonymous') {
            ns = new multiproject.api.NotificationSystem();
            ns.getNotifications({initiator: '', reset: false, type:'message', cb: updateNotificationIndicator});
        }
    });

})(jQuery, window);
