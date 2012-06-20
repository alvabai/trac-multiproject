/* Folding functionality, the multiproject way. Instead of trac's folding,
 * this supports also jQuery effects in folding and unfolding.
 */
$(document).ready(function() {
    // toggle advanced folding box open/closed, when title is clicked
    $("#foldingtitle").click(function(event) {
        var ftitle = this;
        $('#folding').slideToggle('fast', function() {
            $(ftitle).toggleClass('open', $(this).is(":visible"));
        });
    });
});
