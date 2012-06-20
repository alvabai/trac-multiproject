/**
 * File hooks itself to different trac/multiproject views
 * by adding user profile box in account name listings
 */
(function($, window, undefined) {
    $(document).ready(function(){
        // Add links to summary team listing
        $('ul.team_members div a').UserProfileBox();

        // Add links to summary team listing
        $('table.listing.tickets td.owner').UserProfileBox();

        // Add links to author fields - avoid duplicates
        $('span.author, span.author a, a.author').UserProfileBox();

        // Add link on ticket properties
        $('table.properties td[headers="h_owner"], table.properties td[headers="h_reporter"]').UserProfileBox();

    });
})(jQuery, window);
