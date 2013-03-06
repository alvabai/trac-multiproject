$(document).ready(function() {

    $('#mail').click(function(event) {
        var islocal = $('#local_user').val();

        if (islocal === "non_local"){
            alert("Email change not allowed for Coporate users.");
            $("#mail").prop('disabled', true);
           var lubox = multiproject.ui.NotifyBox("Email change not allowed for Coporate users.");
           lubox.open(); 
        }

    });  
});
