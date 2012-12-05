/**
 * File contains the javascript functionality
 * specific to project admin basics view:
 *
 * - User autocomplete field to project author selection
 */
$(document).ready(function(){
    // Author autocomplete field
    var author_id = $('input#author_id');
    var author_text = $('input#author');

    // Create autocomplete field for project author
    var userfield = new multiproject.ui.UserField(author_text);

    // On selection, format text style
    userfield.onFocus = function(event, ui) {
        author_text.val(new String(ui.item.firstname + " " + ui.item.lastname + " (" + ui.item.username + ")").trim());
        return false;
    };

    // On select, update field value
    userfield.onSelect = function(event, ui) {
        author_id.val(ui.item.id);
        return false;
    };

    // When value is changed, clear author_id value if empty
    userfield.onChange = function(event, ui) {
        // Reset the author_id info
        if (!ui.item) {
            author_id.val("");
        }
        return false;
    };

    // Remove the id also on save because the onChange event does not happen when doing directly: clear -> save
    $('input[name="save"]').click(function(event) {
        if (author_text.val().trim().length == 0) {
            author_id.val("");
        }
    });

    userfield.render();
});
