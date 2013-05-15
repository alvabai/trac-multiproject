/**
 * File contains javascript functionality related to notifications/announce
 */
$(document).ready(function(){
    var uri = window.location.href.toString().split("/");
    console.log("Location: "+uri[4]);
    if(uri[4] != "wiki"){
        var announceKey = 'multiproject-notifications';
        var announceValue = multiproject.conf.announce_id || announceKey;
        var announceBlock = $('div.announce');
        var cookieValue = $.cookie('multiproject-notifications');

        // Hide announcement box and set flag in cookie
        var hideAnnounceBox = function() {
            announceBlock.slideUp(300);
            $.cookie(announceKey, announceValue, {expires: 30, path: '/'});
        };

        // Bind events
        announceBlock.find('a.close').click(function(event) {
            event.preventDefault();
            hideAnnounceBox();
        });

        // Hide/show based on cookie status
        announceBlock.hide();
        if (cookieValue !== announceValue) {
            announceBlock.slideDown(300);
        }
    }
});