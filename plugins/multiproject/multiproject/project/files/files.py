# -*- coding: utf-8 -*-
from pkg_resources import resource_filename
import os.path

from genshi.builder import tag
from genshi.filters import Transformer
from trac.core import Component, implements, TracError
from trac.perm import IPermissionRequestor, PermissionError
from trac.web import IRequestHandler, ITemplateStreamFilter
from trac.web.chrome import ITemplateProvider, INavigationContributor, add_stylesheet, add_script, add_notice, add_script_data
from trac.web.api import HTTPNotFound
from trac.mimeview.api import Mimeview
from trac.web.chrome import add_warning
from trac.util.translation import _

from multiproject.common.projects import Project
from multiproject.core.users import get_userstore
from multiproject.core.files.api import MappedFileNode, \
    ProjectDownloadEntry, get_div_class, InvalidOperationError
from multiproject.core.util.util import format_filename
from multiproject.project.files.timeline import FilesEventNotifier
from multiproject.project.files.core import FilesCoreComponent


CHUNK_SIZE = 4096

def _is_current_mode(node, mode, target_filename, current_mode):
    """
    Helper function for displaying the CSS class in multiproject_files_util.html.

    :return: True, if mode should have "current mode" CSS class, False otherwise.
    """
    if not node:
        if current_mode == mode:
            return True
        elif mode == 'modify_mode' and current_mode.endswith('multiple_mode'):
            return True
        else:
            return False
    else:
        if node.filename == target_filename:
            if current_mode == mode:
                return True
            else:
                return False
        elif mode == 'show_mode':
            return True
        else:
            return False

