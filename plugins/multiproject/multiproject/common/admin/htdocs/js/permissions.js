$(document).ready(function() {

    $('form.add_member input[name="member"]').each(function(index) {
        var userfield = new multiproject.ui.UserField($(this), {
            minLength: 2,
            limit: 5,
            status: ['inactive', 'active']
        });
        userfield.render();
    });

    $('input.remove_member').click(function(event) {
        var cbox = multiproject.ui.ConfirmationBox("Are you sure you want to remove the member?");
        var self = this;
        cbox.open(event, function() {
            removeMember($(self));
        });
    });

    $('input.remove_permission').click(function(event) {
        var self = this;
        var li = $(self).closest('li');
        var perm_group = li.find('input[name="group"]').val();
        var permission = li.find('input[name="permission"]').val();
        if (perm_group === "Public viewers" && permission === "PROJECT_VIEW") {
          var nbox = multiproject.ui.NotifyBox("You are not allowed to remove "+"'"+permission+"'"+" permission for "+perm_group);
          nbox.open();
        }else{
          var cbox = multiproject.ui.ConfirmationBox("Are you sure you want to remove the permission?");
          cbox.open(event, function() {
            removePermission($(self));
          });
       }
    });

    $('input.remove_group').click(function(event) {
        var cbox = multiproject.ui.ConfirmationBox("Are you sure you want to remove the group?");
        return cbox.open(event) === true;
    });

    $('form.remove_member').submit(function(e) {
        e.preventDefault();
    });

    $('form.remove_permission').submit(function(e) {
        e.preventDefault();
    });

    /* new group dialog */

    $('#new_group_button').click(function() {
        $("#new_group").dialog({modal: true, draggable: false, width: 750, resizable: false});
    });

    $('form.create_group').submit(function(e) {
        e.preventDefault();
    });

    $("#new_group input[type='checkbox']").click(function() {
        var selected = $("#new_group input[type='checkbox']:checked");
        var create = $("#create_button");
        if (selected.length > 0) {
            create.removeAttr("disabled");
        } else {
            create.attr("disabled", "disabled");
        }
    });

    /* select type of add */

    $(".add_type").change(function() {
        var form = $(this).closest('form');
        var selected = form.find(".add_type option:selected").text();

        var selections = {
            'User': form.find(".add_type_user"),
            'Organization': form.find(".add_type_organization"),
            'LDAP group': form.find(".add_type_ldap"),
            'Login status': form.find(".add_type_login_status")
        };

        // hide all and show selected
        for (var key in selections) {
            selections[key].hide();
        }
        selections[selected].show();
    });

    $(".all_permissions").click(function(event) {
        $(this).siblings().children(".implicit").show();
        $(this).hide();
    });

});

function removeMember(element) {

    var li = $(element).closest('li');
    var member = li.find('input[name="member"]').val();
    var group = li.find('input[name="group"]').val();
    var type = li.find('input[name="type"]').val();
    var token = li.find('input[name="__FORM_TOKEN"]').val();
    var content = { member: member, group: group, __FORM_TOKEN: token,
        action: 'remove_member', type: type };

    $(element).removeClass('remove_member');
    $(element).addClass('loading');

    $.ajax({
        url: document.URL,
        data: content,
        type: 'POST',
        success: function(response) {
            if (typeof response != 'object') {
                alert('ERROR: Invalid server response, expected JSON');
                return;
            }
            li.fadeOut('fast', function() { li.remove() } );
            $(element).removeClass('loading');
            $(element).addClass('remove_member');
        },
        error: function(jqXHR, textStatus, errorThrown) {
            $(element).removeClass('loading');
            $(element).addClass('remove_member');
            if (textStatus == 'error' && errorThrown == 'Forbidden') {
                alert(jqXHR.responseText);
            } else {
                alert('Unexpected server or communication error. Try again later.');
            }
        }
    });
}

function removePermission(element) {

    var li = $(element).closest('li');
    var ul = $(li).closest('ul');
    var permission = li.find('input[name="permission"]').val();
    var group = li.find('input[name="group"]').val();
    var token = li.find('input[name="__FORM_TOKEN"]').val();
    var content = { permission: permission, group: group, __FORM_TOKEN: token,
        action: 'remove_permission'};

    $(element).removeClass('remove_permission');
    $(element).addClass('loading');

    $.ajax({
        url: document.URL,
        data: content,
        type: 'POST',
        success: function(response) {
            if (typeof response != 'object') {
                alert('ERROR: Invalid server response, expected JSON');
                return;
            }

            if (response['removed'].length == 0) {
                // no permission was really removed, it's still given implicitly
                $(element).removeClass('loading');
                $(element).addClass('remove_permission');
                alert('NOTE: The removed permission is still given implictly through another higher permission.');
                window.location.href=window.location.href;
            }
            for (var i = 0; i < response['removed'].length; i++) {
                var removed = response['removed'][i];
                ul.find("li:contains('" + removed + "')").fadeOut('fast', function() { $(this).remove() } );
            }
            // update implicit count
            var a = ul.parent().find('a');
            if (response['remaining'] == 0) {
                a.fadeOut('fast');
            } else {
                a.text(a.text().replace(/[\d\.]+/g, response['remaining']));
            }

        },
        error: function(jqXHR, textStatus, errorThrown) {
            $(element).removeClass('loading');
            $(element).addClass('remove_permission');
            if (textStatus == 'error' && errorThrown == 'Forbidden') {
                alert(jqXHR.responseText);
            } else {
                alert('Unexpected server or communication error. Try again later.');
            }
        }
    });

}
