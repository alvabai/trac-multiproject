(function(window) {

var document = window.document;
var $ = window.jQuery;

var selected_tab = 'active';
var selected_sub_page = 1;
var results_per_page;
var filter_empty_txt = "Search Projects";
var searching = false;

var next_search;
var current_search;
var init_done = false;
var self_triggered_change = false;

function init_pagination() {
    /* Pagination "link" action */
    $('.subpage_link').not('.disabled').click(function() {
        if ($(this).hasClass('selected')) {
            return false;
        }
        var this_jquery = $(this);
        // If the #upper pagination is not shown, scroll to top
        // Both html and body are needed
        var resulting_scroll = $('html').scrollTop() + $('body').scrollTop();
        if ($('#upper_pagination').offset().top < resulting_scroll) {
            $('html, body').animate({scrollTop: '0px'}, 300);
        }
        selected_sub_page = this_jquery.attr('id').split("_")[1];
        update_url();
        return false;
    });
}


function search_fail(params) {
    var error_range = "<p id='result_range_ajax'>Server error when searching</p>";
    if (params.status && params.status == 403) {
        search_done(error_range + "<h3>403 Forbidden!</h3><p>Are you logged in?</p>");
    }
    else {
        search_done(error_range + "<p>Server Error! Please try again later.</p>");
    }
}

/* Callback method for search event */
function search_done(data) {
    // Inject returned project list data in place
    $('.project_list').html(data);

    // Change page back to active
    $('body').css('cursor','auto');
    $('.catSelectNav').removeClass('searching');
    if($('#searchForProjects').val() != filter_empty_txt && $('#searchForProjects').val() != '') {
        $('#searchForProjects').addClass('active');
        $('#searchForProjects').trigger('focus');
    }
    $('#keyword_attribs').removeClass('searching');
    $('#result_range').text($('#result_range_ajax').text());

    /* Initializes event handlers for pagination items */
    init_pagination();

    // We are not searching anymore
    searching = false;
    current_search = null;
    if (next_search) {
        do_search(next_search);
    }
}

function build_search_args() {
    // Read selected categories
    var category_ids = $('.catlist li.category_item.selected').map(function() {
        return this.id.split("_").slice(1).join('_');
    }).get();
    var resulting_ids = [];

    for (var i = 0; i<category_ids.length; i++) {
        var category_id = category_ids[i];
        if (category_id.indexOf('_top') == -1) {
            var top_version = category_id+'_top';
            for (var j = 0; j<category_ids.length; j++) {
                if (top_version == category_ids[j]) {
                    top_version = true;
                    break;
                }
            }
            if (top_version === true) {
                // Do nothing, since it will be added below.
            }
            else {
                resulting_ids.push(category_id);
            }
        }
        else {
            resulting_ids.push(category_id);
        }
    }

    // Read text filter
    var filter = $('#searchForProjects').val();
    if(filter == filter_empty_txt) {
        filter = '';
    }

    /* Create array with all the arguments needed in search */
    return {'action':'results', 'c':resulting_ids, 'f':filter,
            'tab':selected_tab, 'page':selected_sub_page,
            'numresults': results_per_page};
}

/* Funtion to be ran everytime search criteria changes in page */
function do_search(arguments) {
    /* Do not start searching if already in progress */
    if(searching) {
        var update_next_search = false;
        // If other arguments than current search, store them
        if (current_search['f'] != arguments['f']
            || current_search['tab'] != arguments['tab']
            || current_search['page'] != arguments['page']
            || current_search['numresults'] != arguments['numresults'])
        {
            update_next_search = true;
        }
        else {
            var c_current = [];
            var c_args = [];
            if (current_search && current_search['c']) {
                c_current = current_search['c'].sort();
            }
            if (arguments['c']) {
                c_args = arguments['c'];
            }
            if (c_args.length != c_current.length) {
                update_next_search = true;
            }
            else {
                for (var i = 0; i < c_current.length; i++) {
                    if (c_current[i] != c_args[i]) {
                        update_next_search = true;
                        break;
                    }
                }
            }
        }
        if (update_next_search) {
            next_search = arguments;
        }
        return;
    }
    searching = true;

    next_search = null;
    current_search = arguments;

    // Update keywords, as well as the clear all criteria button visibility
    update_search_box(arguments);

    // Change page to inactive state
    $('.catSelectNav').addClass('searching');
    $('#keyword_attribs').addClass('searching');
    $('body').css('cursor','progress');
    $('.project_list').html('<h3>Searching..</h3>');
    $('#searchForProjects').trigger('blur');
    $('#searchForProjects').removeClass('active');

    /* Do ajax request with arguments */
    $.ajax({ url: "", cache:false, data:arguments, success: search_done, error: search_fail});
}

/* When search params has changed, update hash */
function update_url() {
    self_triggered_change = true;
    var args = build_search_args();
    document.location.hash = $.param.fragment('', args);
    setTimeout(function () {
        self_triggered_change = false;
    }, 100);
}

/* Do search when hash changed */
$(window).bind('hashchange', function() {
    var search_params = $.deparam.fragment();
    search_params['action'] = 'results';
    if (!self_triggered_change) {
        // Read content from URL to DOM
        read_fragment();
        self_triggered_change = false;
    }
    // Otherwise, no need to update DOM
    do_search(search_params);
});

function select_category(cat_id, top_cat) {
    var elements = get_elements_for_category_selection(cat_id, top_cat);
    var this_list = elements[0];
    var cat_list_item = elements[1];
    // Get the item which will be opened
    // and make sure that all its parent categories are opened.

    // expand all parent category lists as well as this_list
    //console.log('this_list', this_list, el_id);
    this_list
        .parentsUntil('.rootcatlist')
        .parent('.category_item')
        .add(this_list)
        .each(function () {
            //console.log("opening... ", this);
            open_list_item($(this))
        });

    // Select checkboxes: both for the category in both non-top and top category
    cat_list_item
        .addClass('selected')
        .children('.category_checkbox').find('input[type="checkbox"]')
        .attr('checked', 'checked');

    // Set style to "selected" for both top and non-top category list
    //cat_list_item;

    // Unselect the child categories and all parent categories (both checkbox and style)
    // Luckily, this doesn't match ever to the contexts
    cat_list_item
        .parentsUntil('.rootcatlist')
        .parent('.category_item')
        .filter('.selected')
        .removeClass('selected').each(function() {
            var this_parent_item = $(this);
            get_children_list(this_parent_item).removeClass('children_in_search');
            // Also, remove these categories from the filters
            remove_category_from_search_box(this.id.split('_')[1]);
        })
        .children('.category_checkbox').find('input[type="checkbox"]')
        .removeAttr("checked");

    cat_list_item
        .parentsUntil('.rootcatlist')
        .parent('.category_item')
        .addClass('sub_cat_selected');

    var cat_list_children = get_children_list(cat_list_item);

    // Remove checked status from
    cat_list_children
        .find('.category_item.selected')
        .removeClass('selected')
        .each(function() {
            var this_child_item = $(this);
            get_children_list(this_child_item).removeClass('children_in_search');
            //   Also, remove these categories from the filters
            remove_category_from_search_box(this.id.split('_')[1]);
        })
        .children('.category_checkbox').find('input[type="checkbox"]')
        .removeAttr("checked");

    //console.log(get_children_list(cat_list_item).find('.category_item.sub_cat_selected').add(cat_list_item));
    cat_list_children
        .find('.category_item.sub_cat_selected')
        .add(cat_list_item)
        .removeClass('sub_cat_selected');

    //console.log('adding children_in_search to', cat_list_item);

    // Set the style to "child_selected" to all parents in both top and non-top category lists.
    cat_list_children.addClass('children_in_search');

    // Add category into filters
    put_category_into_search_box(cat_id);
}

function get_elements_for_category_selection(cat_id, top_cat) {
    var el_id = 'cat_' + cat_id;
    if (top_cat) {
        el_id += '_top';
    }
    var this_list = $('#' + el_id);
    // Backup, if this fails... Happens, for example, when search box is used.
    if (this_list.length == 0) {
        el_id = 'cat_' + cat_id;
        if (!top_cat) {
            el_id += '_top';
        }
        this_list = $('#' + el_id);
    }
    var cat_list_item = $('#cat_' + cat_id).add('#cat_' + cat_id + '_top');
    return [this_list, cat_list_item];
}

/* Called when searching. Updates keywords into search box and UI states (not category boxes). */
function update_search_box(arguments) {
    var keywords = '';
    if (arguments['f']) {
        keywords = arguments['f'].replace(/(^ +| +$)/g,'');
    }
    $('#keywords_span').text(keywords);
    if ('' != keywords) {
        $('#keyword_attribs').addClass('with_keywords');
    }
    else {
        $('#keyword_attribs').removeClass('with_keywords');
    }
    if ((arguments['c'] && (arguments['c'].length > 0))
        || '' != keywords) {
        $('#project_search_attribs .search_clear_all').show();
    }
    else {
        $('#project_search_attribs .search_clear_all').hide();
    }
}

function put_category_into_search_box(cat_id) {
    //console.log('put_category_into_search_box', cat_id);
    var cat_name = $('#cat_' + cat_id + '_top').add('#cat_' + cat_id).find('label:first').text();
    if ($('#sbcat_'+cat_id).length > 0) {
        // already there!
        return;
    }
    var cat_list = $('#category_attribs ul.word_box_list');
    cat_list.append('<li id="sbcat_'+cat_id+'" class="sb_category"><span>'+cat_name+'</span> <input type="button" value=" " class="delete_button delete_categories" /></li>');
    // delete_button delete_categories
    cat_list.find('#sbcat_'+cat_id+' .delete_categories').click(function () {
        var cat_id = $(this).parents('li').attr('id').split('_')[1];
        unselect_category(cat_id, true);
        selected_sub_page = 1;
        update_url();
    });
    $('#category_attribs').addClass('with_categories');
}

function remove_category_from_search_box(cat_id) {
    //console.log('remove_category_from_search_box','#sbcat_'+cat_id, $('#sbcat_'+cat_id));
    $('#sbcat_'+cat_id).remove();
    if ($('#category_attribs li.sb_category').length == 0) {
        $('#category_attribs').removeClass('with_categories');
    }
}

function unselect_category(cat_id, top_cat) {
    // Get the item which will be opened
    // and make sure that all its parent categories are opened.
    var elements = get_elements_for_category_selection(cat_id, top_cat);
    var this_list = elements[0];
    var cat_list_item = elements[1];
    // Close this category
    var children_list = get_children_list(this_list);
    if (children_list.children('.category_item.selected').length == 0
        && children_list.children('.category_item.sub_cat_selected').length == 0) {
        close_list_item(this_list);
    }
    // But no recursion

    // For the category in both non-top and top category
    cat_list_item
        .children('.category_checkbox')
        .find('input[type="checkbox"]')
        .removeAttr('checked');

    // Set style to "selected" for both top and non-top category list
    cat_list_item.removeClass('selected');

    // Remove the sub_cat_selected class from parent categories,
    // if the corresponding category don't have children which are selected.
    var sub_category_list = cat_list_item.parent('ul.subcatlist');
    //console.log('starting recursion into root', sub_category_list);
    while (sub_category_list.length > 0) {
        if (sub_category_list.children('.category_item.selected').length > 0
            && sub_category_list.children('.category_item.sub_cat_selected')) {
            //console.log('break, since has selected sub category: ');
            break;
        }
        //console.log('removing sub_cat_selected',sub_category_list.prev('.category_item.sub_cat_selected'))
        sub_category_list.parent('.category_item.sub_cat_selected').removeClass('sub_cat_selected');
        sub_category_list = sub_category_list.parent('ul.subcatlist');
    }
    //console.log('removing children_in_search of', get_children_list(cat_list_item))
    get_children_list(cat_list_item).removeClass('children_in_search');
    // Set the style to "child_selected" to all parents in both top and non-top category lists.

    // Remove category from filters
    remove_category_from_search_box(cat_id);
}

function get_children_list(list_item) {
    return list_item.children('.subcatlist');
}

function open_list_item(list_item) {
    if (!list_item.hasClass('opened')) {
        if (init_done) {
            get_children_list(list_item).slideDown('fast');
        }
        else {
            // On initiation, no animation
            get_children_list(list_item).show();
        }
        list_item.addClass('opened');
    }
}

function close_list_item(list_item) {
    if (list_item.hasClass('opened')) {
        get_children_list(list_item).slideUp('fast');
        list_item.removeClass('opened');
    }
}

function show_all_categories() {
    $("#all_categories_show").hide();
    $("#all_categories_hide").show();
    $('#all_categories_toggle').addClass('open');
    $('#all_categories').slideDown('slow');
}
function hide_all_categories() {
    $("#all_categories_show").show();
    $("#all_categories_hide").hide();
    $('#all_categories_toggle').removeClass('open');
    $('#all_categories').slideUp('slow');
}

/* Add click handlers into elements. */
function init_view() {
    /* Search input focus/blur action*/
    $("#searchForProjects").click(function() {
        if ( $("#searchForProjects").val() == filter_empty_txt) {
            $("#searchForProjects").val("");
            $("#searchForProjects").addClass("active");
        }
    });
    $("#searchForProjects").blur(function() {
        if ( $("#searchForProjects").val() == "") {
            $("#searchForProjects").removeClass("active");
            $("#searchForProjects").val(filter_empty_txt);
        }
    });

    $("#resperpage").change(function() {
        var wanted_index = (selected_sub_page - 1) * results_per_page;
        results_per_page = $(this).val();
        selected_sub_page = Math.floor(wanted_index / $(this).val()) + 1;
        update_url();
    });

    // Bind click event on category checkboxes
    var catCheckboxes = $('.catlist span.category_checkbox > input[type="checkbox"]');
    catCheckboxes.unbind('click');
    catCheckboxes.click(function(event) {
        event.stopPropagation();

        var parts = this.id.split('_');
        var cat_id = parts[1].replace('top', '');
        var is_top = parts.length > 1 && parts[2] == 'top';

        if(!$(this).is(':checked')) {
            unselect_category(cat_id, is_top);
        } else {
            select_category(cat_id, is_top);
        }

        selected_sub_page = 1;
        update_url();
    });

    $(".toggle_button").click(function(event) {
        var list_item = $(this).parents('.category_item');
        if (list_item.hasClass('opened')) {
            close_list_item(list_item);
        }
        else {
            open_list_item(list_item);
        }
        return false;
    });

    $(".context_item_top").click(function(event) {
        event.preventDefault();
        event.stopPropagation();

        var list_item = $(this);
        if (list_item.hasClass('opened')) {
            close_list_item(list_item);
        }
        else {
            open_list_item(list_item);
        }
        return false;
    });

    /* All categories show/hide toggle */
    $("#all_categories_toggle, #toggle_img").click(function(event) {
        if(!$(this).hasClass("open")) {
            show_all_categories();
        } else {
            hide_all_categories();
        }
    });

    /* Search projects button click */
    $("#searchProjectsBtn").click(function(event) {
        selected_sub_page = 1;
        update_url();
        return false;
    });

    /* Tab click action (change tab) */
    $('#tabbedNavigation li').click(function(event) {
        /* Change tab to selected tab and reset pagination, finally search */
        selected_tab = $(this).attr('id').split("_")[1];
        // Select correct tab
        $('#tabbedNavigation li.selected').removeClass('selected');
        $(this).addClass('selected');
        selected_sub_page = 1;
        update_url();
        return false;
    });

    $('#project_search_form').submit(
        function() {
            selected_sub_page = 1;
            update_url();
            return false;
        }
    );

    $('#keyword_attribs .delete_keywords').click(function () {
        $('#keyword_attribs').removeClass('with_keywords');
        $('#searchForProjects').val(filter_empty_txt);
        selected_sub_page = 1;
        update_url();
    });

    $('#project_search_attribs .search_clear_all input[type="button"]').click(function () {
        clear_all_search_box_filters();
        update_url();
    });
}

function clear_all_search_box_filters() {
    // Doesn't touch to results per page and tab
    // Clears category, filter string and selected sub page
    $('#keyword_attribs').removeClass('with_keywords');
    $('#searchForProjects').val(filter_empty_txt);
    var category_ids = $('.catlist li.category_item.selected').map(function() {
        return this.id.split("_").slice(1).join('_');
    }).get();
    for(var i=0 ;i<category_ids.length; i++) {
        var cat_id = category_ids[i];
        var is_top = false;
        if (cat_id.indexOf('_top') != -1) {
            is_top = true;
            cat_id = cat_id.replace('_top','');
        }
        unselect_category(cat_id, is_top);
    }

    $('#category_attribs').removeClass('with_categories');

    selected_sub_page = 1;
}

/* Reads state from fragment to DOM */
/* Happens on document load or when manually changing fragment */
function read_fragment() {
    var search_params = $.deparam.fragment();
    clear_all_search_box_filters();

    for(var name in search_params) {
        if(name == 'c') {
            var all_categories_shown = false;

            // Skip if c value is empty
            var categories = search_params[name];
            if (categories.length === 0) {
                continue;
            }

            // Select selected categories
            $.each(categories, function(index, cat_id){
                var is_top = false;
                if (cat_id.indexOf('_top') != -1) {
                    is_top = true;
                    cat_id = cat_id.replace('_top','');
                }
                else if (!all_categories_shown) {
                    show_all_categories();
                    all_categories_shown = true;
                }
                if(cat_id == 'all') {
                    return false;
                } else {
                    select_category(cat_id, is_top);
                }
            });

        }
        if(name == 'tab') {
            selected_tab = search_params[name];
            var this_el = $('#tab_' + selected_tab);
            // Select correct tab
            $('#tabbedNavigation li.selected').removeClass('selected');
            this_el.addClass('selected');
        }
        if(name == 'f') {
            var value = search_params[name];
            if(value != '') {
                $('#searchForProjects').val(value);
                $('#searchForProjects').addClass("active");
            }
        }
        if (name == 'numresults') {
            $('#resperpage').val(search_params[name]);
        }
        if (name == 'page') {
            selected_sub_page = search_params[name];
        }
    }
}

$(document).ready(function () {
    init_view();
    results_per_page = $('#resperpage').val();
    // If a hash link given do search ow. use defaults
    if(document.location.hash.length > 1) {
        // Even if the url doesn't change, trigger hash change (fixes refresh)
        $(window).trigger('hashchange');
    } else {
        update_url();
    }
    init_done = true;
});
})(window);
