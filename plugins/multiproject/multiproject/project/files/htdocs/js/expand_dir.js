// Enable expanding/folding folders in Multiproject Files

// This was copied from Trac and modified

(function($){
    var FOLDERID_COUNTER = 0;
    var SUBFOLDER_INDENT = 20;

    // enableExpandMoveDir adds the capability to ''folder'' rows in a table
    // to be expanded and folded.
    //
    // It also teach the rows about their ancestors. It expects:
    //  - `parent_tr`, the logical parent row (`null` if there's no ancestor)
    //  - a `rows` jQuery object matching the newly created entry rows
    //  - `qargs`, additional parameters to send to the server when expanding
    //  - `autoexpand`, an optional array corresponding to a splitted sub-path
    //    of entries that will be expanded automatically.
    // - `a_callback`, callback which takes a element and attaches proper click handler to it

    window.enableExpandMoveDir = function(parent_tr, rows, qargs, on_click, autoexpand) {
        // the ancestors folder ids are present in the parent_tr class attribute
        var ancestor_folderids = [];

        if (parent_tr) // rows are logical children of the parent_tr row
            ancestor_folderids = $.grep(parent_tr.attr("class").split(" "),
                function(c) { return c.match(/^f\d+$/)});

        var autoexpand_expander = null;
        rows.not('.expand_enabled').addClass('expand_enabled').each(function () {
            var a = $(this).find("a.dir");

            a.click(function() {
                var that = $(this);
                var tr = that.parents("tr:first");
                toggleMoveDir(that.prev(), qargs, on_click);
                if (on_click) {
                    return on_click(that);
                }
                else {
                    return false;
                }
            });
            if (a.length) { // then the entry is a folder
                // create new folder id
                var folderid = "f" + FOLDERID_COUNTER++;
                this.id = folderid;
                $(this).addClass(folderid);

                // add the expander icon
                var expander = $('<span class="expander">&nbsp;</span>')
                    .attr("title", _("Expand sub-directory in place"))
                    .click(function() { toggleMoveDir($(this), qargs, on_click); });
                a.wrap('<div></div>').before(expander);
                if (autoexpand && a.text() == autoexpand[0]) {
                    autoexpand_expander = expander;
                    on_click(a);
                }
            }

            // tie that row to ancestor folders
            if (parent_tr)
                $(this).addClass(ancestor_folderids.join(" "));
        });

        if ( autoexpand_expander )
            toggleMoveDir(autoexpand_expander, qargs, on_click, autoexpand.slice(1));
    };

    // handler for click event on the expander icons
    window.toggleMoveDir = function(expander, qargs, on_click, autoexpand) {
        var tr = expander.parents("tr:first");
        var folderid = tr.get(0).id;

        if ( tr.hasClass("expanded") ) { // then *fold*
            tr.removeClass("expanded");
            if (tr.next().hasClass("error")) {
                tr.next().remove();
            } else {
                tr.addClass("collapsed");
                tr.siblings("tr."+folderid).hide();
            }
            expander.attr("title", _("Re-expand directory"));
            return;
        }

        var a = expander.next("a");

        if ( tr.hasClass("collapsed") ) { // then *expand*
            tr.removeClass("collapsed").addClass("expanded");
            tr.siblings("tr."+folderid).show();
            // Note that the above will show all the already fetched subtrees,
            // so we have to fold again the folders which were already collapsed.
            tr.siblings("tr.collapsed").each(function() {
                tr.siblings("tr."+this.id).not(this).hide();
            });
        } else {                                // then *fetch*
            var td = expander.parents("td:first");
            var td_class = td.attr("class");
            var depth =
                parseFloat(td.css("padding-left").replace(/^(\d*\.\d*).*$/, "$1")) +
                    SUBFOLDER_INDENT;

            tr.addClass("expanded");
            // insert "Loading ..." row
            var loading_row = $($.htmlFormat(
                '<tr>' +
                    ' <td class="$td_class" colspan="$colspan" ' +
                    '     style="padding-left: ${depth}px">' +
                    '  <span class="loading">${loading}</span>' +
                    ' </td>' +
                    '</tr>', {
                    td_class: td_class,
                    colspan: tr.children("td").length,
                    depth: depth,
                    loading: babel.format(_("Loading %(entry)s..."), {entry: a.text()})
                }));
            tr.after(loading_row);

            // XHR for getting the rows corresponding to the folder entries
            $.ajax({
                type: "GET",
                url: a.attr("href"),
                data: qargs,
                dataType: "html",
                success: function(data) {
                    // Safari 3.1.1 has some trouble reconstructing HTML snippets
                    // bigger than 50k - splitting in rows before building DOM nodes
                    var rows = data.replace(/^<!DOCTYPE[^>]+>/, "").trim().split("</tr>");

                    if (rows.length && rows[0]) {
                        // insert entry rows
                        $(rows).each(function() {
                            row = $(this+"</tr>");
                            row.children("td."+td_class).css("padding-left", depth);
                            // make all entry rows collapsible but only subdir rows expandable
                            loading_row.before(row);
                            enableExpandMoveDir(tr, row, qargs, on_click, autoexpand);
                        });
                        // remove "Loading ..." row
                        loading_row.remove();
                    } else {
                        loading_row.find("span.loading")
                            .text("")
                            .append("<i>" + _("(empty)") + "</i>")
                            .removeClass("loading");
                        enableExpandMoveDir(tr, loading_row, qargs, on_click); // make it collapsible
                    }
                },
                error: function(req, err, exc) {
                    loading_row.find("span.loading")
                        .text("")
                        .append("<i>" + _("(error)") + "</i>")
                        .removeClass("loading");
                    loading_row.addClass("error");
                    enableExpandMoveDir(tr, loading_row, qargs, on_click); // make it collapsible
                }
            });
        }
        expander.attr("title", _("Fold directory"));
    }

})(jQuery);
