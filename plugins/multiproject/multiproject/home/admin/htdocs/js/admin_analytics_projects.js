/**
 * Javascript functionality specific to admin_analytics_project.html template
 */
$(document).ready(function(){
    var catfield = $("#categories");

    // Create ajax requester for autocomplete
    var requester = function (request, response) {
        // Show loader class until response is shown
        catfield.addClass('loading');
        var keyword = catfield.val();
        $.getJSON(window.multiproject.req.base_path +"/catautocomplete", {q:keyword}, function(data){
            response(data);
            catfield.removeClass('loading');
        });
    };
    catfield.autocomplete({source:requester, minLength:2});

    // Create date range selection
    var dates = $('input#starttime, input#endtime').datepicker({
        defaultDate: "+1w",
        showWeek: true,
        maxDate:"0D",
        numberOfMonths: 2,
        firstDay: 1,
        dateFormat: window.multiproject.conf.dateformat,
        onSelect: function( selectedDate ) {
            var option = this.id == "starttime" ? "minDate" : "maxDate",
                instance = $(this).data( "datepicker" ),
                date = $.datepicker.parseDate(
                    instance.settings.dateFormat ||
                    $.datepicker._defaults.dateFormat,
                    selectedDate, instance.settings );
            dates.not(this).datepicker("option", option, date);
        }
    });
});