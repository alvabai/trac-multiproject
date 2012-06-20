/*
 * Hides dom object that is given as parameter
 */
function hide(obj) {
    obj.style.display = 'none';
}

/*
 * Shows dom object that is given as parameter
 */
function show(obj) {
    obj.style.display = 'block';
}

function showInline(obj) {
    obj.style.display = 'inline';
}

/*
 * Toggles dom object visibility. objname is id of object.
 */
function toggle(objname) {
    // Find object
    var obj = document.getElementById(objname);
    // Show if hidden, hide if visible
    if( obj != null ) {
        if(obj.style.display == 'none') {
            show(obj);
        }
        else {
            hide(obj);
        }
    }
}

function toggleInline(objname) {
    // Find object
    var obj = document.getElementById(objname);
    // Show if hidden, hide if visible
    if( obj != null ) {
        if(obj.style.display == 'none') {
            showInline(obj);
        }
        else {
            hide(obj);
        }
    }
}

/*
 * Binds given category into current project
 */
function bindCategory(env, contextId, categoryId) {
    // Id of the object that will be injected with response data
    var inject = "#context_" + contextId;
    // Make a get request and inject data to correct context
    $.post(multiproject.req.base_path + "/categories", {'action':'bind',
                                'context_key':contextId,
                                'category_key':categoryId,
                                '__FORM_TOKEN':$('input[name=__FORM_TOKEN]:first').val()
                                },
                                function(data){
                                    $(inject).html(data);
                                    contextUpdated(contextId);
                                });
}

/*
 * Removes binding of given category into current project
 */
function unBindCategory(env, contextId, categoryId) {
    // Id of the object that will be injected with response data
    var inject = "#context_" + contextId;

    // Make a get request and inject data to correct context
    $.post(multiproject.req.base_path + "/categories", {'action':'unbind',
                                'context_key':contextId,
                                'category_key':categoryId,
                                '__FORM_TOKEN':$('input[name=__FORM_TOKEN]:first').val()
                                },
                                function(data){
                                    $(inject).html(data);
                                    contextUpdated(contextId);
                                });
}

function contextUpdated(contextId) {
    id = '#update_notification_' + contextId
    $(id).fadeIn('slow',
            function() {
                $(this).delay(500);
                $(this).fadeOut(2500);
            }
    )
}