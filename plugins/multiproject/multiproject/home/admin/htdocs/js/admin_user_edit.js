(function($, window, undefined) {
$(document).ready(function(){
    // Bind confirmation on button click
    $('form input.confirm').click(function(event){
        return window.confirm('Are you sure you want to delete account?');
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
    var deputy_text = $('input#add_deputy');
    var fields = ['id', 'username', 'firstname', 'lastname', 'email'];
    var userfield = new multiproject.ui.UserField(author_text, {fields: fields});
    var deputyfield = new multiproject.ui.UserField(deputy_text, {fields: fields});
    userfield.onFocus = function(event, ui) {
        author_text.val(ui.item.firstname + " " + ui.item.lastname);
        return false;
    };

    deputyfield.onFocus = function(event, ui) {
        deputy_text.val(ui.item.firstname + " " + ui.item.lastname);
        return false;
    };

    userfield.onSelect = function(event, ui) {
        author_id.val(ui.item.id);
        return false;
    };
    userfield.onChange = function(event, ui) {
        // Reset the author_id info
        if (!ui.item) {
            author_id.val("");
        }
        return false;
    };
    // Remove the id also on save because the onChange event does not happen when doing directly: clear -> save
    $('input[name="save"]').click(function(event) {
        if (author_text.val().trim().length === 0) {
            author_id.val("");
        }
    });

    $(".remove_deputy").on("click", function(){
        var self = $(this).parent();
        var load_element = "Removing ..."+
        "<img src='/htdocs/theme/images/loading.gif' alt='Loading' style='margin: 0 auto; display: inline-block;' />";
        var send_url = window.location.href + "&remove_deputy="+$(this).prev().text().trim();
        if(confirm("Do you want to remove deputy?")){
            $(this).parent().addClass("ajax_load");
            $(this).parent().html(load_element);
            $.ajax({
                url: send_url,
                context: self,
                type: 'GET',
                dataType: 'text',
                success: function(response){
                    if(response == "success"){
                        $(this).remove();
                    }
                    else {
                        $(this).removeClass("ajax_load").addClass("ajax_load_failed").html("Removing failed, please try again later");
                    }
                },
                error: function(response) {
                    $(this).removeClass("ajax_load");
                    $(this).addClass("ajax_load_failed").html("Removing failed, please try again later");
                }
            });
        }
    });

    userfield.render();
    deputyfield.render();
});
})(jQuery, window);