/* Ticket query view specific javascripts */
$(document).ready(function() {
    // moved from query.html template
    initializeFilters();
    $("#group").change(function() {
        $("#groupdesc").enable(this.selectedIndex != 0)
    }).change();

    $("fieldset legend.foldable").enableFolding(false);

    /* Hide the filters for saved queries. */
    if (window.location.href.search(/[?&]report=[0-9]+/) != -1)
        $("#filters").toggleClass("collapsed");
    /* Hide the columns by default. */
    $("#columns").toggleClass("collapsed");

    $("#columnslist label").click(function(event) {
        if ($(this).is('.checked')) {
            $(this).removeClass('checked');
        } else {
            $(this).addClass('checked');
        }
    });

    $("#plusbutton, #columnstitle").click(function(event) {
        if ($("#columnsmenu").is('.open')) {
            $("#columnsmenu").removeClass('open');
        } else {
            $("#columnsmenu").addClass('open');
        }
    });
});
