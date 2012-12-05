# -*- coding: utf-8 -*-
from trac.admin import IAdminPanelProvider, IAdminCommandProvider, AdminCommandError
from trac.core import Component, implements, TracError
from trac.util.text import printout
from trac.web.chrome import add_warning, add_notice
from trac.util.translation import _

from multiproject.core.files.api import  FileSystemNode, MappedFileNode, ProjectDownloadEntry
from multiproject.core.files.files_conf import DownloadDirValidationException, FilesDownloadConfig
from multiproject.project.files.core import FilesCoreComponent
from multiproject.project.files.timeline import FilesEventNotifier

class FilesWebAdmin(Component):
    implements(IAdminPanelProvider)

    # IAdminPanelProvider interface requirement
    def get_admin_panels(self, req):
        if req.perm.has_permission('FILES_DOWNLOADS_ADMIN'):
            yield ('general', _('General'), 'filesdownloads', _('Files Downloads'))

    # IAdminPanelProvider interface requirement
    def render_admin_panel(self, req, category, page, path_info):
        req.perm.require('FILES_DOWNLOADS_ADMIN')

        env_name = self.env.project_identifier
        download_config = FilesDownloadConfig(env_name)

        node_factory = FileSystemNode(download_config.base_path)
        files_console = FilesConsoleAdmin(self.env)
        old_node, old_dir_exists = files_console.get_dir_data(download_config, node_factory)

        self.log.debug('downloads directory is "%s"', download_config.downloads_dir)

        new_dir_name = ''

        if req.method == 'POST':
            req.perm.require('FILES_DOWNLOADS_ADMIN')
            new_dir_name = req.args.get('new_dir_name')
            old_dir_select = req.args.get('old_dir_select')
            old_downloads_dir = req.args.get('old_downloads_dir')

            do_update = True

            if old_downloads_dir:
                if download_config.downloads_dir != old_downloads_dir:
                    add_warning(req, _('The downloads directory has been changed. '
                                       ' Check the new directory and try again, if needed.'))
                    do_update = False

            if do_update:
                can_be_moved = bool(req.args.get('move_also'))
                warning = lambda msg: add_warning(req, msg)
                notice = lambda msg: add_notice(req, msg)
                if old_dir_select and new_dir_name:
                    add_warning(req, _('Cannot decide, what to do: '
                                       'Both old directory selected and new directory name given.'))
                elif not old_dir_select:
                    if old_dir_exists and new_dir_name == old_downloads_dir:
                        add_notice(req, _('Old downloads dir was the required one.'))
                    elif new_dir_name:
                        # Create new directory
                        files_console.handle_change(download_config, new_dir_name, can_be_moved,
                            node_factory, warning, notice)
                        req.redirect(req.href.admin(category, page))
                    else:
                        add_warning(req, _('No new directory name given.'))
                else:
                    if old_dir_exists and old_dir_select == old_downloads_dir:
                        add_notice(req, _('Old downloads dir was the required one.'))
                    elif old_dir_select == '__delete__':
                        if old_dir_exists:
                            files_console.handle_unset(warning, notice)
                            req.redirect(req.href.admin(category, page))
                        else:
                            add_notice(req, _('Old downloads dir was already unset.'))
                    else:
                        files_console.handle_change(download_config, old_dir_select, False,
                            node_factory, warning, notice)
                        req.redirect(req.href.admin(category, page))

        root_node = FileSystemNode.from_path('.', node_factory)
        dirs, files = root_node.get_dirs_and_files()
        default_downloads_directory = FilesCoreComponent(self.env).default_downloads_directory

        data = {
            'downloads_dir': download_config.downloads_dir,
            'available_dirs': dirs,
            'old_dir_exists': old_dir_exists,
            'show_confirm': False,
            'public_downloads_default': default_downloads_directory,
            'new_dir_name': new_dir_name
        }

        return 'multiproject_admin_files.html', data


