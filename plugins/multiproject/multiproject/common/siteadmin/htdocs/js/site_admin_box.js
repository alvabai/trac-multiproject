/**
 * Javascript specific to site admin box:
 * Opens the multiproject.SiteAdminBox when a.site_admin link
 * is clicked.
 */
(function($, window, undefined) {
    $(document).ready(function(){
        $('a.site_admin').SiteAdminBox();
    });
})(jQuery, window);
