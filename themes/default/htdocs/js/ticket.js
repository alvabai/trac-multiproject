/*
 * Single ticket view specific javascript for nokia theme. Consists of autocomplete
 * hooks and the cc ui component for tickets.
 */
var $ = jQuery;
$(document).ready(function() {
    var opts = {
        minLength: 2,
        limit: 5
    };
    var multiproject = window.multiproject;

    $("div.description").find("h1,h2,h3,h4,h5,h6").addAnchor(_("Link to this section"));
    $(".foldable").enableFolding(false, true);

    /* Autocomplete support for adding people into the CC list. Not always present, so
     * need to handle exceptions here.
     */
    try {
        var cc_user_field = new multiproject.ui.UserField($("#add_cc_list_member"), opts);
        cc_user_field.onSelect = function() {
            return addUserClick();
        };
        $("#add_cc_button").click(function() {
            addUserClick();
        });
        cc_user_field.render();
    } catch(e) {
    }

    /* Autocomplete support for changing assignee of a ticket, the field is not
     * there when creating new ticket, so need to handle exceptions
     */
    try {
        var assignee_field = new multiproject.ui.UserField($("#action_reassign_reassign_owner"), opts);
        assignee_field.render();
    } catch(e) {
    }

    /* Autocomplete support for selecting a new ticket owner */
    try {
        var reporter_field = new multiproject.ui.UserField($("#field-reporter"), opts);
        reporter_field.render();
    } catch(e) {
    }

    /* Bind all remove buttons to remove button click */
    $(".remove_user_btn").click(function() {
        removeUserClick($(this));
    });

    /* Autocomplete support for owner field, which is not always present */
    try {
        var owner_field = new multiproject.ui.UserField($("#field-owner"), opts);
        owner_field.render();
    } catch(e) {
    }

    $("#field-summary").click(function() {
        if ( $(this).val() === "enter a brief description") {
            $(this).val("");
        }
        $(this).addClass("active");
    });
    $("#field-summary").blur(function() {
        if ( $(this).val() === "") {
            $(this).removeClass("active");
            $(this).val("enter a brief description");
        }
    });
    $("#field-description").click(function() {
        if ( $(this).val() === "enter an indepth description") {
            $(this).val("");
        }
        $(this).addClass("active");
    });
    $("#field-description").blur(function() {
        if ( $(this).val() === "") {
            $(this).removeClass("active");
            $(this).val("enter an indepth description");
        }
    });

    /* Hook for handling user selection, and clicking add button to add people
     * on cc list. Needs to be a separately specified function, as we need to allow
     * people who cannot be autocompleted as well.
     */
    var addUserClick = function() {
        var cc_field = $("#add_cc_list_member");
        var cc_data = cc_field.val();
        var users = null;

        if (cc_data === null || cc_data.trim() === "") {
            return false;
        }

        users = cc_data.split(/[\s,;]+/);

        if (users === cc_data) {
            users = [cc_data];
        }

        $(users).each(function(index, username) {
            var user_item = null;
            var remove_button = null;
            var found = false;

            /* Block straight up duplicates */
            $("li.user .username").each(function(index, element) {
                if ($(element).text() === username) {
                    found = true;
                    return false;
                }
            });

            if (found === true) {
                return true;
            }

            user_item = jQuery("<li/>", {
                "class": "user",
            }).hide();

            remove_button = jQuery("<input/>", {
                "type": "button",
                "class": "remove_user_btn",
                "value": $("<div/>").html("&ndash;").text(),
            }).appendTo(user_item);

            remove_button.click(function() {
                removeUserClick(remove_button);
            });

            jQuery("<div/>", {
                "class": "username",
                "text": username,
            }).appendTo(user_item);

            /* Fade into the list */
            user_item.appendTo("#users_list");
            user_item.fadeIn("fast", function() {
                /* IE fix */
                $(this).show();
            });
        });

        /* Then rebuild the hidden input */
        cc_field.val("");
        rebuildCcInput();

        return true;
    }

    /* Hook for removing cc items from list */
    var removeUserClick = function(button) {
        var li = button.closest("li.user");
        li.fadeOut("fast", function() {
            $(this).remove();
            rebuildCcInput();
        });
    }

    /* Re-builds the internal input for Trac, based on the values in the current
     * CC list.
     */
    var rebuildCcInput = function() {
        var names = "";
        $("li.user .username").each(function(index, element) {
            if (index != 0) {
                names += ", ";
            }
            names += $(element).text();
        });
        $("#field-cc").val(names);
    }
});
