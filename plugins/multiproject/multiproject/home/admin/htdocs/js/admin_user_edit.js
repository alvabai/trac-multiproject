$(document).ready(function(){
    // Bind confirmation on button click
    $('form input.confirm').click(function(event){
        return confirm('Are you sure you want to delete account?');
    });

    // Create date range selection
    var dates = $('input#expires').datepicker({
        showWeek: true,
        minDate: "-1D",
        maxDate: "+12M",
        numberOfMonths: 1,
        firstDay: 1,
        dateFormat: multiproject.conf.dateformat
    });

    // Author autocomplete field
    var author_id = $('input#author_id');
    var author_text = $('input#author');
    var userfield = new multiproject.ui.UserField(author_text);
    userfield.onFocus = function(event, ui) {
        author_text.val(ui.item.firstname + " " + ui.item.lastname);
        return false;
    };
    userfield.onSelect = function(event, ui) {
        author_id.val(ui.item.id);
    };
    userfield.onChange = function(event, ui) {
        // Reset the author_id info
        if (!ui.item) {
            author_id.val("");
        }
        return true;
    };
    // Remove the id also on save because the onChange event does not happen when doing directly: clear -> save
    $('input[name="save"]').click(function(event) {
        if (author_text.val().trim().length == 0) {
            author_id.val("");
        }
    });

    userfield.render();
});