class FilesModule(Component):
    """
    Trac component for showing the Files tab.
    """
    implements(ITemplateProvider, IRequestHandler, INavigationContributor, IPermissionRequestor)

    # IRequestHandler methods

    def match_request(self, req):
        """ Path used for showing this page
        """
        return req.path_info == '/files' or req.path_info.startswith('/files/')

    def process_request(self, req):
        """ Process request for listing, creating and removing projects
        """

        files_core = FilesCoreComponent(self.env)
        timeline_notifier = FilesEventNotifier(self.env)
        node_factory, download_config = files_core.files_node_factory_and_config(req)
        if req.args.get('redirect') == 'downloads':
            req.perm.require('FILES_DOWNLOADS_VIEW')
            if download_config.downloads_dir == '':
                raise HTTPNotFound(_("The project doesn't have downloads directory."))
            req.redirect(req.href.files(download_config.downloads_dir))

        user_store = get_userstore()
        user = user_store.getUser(req.authname)

        env_name = download_config.env_name

        node = MappedFileNode.from_request_path_info(req.path_info, node_factory)
        open_in_mode_mode = ''
        filename = None
        if req.args.get('action') == 'open_in_mode':
            open_in_mode_mode = req.args.get('mode')
        if not node.exists():
            if node.is_download() and node.download().is_available():
                node.delete()
            raise HTTPNotFound(_("The file was not found!"))
        if req.method == 'POST' and not req.args.get('cancel'):
            # Each X_from_request or X_by_request method does permission check
            action = req.args.get('action')
            # need to delete a file?
            if action == 'delete_multiple' or action == 'delete':
                self.process_delete(action, node, node_factory, req, timeline_notifier)
            elif action == 'add_file':
                filename, open_in_mode_mode = self.process_add_file(node,
                    req, timeline_notifier, user)
            elif action == 'move_multiple' or action == 'rename':
                self.process_move(action, node, node_factory, req,
                    timeline_notifier, user)
            elif action == 'add_folder':
                try:
                    new_dir = node.create_dir_from_request(req, user.id, timeline_notifier)
                    if not new_dir:
                        add_warning(req, _("No folder name was given"))
                    else:
                        filename = new_dir.filename
                        open_in_mode_mode = 'show_mode'
                except TracError as e:
                    add_warning(req, _("Error when creating a new directory: ") + str(e))
            elif action == 'update':
                filename, open_in_mode_mode = self.process_update(node, node_factory, req,
                    timeline_notifier, user)

        if node.is_dir():
            if open_in_mode_mode:
                if not filename:
                    filename = req.args.get('target')
                return self.show_dir(req, node, node_factory, files_core, user_store,
                    target_filename=filename, current_mode=open_in_mode_mode)
            else:
                return self.show_dir(req, node, node_factory, files_core, user_store)
        elif node.is_file():
            mimeview = Mimeview(self.env)
            try:
                node.show_file(req, mimeview, timeline_notifier)
            except InvalidOperationError as e:
                pass
            else:
                add_warning(req, _("Error was received when displaying the file"))
            parent_node = node.get_parent_dir()
            # Error was obtained
            return self.show_dir(req, parent_node, node_factory, files_core, user_store)
        else:
            raise TracError(_('Invalid filesystem node was requested'))

    def _get_selected_files(self, req, node, is_single_action):
        if not node.is_dir():
            raise TracError('Actions for selected not permitted for other than folders.')
        if is_single_action:
            selected_files = req.args.get('target')
        else:
            selected_files = req.args.get('selected_file[]')
        if not selected_files:
            add_warning(req, _("No files were selected."))
            selected_files = []
        elif not isinstance(selected_files, list):
            selected_files = [selected_files]
        return selected_files

    def process_update(self, node, node_factory, req, timeline_notifier, user):
        open_in_mode_mode = ''
        filename = None
        selected_files = self._get_selected_files(req, node, True)

        # Updating the meta-info can currently be done only for one file at a time
        if len(selected_files) == 1:
            filename = selected_files[0]
            relative_path = os.path.join(node.relative_path, filename)

            target_node = MappedFileNode.from_path(relative_path, node_factory,
                assume_relative_path=True)
            from_dir = os.path.dirname(target_node.relative_path)
            moved_node = None

            # If the filename was changed, we have to do the move_by_request
            if req.args.get('to_relative_path', filename) != filename:

                try:
                    moved_node = target_node.move_by_request(req, user.id,
                        timeline_notifier,
                        destination_is_dir=False, update_also=True)
                except TracError as e:
                    add_warning(req, _("Could not move file or folder %(filename)s: ",
                        filename=target_node.filename) + str(e))

                # If the moving was successful, add a proper notice
                if moved_node:
                    target_node = moved_node
                    self.log.debug("update target_node %s", target_node)
                    destination = target_node.get_parent_dir()
                    destination_link = tag.a(target_node.filename,
                        href=destination.get_href(req))
                    sentence = _("Renamed and updated file %(filename)s successfully to ",
                        filename=selected_files[0])
                    add_notice(req, tag(sentence, destination_link))
                    if from_dir == os.path.dirname(target_node.relative_path):
                        open_in_mode_mode = 'show_mode'
                        filename = target_node.filename

            # If the filename was not changed, just updating the file info is enough
            else:
                try:
                    target_node.update_metadata_from_request(req, user.id)
                    open_in_mode_mode = 'show_mode'
                    filename = target_node.filename
                    add_notice(req, _("Updated file %(filename)s download information.",
                        filename=filename))
                except TracError as e:
                    self.log.exception("foobar")
                    add_warning(req, _("Could not save the downloads information for file."))
        return filename, open_in_mode_mode

    def process_add_file(self, node, req, timeline_notifier, user):
        open_in_mode_mode = ''
        filename = None
        uploads = req.args.get('upload[]')
        # not uploads is True, when it is FieldStorage (one file has been uploaded).
        if not isinstance(uploads, list):
            uploads = [uploads]
        successful_files = 0
        is_multiple_upload = len(uploads) != 1
        for upload in uploads:
            new_node = None
            try:
                new_node = node.create_file_from_request(req, upload,
                    user.id, timeline_notifier, is_multiple_upload)
                self.log.info('File %s uploaded', new_node.relative_path)
                successful_files += 1
            except TracError as e:
                add_warning(req, _("Error when saving the file: ") + str(e))
        if successful_files and successful_files == len(uploads):
            if successful_files == 1:
                open_in_mode_mode = 'show_mode'
                filename = new_node.filename
                add_notice(req, _("Saved file %(filename)s successfully.",
                    filename=filename))
            else:
                add_notice(req, _("Saved files successfully."))
        elif successful_files:
            add_notice(req, tag(_("Saved other files successfully.")))
        return filename, open_in_mode_mode

    def process_move(self, action, node, node_factory, req, timeline_notifier, user):
        is_rename = action == 'rename'
        selected_files = self._get_selected_files(req, node, is_rename)
        successful_files = 0
        target_node = None
        for filename in selected_files:
            relative_path = os.path.join(node.relative_path, filename)
            target_node = MappedFileNode.from_path(relative_path, node_factory,
                assume_relative_path=True)
            try:
                moved_node = target_node.move_by_request(req, user.id,
                    timeline_notifier, destination_is_dir=not is_rename,
                    update_also=is_rename)
                target_node = moved_node
                successful_files += 1
            except TracError as e:
                add_warning(req, _("Could not move file or folder %(filename)s: ",
                    filename=target_node.filename) + str(e))
        destination_link = None
        if target_node:
            destination = target_node.get_parent_dir()
            if is_rename:
                filename = target_node.filename
            else:
                filename = destination.relative_path == '.' and _('Home')\
                or destination.filename
            destination_link = tag.a(filename, href=destination.get_href(req))
        if successful_files and successful_files == len(selected_files):
            if successful_files == 1:
                if is_rename:
                    sentence = _("Renamed file %(filename)s successfully to ",
                        filename=selected_files[0])
                else:
                    sentence = _("Moved file %(filename)s successfully to location ",
                        filename=selected_files[0])
                add_notice(req,
                    tag(sentence, destination_link))
            else:
                # Batch rename not implemented
                add_notice(req,
                    tag(_("Moved files successfully to location "), destination_link))
        elif successful_files:
            add_notice(req, tag(_("Moved other files successfully to location "),
                destination_link))

    def process_delete(self, action, node, node_factory, req, timeline_notifier):
        selected_files = self._get_selected_files(req, node, action == 'delete')
        successful_files = 0
        target_node = None
        for filename in selected_files:
            relative_path = os.path.join(node.relative_path, filename)
            removed_node = MappedFileNode.from_path(relative_path, node_factory,
                assume_relative_path=True)
            try:
                removed_node.remove_by_request(req, timeline_notifier)
                successful_files += 1
            except TracError as e:
                add_warning(req, _("Could not remove file or folder %(filename)s: ",
                    filename=filename) + str(e))
        if len(selected_files) == 1 and successful_files == 1:
            add_notice(req, _("Removed file %(filename)s successfully",
                filename=selected_files[0]))
        elif successful_files and successful_files == len(selected_files):
            add_notice(req, _("Removed files successfully"))
        elif successful_files:
            add_notice(req, _("Removed other files successfully"))

    def show_dir(self, req, node, node_factory, files_core, user_store,
                  target_filename='', current_mode=''):
        """
        Shows the content of a dir in a browser

        :param MappedFileNode node: mapped file node
        """
        only_downloads_dir = False
        try:
            node.require_read_perm(req.perm)
        except PermissionError as e:
            if node.relative_path == '.' and 'FILES_DOWNLOADS_VIEW' in req.perm:
                add_warning(req, _("You must have FILES_VIEW permission "
                                   "to view files in Home folder."))
                only_downloads_dir = True
            else:
                raise

        dirs, files = self.get_dirs_and_files(only_downloads_dir, node)
        # Ajax request case (after permission check)
        if req.get_header('X-Requested-With') == 'XMLHttpRequest':
            return 'multiproject_files_tree.html', {'tree_dirs': dirs, 'tree_files': files}, None

        # Fetch information for showing dir content
        dav_url = '/'.join([self.env.abs_href().rsplit('/',1)[0], files_core.url_dav_path,
            self.env.project_identifier, ''])

        (parent_folders, current_folder,
            root_node) = self.get_breadcrumb_data(node)
        root_dirs, root_files = [], []
        if node.relative_path == '.':
            root_dirs, root_files = dirs, files
        else:
            if 'FILES_VIEW' in req.perm:
                root_dirs, root_files = root_node.get_dirs_and_files()
            elif 'FILES_DOWNLOADS_VIEW':
                root_dirs, root_files = self.get_dirs_and_files(True, root_node)

        if node.is_download():
            can_edit = 'FILES_DOWNLOADS_ADMIN' in req.perm
        else:
            can_edit = 'FILES_ADMIN' in req.perm

        files_core.order_files_and_dirs(req, node.is_download(), dirs, files)

        # Setup downloads data
        old_downloads = []
        user_by_id = {}
        if node.is_download():
            if not can_edit:
                # Show only those downloads which are available
                available_files = []
                for file in files:
                    if file.download().is_available():
                        available_files.append(file)
                files = available_files

            for file in files:
                download = file.download()
                if download.uploader_id and not user_by_id.has_key(download.uploader_id):
                    user_by_id[download.uploader_id] = user_store.getUserWhereId(
                        download.uploader_id)

            old_downloads = ProjectDownloadEntry.get_all_download_entries(node_factory.project_id,
                only_deleted=True)
            for old_download in old_downloads:
                old_download.filename = os.path.basename(old_download.download_path)
                if old_download.uploader_id and not user_by_id.has_key(old_download.uploader_id):
                    user_by_id[old_download.uploader_id] = user_store.getUserWhereId(
                        old_download.uploader_id)

        table_mode = 'no_mode'
        files_entry_class = lambda node: ''
        if target_filename:
            if current_mode:
                ok_modes = ('edit_mode', 'move_mode', 'show_mode', 'delete_mode')
                if current_mode not in ok_modes:
                    add_warning(req, _('The mode argument was not one of follows: %(list)s',
                            list=','.join(ok_modes)))
                    current_mode = 'show_mode'
                files_entry_class = lambda node: current_mode if node.filename == target_filename else ''
        else:
            if current_mode:
                ok_modes = ('move_multiple_mode', 'delete_multiple_mode', 'add_mode', 'upload_mode', 'modify_mode')
                if current_mode not in ok_modes:
                    add_warning(req, _('The mode argument was not one of follows: %(list)s',
                        list=','.join(ok_modes)))
                    current_mode = ''
                if current_mode.endswith('multiple_mode'):
                    table_mode = 'modify_mode'
                elif current_mode == 'modify_mode':
                    table_mode = 'modify_mode'
                    current_mode = 'modify_mode'
                else:
                    table_mode = current_mode
        action_row_attrs = None
        if can_edit:
            action_row_attrs = {}
            not_selected = {'row': {}, 'td': {}, 'div': {}}
            for key in ('modify_mode', 'add_mode', 'upload_mode'):
                if key == table_mode:
                    action_row_attrs[key] = {'row': {'style': 'display: table-row;'},
                                             'td': {'style': 'display: table-cell;'},
                                             'div': {'style': 'display: block;'}}
                else:
                    action_row_attrs[key] = not_selected

        data = {'dir_node': node,
                'parent_folders': parent_folders,
                'files_entry_class': files_entry_class,
                'current_folder': current_folder,
                'can_edit': can_edit,
                'target_filename': target_filename,
                'current_mode': current_mode,
                'is_current_mode': _is_current_mode,
                'current_table_mode': table_mode,
                'action_row_attrs': action_row_attrs,
                'user_by_id': user_by_id,
                'files': files,
                'dirs': dirs,
                'root_files': root_files,
                'root_dirs': root_dirs,
                'url': req.base_path,
                'dav_url': dav_url,
                'helpurl': self.config.get('multiproject', 'dav_help_url', ''),
                'old_downloads': old_downloads,
                'format_filename': format_filename,
                'get_div_class': get_div_class}

        add_stylesheet(req, 'multiproject/css/files.css')
        add_script(req, 'multiproject/js/files.js')
        if can_edit:
            add_script(req, 'multiproject/js/expand_dir.js')
        add_script_data(req, {'files_data': {
            'is_download': 1 if node.is_download() else 0
        }})

        return 'multiproject_files.html', data, None

    def get_breadcrumb_data(self, node):
        root_node = node.node()
        root_node.populate_file_data('.',exists_and_is_dir=True)
        root_node.populate_url_data()

        root_node.filename = _('Home')
        parent_folders = []
        current_node = node
        current_folder = current_node
        if current_node.relative_path == '.':
            current_folder = root_node
        else:
            while True:
                current_node = current_node.get_parent_dir()
                if current_node.relative_path == '.':
                    parent_folders.insert(0, root_node)
                    break
                parent_folders.insert(0, current_node)
        return parent_folders, current_folder, root_node

    def get_dirs_and_files(self, only_downloads_dir, node):
        if not only_downloads_dir:
            return node.get_dirs_and_files()
        else:
            if node.downloads_dir:
                downloads_dir = node.node()
                downloads_dir.populate_file_data(node.downloads_dir)
                downloads_dir.populate_url_data()
                if downloads_dir.exists() and downloads_dir.is_dir():
                    return [downloads_dir], []
        return [[], []]

    # INavigationContributor methods

    def get_active_navigation_item(self, req):
        return 'files'

    def get_navigation_items(self, req):
        if 'FILES_VIEW' in req.perm:
            yield ('mainnav', 'files',
                   tag.a('Files', href = req.href.files()))
        elif 'FILES_DOWNLOADS_VIEW' in req.perm:
            yield ('mainnav', 'files',
                   tag.a('Files', href = req.href.files(redirect='downloads')))

    # ITemplateProvider methods

    def get_templates_dirs(self):
        return [resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        return [('multiproject', resource_filename(__name__, 'htdocs'))]

    # IPermissionRequestor methods

    def get_permission_actions(self):
        """
        If file is a download or is changed to be a download,
        FILES_DOWNLOADS_* permissions are required.
        Otherwise, FILES_* permissions are required.
        """
        return ['FILES_DOWNLOADS_VIEW',
                ('FILES_DOWNLOADS_ADMIN', ['FILES_DOWNLOADS_VIEW']),
                'FILES_VIEW',
                ('FILES_ADMIN', ['FILES_VIEW'])]


class FilesSummaryPageFilter(Component):

    implements(ITemplateStreamFilter)

    def filter_stream(self, req, method, filename, stream, data):
        """
        Adds project total count information in project summary block::

            Downloads: 288

        """
        # TODO: Make interface for the project summary box and implement it here

        # Filter only the summary table wiki macro
        if filename != 'multiproject_summary.html':
            return stream

        # Load project and followers info
        project = Project.get(self.env)
        count = ProjectDownloadEntry.total_download_count(project.id)

        if count == 0:
            return stream

        # Add following information into project summary block
        trans = Transformer('//div[@class="summary"]/table').append(
            tag.tr(
                tag.th('Downloads:'),
                tag.td(count)
            )
        )

        return stream | trans