class FilesConsoleAdmin(Component):
    implements(IAdminCommandProvider)

    # IAdminCommandProvider methods
    def get_admin_commands(self):
        yield ('files download create', '[<downloads directory name>]',
               """Create downloads directory.

If no filename given, use the default from configuration.""",
               None, self._downloads_dir_create)
        yield ('files download set', '<downloads directory name> <move if exists>',
               'Set downloads directory, bool to control whether or not moving the old',
               None, self._downloads_dir_set)
        yield ('files download check', '',
               'Print whether or not the downloads directory exists',
               None, self._downloads_dir_check)
        yield ('files download unset', '',
               'Print whether or not the downloads directory exists',
               None, self._handle_unset)

    def _downloads_dir_create(self, downloads_dir_name=None):
        self._handle_change('downloads-dir-create', downloads_dir_name, False)

    def _downloads_dir_set(self, downloads_dir_name, can_be_moved):
        mapping = {'true':True,'false':False,'0':False,'1':True}
        can_be_moved = mapping.get(can_be_moved.lower(), False)
        self._handle_change('downloads-dir-move', downloads_dir_name, can_be_moved)

    def _downloads_dir_check(self):
        try:
            env_name = self.env.project_identifier
        except AttributeError as e:
            # In case of trac admin commands, project_identifier is not found
            env_name = self.env.path.split('/')[-1]
            self.env.project_identifier = env_name

        download_config = FilesDownloadConfig(env_name)
        node_factory = FileSystemNode(download_config.base_path)
        node, dir_exists = self.get_dir_data(download_config, node_factory)
        if dir_exists:
            printout("[+] {0:<30} '{1:}'".format(env_name, download_config.downloads_dir))
        else:
            printout("[-] {0:<30} '{1:}'".format(env_name, download_config.downloads_dir))

    def _handle_change(self, command, downloads_dir_name, can_be_moved):
        try:
            env_name = self.env.project_identifier
        except AttributeError as e:
            # In case of trac admin commands, project_identifier is not found
            env_name = self.env.path.split('/')[-1]
            self.env.project_identifier = env_name

        download_config = FilesDownloadConfig(env_name)
        if downloads_dir_name is None:
            files_core = FilesCoreComponent(self.env)
            downloads_dir_name = files_core.default_downloads_directory
        node_factory = FileSystemNode(download_config.base_path)

        old_node, old_dir_exists = self.get_dir_data(download_config, node_factory)

        if command == 'downloads-dir-create':
            if old_dir_exists:
                raise AdminCommandError(_('Project already has existing downloads directory'))
            node = FileSystemNode.from_path(downloads_dir_name, node_factory)
            if node.exists():
                raise AdminCommandError(_('The given downloads directory already exists'))

        msg_handler = lambda msg: printout(msg)

        try:
            self.handle_change(download_config, downloads_dir_name, can_be_moved,
                node_factory, msg_handler, msg_handler)
        except TracError as e:
            raise AdminCommandError(str(e))
        if command == 'downloads-dir-create':
            files_core = FilesCoreComponent(self.env)
            mapped_node_factory, mapped_download_config = files_core.files_node_factory_and_config()
            created_node = MappedFileNode.from_path(download_config.downloads_dir,
                mapped_node_factory)
            files_notifier = FilesEventNotifier(self.env)
            files_notifier.node_created('trac', created_node)

    def handle_change(self, download_config, new_downloads_dir,
                      can_be_moved, node_factory, warning, notice):
        """
        :param FilesDownloadConfig download_config: download_configuration configuration
        :returns: True if new
        """
        old_node, old_dir_exists = self.get_dir_data(download_config, node_factory)

        try:
            download_config.downloads_dir = new_downloads_dir
        except DownloadDirValidationException as e:
            raise TracError(_('New downloads directory is not valid: ') + str(e))

        new_node = FileSystemNode.from_path(download_config.downloads_dir, node_factory)
        if new_node.exists() and not new_node.is_dir():
            raise TracError(_('Error: Destination path exists and is a file'))
        elif new_node.exists() and can_be_moved:
            raise TracError(_("Error: Destination path already exists"))

        try:
            download_config.save()
            notice(_('Your changes have been saved.'))
        except Exception as e:
            self.log.exception('Failed to save downloads directory')
            raise TracError(_('Saving new value failed'))

        was_created = False
        if old_dir_exists and can_be_moved:
            try:
                old_node.move(new_node.relative_path)
                notice(_('Moved old downloads directory to be new one'))
                was_created = True
            except Exception as e:
                self.log.exception('Exception while moving old directory to new one')
                warning(_('Error while moving the old directory.'))
        elif not new_node.exists():
            try:
                new_node.get_parent_dir().create_dir(new_node.filename)
                notice(_('Created new downloads directory'))
                was_created = True
            except Exception as e:
                self.log.exception('Creating new downloads directory failed.')
                warning(_('Creating new downloads directory failed.'))
        else:
            # not can_be_moved
            if old_dir_exists:
                try:
                    for entry in ProjectDownloadEntry.get_all_download_entries(
                        node_factory.project_id):
                        entry.delete()
                except Exception as e:
                    warning(_("Marking files as deleted failed"))
            notice(_('Set the new downloads directory to be the directory chosen.'))

        return was_created

    def _handle_unset(self):
        msg_handler = lambda msg: printout(msg)
        self.handle_unset(msg_handler, msg_handler)

    def handle_unset(self, warning, notice):
        try:
            env_name = self.env.project_identifier
        except AttributeError as e:
            # In case of trac admin commands, project_identifier is not found
            env_name = self.env.path.split('/')[-1]
            self.env.project_identifier = env_name
        try:
            files_core = FilesCoreComponent(self.env)
            node_factory, download_config = files_core.files_node_factory_and_config()
            download_config.delete()
            notice(_('Your changes have been saved.'))
        except Exception as e:
            self.log.exception('Failed to unset downloads directory')
            raise TracError(_('Unsetting failed'))
        try:
            for entry in ProjectDownloadEntry.get_all_download_entries(
                node_factory.project_id):
                entry.delete()
        except Exception as e:
            warning(_("Marking files as deleted failed"))

    def get_dir_data(self, download_config, node_factory):
        """
        If there is a file (not dir) corresponding the current download_config.downloads_dir,
        resets the downloads dir to ''
        :returns: (old_node, old_dir_exists)
        """
        old_node = None
        old_dir_exists = False
        if download_config.downloads_dir:
            old_node = FileSystemNode.from_path(download_config.downloads_dir, node_factory)
            if old_node.exists():
                if not old_node.is_dir():
                    # Don't allow the download config to be a file, ever!
                    download_config.reset_downloads_dir()
                else:
                    old_dir_exists = True
        return old_node, old_dir_exists
