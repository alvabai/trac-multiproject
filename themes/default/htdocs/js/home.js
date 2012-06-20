/*-------- Put js utility methods needed on home project here ------------*/


/*-------- Create project form scripts -------------*/
function scm_source() {
    if($('#vcsparent').css("display") == "none") {
        $('#advanced_options').css("cursor", "progress")

        $('#vcsparent').load(
                "forkables",
                function(data) {
                    $('#advanced_options').css("cursor", "default")
                    $('#vcsparent').css("display", "block");
                    $('#vcstype').css("display", "none");
                    $('#scm_source').html("Create");
                    $('#selected_scm_source').html("Clone");
                    $('#setups').css("display", "none");
                    $('#scm_source').attr("title", "Create new repository");
                }
            );
    } else {
        $('#vcsparent').css("display", "none");
        $('#vcsparent').html("");
        $('#vcstype').css("display", "block");
        $('#scm_source').html("Clone");
        $('#selected_scm_source').html("Create");
        $('#setups').css("display", "block");
        $('#scm_source').attr("title", "Clone repository from existing project");
    }
    $('body').css("cursor", "auto")
}
