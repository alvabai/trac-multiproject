var selected_sub_page = 1;
var filter_empty_txt = "Search in selected project pages";
var searching = false;

function init_pagination() {
    /* Pagination "link" action */
    $('.subpage_link').click(function(e) {
        selected_sub_page = $(this).attr('id').split("_")[1];
        update_url();
    });
}

function search_fail() {
    search_done("<p>Server error! Check your search parameters, or try again later.</p>")
}

/* Callback method for search event */
function search_done(data) {
    // Inject returned project list data in place
    $('#searchResults').html(data);

    // Change page back to active
    $('body').css('cursor','auto');
    $('.catSelectNav').removeClass('searching');
    $('#searchForProjects').removeAttr("disabled");
    if($('#searchForProjects').val() != filter_empty_txt && $('#searchForProjects').val() != '') {
        $('#searchForProjects').addClass('active');
        $('#searchForProjects').trigger('focus');
    }

    // We are not searching anymore
    searching = false;

    /* Initializes event handlers for pagination items */
    init_pagination();
}

function build_search_args() {
    // Read selected categories
    var search_categories = $('.catlist li.selected').map(function() {
        return this.id.split("_")[1];
    }).get();

    // Read filter
    var filter = $('#searchForProjects').val();
    if (filter == filter_empty_txt) {
        filter = '';
    }

    /* Create array with all the arguments needed in search */
    var search_args = {
        'q': filter,
        'page': selected_sub_page
    }

    for (index in search_categories) {
        search_args[search_categories[index]] = 'on';
    }

    return search_args;
}

/* Funtion to be ran everytime search criteria changes in page */
function do_search(arguments) {
    /* Do not start searching if already in progress */
    if(searching)
        return;
    searching = true;

    // Change page to inactive state
    $('.catSelectNav').addClass('searching');
    $('body').css('cursor','progress');
    $('#searchResults').html('<h3>Searching..</h3>');
    $('#searchForProjects').trigger('blur');
    $('#searchForProjects').attr('disabled', true);
    $('#searchForProjects').removeClass('active');

    /* Do ajax request with arguments */
    $.ajax({ url: "", cache:false, data:arguments, success: search_done, error: search_fail});
}

/* When search params has changed, update hash */
function update_url() {
    var args = build_search_args();
    /* Do search only when there is actually something to be searched */
    if (args['q'] != filter_empty_txt && args['q'] != '') {
        document.location.hash = $.param.fragment('', args);
    }
}

/* Do search when hash changed */
$(window).bind( 'hashchange', function( event ) {
    var search_params = $.deparam.fragment();
    search_params['action'] = 'results';
    search_params['noquickjump'] = '1';
    do_search(search_params);
});

function select_category(item, with_subs) {
    var id = item.attr('id');

    //"All categories" not selected when something else is
    $('#select_all').removeClass('selected');

    //Deselect every item when all categories selected
    if(item.attr('id') == 'select_all') {
        $('.catlist li').removeClass('selected');
        $('.catlist li').map(function() {
            unselect_category($(this), with_subs);
        });
    }

    //Select this item
    item.addClass('selected');
}

function unselect_category(item, with_subs) {
    var id = item.attr('id');

    // Remove selection
    item.removeClass('selected');

    // If no selections exists select "All categories"
    if(!$('.catlist li:not(.context)').hasClass('selected')) {
        $('#select_all').addClass('selected');
    }
}

/* Reads state from fragment */
function read_fragment() {
    var search_params = $.deparam.fragment();

    // Defaults
    $('.catlist li').removeClass('selected');
    $('#select_all').addClass('selected');

    for (name in search_params) {
        if (name == 'q') {
            var value = search_params[name];
            if (value != '') {
                $('#searchForProjects').val(value);
                $('#searchForProjects').addClass("active");
            }
        }
        else if (name == 'all' || name == 'action' || name == 'page' || 'noquickjump') {
            // nothing to do
        }
        else {
            // Select selected categories
            select_category($('#cat_' + name), false);
        }
    }
}

$(document).ready(function () {

    /* Search input focus/blur action*/

    $("#searchForProjects").get(0).focus();
    if ($("#searchForProjects").val() != filter_empty_txt) {
        $("#searchForProjects").addClass("active");
    }

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

    /* Categorylist hover effect */
    $(".catlist li").hover(
            /* Handler in */
            function() {
                $(this).addClass('hover');
            },
            /* Handler out */
            function() {
                $(this).removeClass('hover');
            });

    /* Category select / unselect effect */
    $(".catlist li").click(
        function() {
            if(!searching) {
                if($(this).hasClass('selected')) {
                    unselect_category($(this), true);
                } else {
                    select_category($(this), true);
                }
                selected_sub_page = 1;
                update_url();
            }
        });

    /* Search projects button click */
    $('#searchProjectsBtn').click(
            function() {
                if(!searching) {
                    selected_sub_page = 1;
                    update_url();
                }
                return false;
            });


    $('#fullsearch').submit(
            function() {
                if(!searching) {
                    selected_sub_page = 1;
                    update_url();
                }
                return false;
            }
    );

    // If a hash link given do search ow. use defaults
    if(document.location.hash.length > 1) {
        read_fragment();
        $(window).trigger( 'hashchange' );
    } else {
        update_url();
    }
});