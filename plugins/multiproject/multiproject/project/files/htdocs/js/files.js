(function(window) {

var document = window.document;
var $ = window.jQuery;

var availableModes = ['show_mode', 'edit_mode', 'move_mode', 'delete_mode',
    'move_multiple_mode', 'delete_multiple_mode', 'no_mode'];
var availableTableModes = ['modify_mode', 'add_mode', 'upload_mode'];

function FilesEntry(head, table) {
    this.init(head, table);
}

function onClickFollowInitializer(elements) {
    elements.removeClass('on_click_follow').addClass('follow_when_clicked')
    .click(function () {
        // To be sure, that location is in the files section of the same project...
        var resulting_path = $(this).find('.filename a').attr('href');
        resulting_path = getFilesSectionUrl(resulting_path);
        if (resulting_path != '') {
            resulting_path = window.multiproject.req.base_path + '/files' + resulting_path;
            document.location.pathname = resulting_path;
        }
    }).find('.filename a').click(function (event) {
        event.stopPropagation();
    });
}

function modeButtonInitializer(filesEntry, mode) {
    filesEntry.buttonRow.find('.mode_button.'+mode).click(function (event) {
        filesEntry.setCurrentMode(mode);
        return false;
    });
}

FilesEntry.prototype = {
    init: function(head, filesTable) {
        var filesEntry = this;
        this.head = $(head);
        this.body = this.head.next().find('.files_entry_body');
        this.buttonRow = this.body.find('.node_button_row');
        this.filesTable = filesTable;
        this.head.removeClass('needs_init');
        this.currentModeArea = this.body.find('.current_mode_area').first();
        this.currentModeButton = this.body.find('.current_mode_button').first();
        this.head.hover(function() {filesEntry.body.addClass('hovered')});
        this.head.hover(
            function() {filesEntry.body.addClass('hovered')},
            function() {filesEntry.body.removeClass('hovered')}
        );
        for (var i=0;i<availableModes.length; i++) {
            var mode = availableModes[i];
            /*  mode is 'move_mode', 'edit_mode', 'delete_mode', 'show_mode'
                but not 'download_mode' */
            modeButtonInitializer(filesEntry, mode);
        }
        this.body.find('.mode_cancel').click(function (event) {
            filesEntry.setCurrentMode();
            if ($(this).closest('form') && $(this).closest('form').get(0)) {
                $(this).closest('form').get(0).reset();
            }
            return false;
        });
        this.checkbox = this.head.find('.first_col .file_selector');
        this.checkbox.click(function (event) {
            var wasChecked = false;
            if($(this).checked()) {
                wasChecked = true;
            }
            filesEntry.setChecked(wasChecked);
            event.stopPropagation();
        });
        this.headClick = function(event) {
            if (filesEntry.body.hasClass('show_mode') || filesEntry.body.css('display') == 'block') {
                if (filesEntry.body.hasClass('show_mode')) {
                    filesEntry.body.css('display', 'block');
                    filesEntry.body.removeClass('show_mode');
                }
                filesEntry.body.slideUp('fast', function() {
                    filesEntry.head.removeClass('opened');
                });
            } else {
                filesEntry.head.addClass('opened');
                filesEntry.body.slideDown('fast');
            }
        };
        this.head.click(this.headClick);
        /* Exception: if link or label is clicked, don't toggle! */
        this.head.find('.file_link').add(this.head.find('label')).click(function (event) {
            event.stopPropagation();
        });
    },
    setChecked: function(wasChecked) {
        if (!this.checkbox.length) {
            return;
        }
        if (wasChecked) {
            if (this.head.hasClass('checked')) {
                return;
            }
            this.body.addClass('checked');
            this.head.addClass('checked');
            if (!this.checkbox.attr('checked')) {
                this.checkbox.attr('checked', 'checked');
            }
        }
        else {
            if (!this.head.hasClass('checked')) {
                return;
            }
            this.body.removeClass('checked');
            this.head.removeClass('checked');
            if (this.checkbox.attr('checked')) {
                this.checkbox.removeAttr('checked');
            }
        }
        this.filesTable.entryChecked(this, wasChecked);
    },
    setCurrentMode: function(new_mode) {
        // returns true, if was set (toggle on), otherwise false
        for (var i=0;i<availableModes.length;i++) {
            if (this.body.hasClass(availableModes[i])) {
                if (new_mode && new_mode == availableModes[i]) {
                    // If the current_mode_button was clicked, don't do anything.
                    return;
                }
                this.body.removeClass(availableModes[i]);
                this.head.removeClass(availableModes[i]);
            }
        }
        this.currentModeArea.removeClass('current_mode_area');
        this.currentModeButton.removeClass('current_mode_button');
        if (new_mode) {
            this.body.addClass(new_mode);
            this.currentModeButton = this.body.find('.mode_button.'+new_mode).addClass('current_mode_button');
            this.currentModeArea = this.body.find('.mode_area.'+new_mode).addClass('current_mode_area');
        }
        else {
            this.body.addClass('show_mode');
            this.currentModeButton = this.body.find('.mode_button.show_mode').addClass('current_mode_button');
            this.currentModeArea = this.body.find('.mode_area.show_mode').addClass('current_mode_area');
        }
        return true;
    },
    // Works only when user can edit files (there are checkboxes)
    getFilename: function() {
        return this.head.find('.first_col input[type="checkbox"]').val();
    }
};

function getFilesSectionUrl(path) {
    var parts = path.split('/');
    var files_path = window.multiproject.req.base_path+'/files/';
    var folders = [];
    if (path.indexOf(files_path) != 0 || parts[0] != '') {
        return '';
    }
    parts = parts.slice(files_path.split('/').length - 1);
    for (var i=0;i<parts.length; i++) {
        if (parts[i] == '..') {
            return '';
        }
        else if (parts[i] != '.') {
            folders.push(parts[i])
        }
    }
    if (0 == folders.length) {
        return '/'
    }
    return '/'+folders.join('/');
}

function TableFormHandler(filesTable, buttonRowSelector, rowSelector, mode, firstTimeCallback,
                          onOpenedCallback) {
    this.init(filesTable, buttonRowSelector, rowSelector, mode, firstTimeCallback,
        onOpenedCallback);
}

TableFormHandler.prototype = {
    init: function (filesTable, buttonRowSelector, rowSelector, mode, firstTimeCallback,
                    onOpenedCallback) {
        /**
         * filesTable - FilesTable object
         * buttonRowSelector str like '.get_modify_form'
         * rowSelector str like '.modify_form'
         * @type {FilesEntry}
         */
        var formHandler = this;
        this.filesTable = filesTable;
        this.filesEntry = new FilesEntry(filesTable.table.find('.files_entry_head'+rowSelector),
            filesTable);
        this.space = this.filesEntry.head.next().next().children('.td_between');
        this.mode = mode;
        this.openedOnce = false;
        this.onOpenedCallback = onOpenedCallback;
        this.firstTimeCallback = firstTimeCallback;
        this.filesEntry.head.unbind('click');
        this.filesEntry.head.click(function (event) {
            formHandler.toggle();
            return false;
        });

        filesTable.filesHeading.find(buttonRowSelector).click(function () {
            formHandler.toggle();
            return false;
        });
        this.filesEntry.body.find('.table_mode_cancel').click(function () {
            if ($(this).closest('form') && $(this).closest('form').get(0)) {
                $(this).closest('form').get(0).reset();
            }
            formHandler.toggle();
            return false;
        });
        if (filesTable.getCurrentMode() == mode) {
            filesTable.currentFormHandler = this;
        }
    },
    toggle: function (wasOldHandler) {
        this.filesTable.table.removeClass('no_mode');
        var oldFormHandler = null;
        if (this.filesTable.currentFormHandler) {
            if (!wasOldHandler && this.filesTable.currentFormHandler != this) {
                oldFormHandler = this.filesTable.currentFormHandler;
                oldFormHandler.filesEntry.head.before(this.filesEntry.head)
                    .before(this.filesEntry.body.parent())
                    .before(this.space.parent());
            }
        }
        var formHandler = this;
        var filesEntry = this.filesEntry;
        if (filesEntry.body.hasClass('show_mode') || filesEntry.head.css('display') != 'none') {
            // Hide this!
            if (filesEntry.body.hasClass('show_mode')) {
                filesEntry.body.removeClass('show_mode');
                filesEntry.body.css('display', 'block');
            }
            var afterBodyHide = function() {
                formHandler.space.hide();
                filesEntry.head.hide();
                if (!wasOldHandler) {
                    // there was no new handler to set the mode
                    formHandler.filesTable.setCurrentMode('no_mode');
                }
            };
            if (filesEntry.body.css('display') == 'none') {
                // If body is already hidden, hide instantly.
                afterBodyHide();
            }
            else {
                filesEntry.body.slideUp('fast', afterBodyHide);
            }
            if (!wasOldHandler) {
                this.filesTable.currentFormHandler = null;
            }
        } else {
            // Show this!
            var afterBodyShow = function() {
                if (oldFormHandler && !wasOldHandler) {
                    oldFormHandler.toggle(true);
                }
                formHandler.filesTable.setCurrentMode();
                if (!wasOldHandler) {
                    // there was no new handler to set the mode
                    formHandler.filesTable.setCurrentMode(formHandler.mode);
                }
            };
            if (!formHandler.openedOnce) {
                // For first time only
                this.onOpened();
                filesEntry.head.addClass('opened');
                filesEntry.body.slideDown('fast', afterBodyShow);
            }
            else if (filesEntry.head.hasClass('opened')) {
                filesEntry.head.show();
                filesEntry.body.slideDown('fast', afterBodyShow);
            }
            else {
                afterBodyShow();
            }
            formHandler.space.show();
            filesEntry.head.show();
            if (!wasOldHandler) {
                this.filesTable.currentFormHandler = this;
            }
        }
        return false;
    },
    onOpened: function() {
        if (this.firstTimeCallback) {
            this.firstTimeCallback(this);
            this.openedOnce = true;
        }
        if (this.onOpenedCallback) {
            this.onOpenedCallback(this);
        }
    }
};

function FilesTable(table) {
    this.init(table);
}

FilesTable.prototype = {
    init: function (table) {
        var filesTable = this;
        this.table = $(table);
        this.filesHeading = this.table.children('thead.files_heading').find('.dir_button_row');
        this.filesBody = this.table.children('tbody.files_entries');
        this.filesEntries = [];
        this.checkAllCheckbox = this.table.find('thead.files_heading > tr > th.first_col .file_selector');
        this.checkAllCheckbox.click(function () {
            var wasChecked = false;
            if($(this).checked()) {
                wasChecked = true;
            }
            for (var i=0;i<filesTable.filesEntries.length;i++) {
                filesTable.filesEntries[i].setChecked(wasChecked);
            }
        });
        this.table.find('.files_entry_head.needs_init').each(function () {
            var filesEntry = new FilesEntry(this, filesTable);
            filesTable.filesEntries.push(filesEntry);
        });
        this.maxCheckCount = filesTable.filesEntries.length;
        this.currentCheckCount = 0;
        if (this.maxCheckCount == 0) {
            this.checkAllCheckbox.attr('disabled', 'disabled');
        }
        onClickFollowInitializer(this.table.find('.files_entry_head.on_click_follow'));

        if (this.filesHeading && this.filesHeading.children().length > 0) {
            this.currentFormHandler = null;
            this.currentFolderModeButton = this.filesHeading.find('.current_mode_button');

            this.modifyForm = new TableFormHandler(filesTable,
                '.mode_button.modify_mode', '.modify_mode', 'modify_mode', function () {
                /* browsers using old WebKits have issues with expandDir... */
                var webkit_rev = /AppleWebKit\/(\d+)/.exec(navigator.userAgent);
                if ( !webkit_rev || (521 - webkit_rev[1]).toString()[0] == "-" )
                    var folders = decodeURI(getFilesSectionUrl(window.location.pathname)).split('/').slice(1);
                    var allTrs = filesTable.modifyForm.filesEntry.body.find("table.dirlist tr");
                    var expanding = allTrs.slice(1);
                    var first = allTrs.slice(0,1).find('a.dir');
                    var onClicked = function(a_element) {
                        a_element = $(a_element);
                        filesTable.modifyForm.currentTr.removeClass('selected');
                        filesTable.modifyForm.currentTr = a_element.closest('tr').addClass('selected');
                        filesTable.modifyForm.toWhere
                            .val(decodeURI(getFilesSectionUrl(a_element.attr('href'))));
                        return false;
                    };
                    first.click(function() {
                        return onClicked($(this));
                    });
                    enableExpandMoveDir(null, expanding, {
                        action: 'inplace'
                    }, onClicked, folders);
                });
            this.modifyForm.toWhere = this.modifyForm.filesEntry.body.find('.modify_input');
            this.modifyForm.currentTr = this.modifyForm.filesEntry.body.find('table.dirlist tr:first');
            this.modifyForm.currentTr.addClass('selected');
            this.modifyForm.selectedEntries = this.modifyForm.filesEntry.body.find('.selected_items');
            this.modifyForm.selectedTemplate = this.modifyForm.selectedEntries.find('input:first').first();
            this.modifyForm.selectedEntries.empty();

            this.modifyForm.filesEntry.getFilename = function () {
                return this.filesTable.modifyForm.selectedEntries.first()
                    .children('input').map(function() { return $(this).val(); }).get();
            };
            this.modifyForm.entryChecked = function (filesEntry, wasChecked) {
                if (wasChecked) {
                    if (!filesEntry.modifyFormData) {
                        filesEntry.modifyFormData = [];
                    }
                    var selectedTemplate = this.selectedTemplate.clone()
                        .val(filesEntry.getFilename());
                    this.selectedEntries.each(function () {
                        var modifyFormInput = selectedTemplate.clone();
                        filesEntry.modifyFormData.push(modifyFormInput);
                        $(this).append(modifyFormInput);
                    });
                }
                else {
                    while (filesEntry.modifyFormData.length > 0) {
                        var item = filesEntry.modifyFormData.pop();
                        item.remove();
                    }
                }
            };

            this.newFolder = new TableFormHandler(filesTable,
                '.mode_button.add_mode', '.add_mode', 'add_mode', null, function(newFolder) {
                    // This should be called after the mouseUp event. For a workaround:
                    setTimeout(function() {
                        newFolder.filesEntry.body.find('input[type="text"]').focus();
                    }, 100);
                });
            this.uploadFile = new TableFormHandler(filesTable,
                '.mode_button.upload_mode', '.upload_mode', 'upload_mode');
            if (this.currentFormHandler) {
                this.currentFormHandler.onOpened();
            }
        }
    },
    entryChecked: function (filesEntry, wasChecked) {
        if (this.modifyForm) {
            this.modifyForm.entryChecked(filesEntry, wasChecked);
        }
        this.currentCheckCount += (wasChecked ? 1 : -1);
        if (this.currentCheckCount == this.maxCheckCount) {
            this.checkAllCheckbox.attr('checked', 'checked');
        }
        else if (this.checkAllCheckbox.attr('checked', 'checked')) {
            this.checkAllCheckbox.removeAttr('checked');
        }
    },
    setCurrentMode: function(new_mode) {
        this.currentFolderModeButton.removeClass('current_mode_button');
        var mode = this.getCurrentMode();
        if (mode != '') {
            this.table.removeClass(mode);
            if (new_mode && new_mode == mode) {
                return false;
            }
        }
        if (new_mode) {
            this.currentFolderModeButton = this.filesHeading.find('.mode_button.'+new_mode);
            this.currentFolderModeButton.addClass('current_mode_button');
            this.table.addClass(new_mode);
        }
        return true;
    },
     getCurrentMode: function() {
         for (var i=0;i<availableTableModes.length;i++) {
             if (this.table.hasClass(availableTableModes[i])) {
                 return availableTableModes[i];
             }
         }
         return '';
     }
};

$(document).ready(function () {
    // Init files tables
    $('.files_table').each(function () {
        var filesTable = new FilesTable(this);
    });
    // In narrow case of wiki macros, there is no files_table
    // Init all elements marked with on_click_follow
    onClickFollowInitializer($('.files_entry_head.on_click_follow'));

    // Init clipboard
    // If clipboard button is not visible, don't bother initializing clipboard
    var copyButton = $('#copybutton');
    if(copyButton.length == 0) {
        return;
    }

    var clip = new ZeroClipboard($("#copybutton"), {
      moviePath: "/htdocs/theme/flash/ZeroClipboard.swf"
    });

    clip.on('load', function (client) {
      //console.log("Flash movie loaded and ready.");
      console.log("Load repoaddress value: "+$("#map_address").val());
      clip.setText($("#map_address").val());
    });

    $("#repoaddress").on("load", function(){
      clip.setText($(this).text());
    });

    $("#repoaddress").on("change", function(){
      clip.setText($(this).text());
    });

    clip.on('noflash', function (client) {
      $("#protocol_selection").hide();
    });

    clip.on('complete', function (client, args) {
      console.log("Copied text to clipboard: " + args.text );
    });
});
})(window);
