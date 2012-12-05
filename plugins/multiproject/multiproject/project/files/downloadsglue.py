# -*- coding: utf-8 -*-
import os
import shutil

from trac.admin import IAdminCommandProvider
from trac.core import Component, implements, TracError
from trac.util import to_unicode
from trac.util import datefmt
from trac.util.html import html
from trac.util.text import printout
from trac.util.translation import _
from trac.web import IRequestHandler
from trac.web.chrome import add_warning
from trac.wiki import IWikiSyntaxProvider, IWikiMacroProvider

from multiproject.core.configuration import conf
from multiproject.core.util import filesystem
from multiproject.core.users import get_userstore
from multiproject.core.files.api import ProjectDownloadEntry, MappedFileNode, \
    FileSystemNode
from multiproject.project.files.core import FilesCoreComponent
from multiproject.project.files.wiki import ProjectDownloadsWiki, DOWNLOADS_GLUE_COMPONENT


def get_download_path(id, filename):
    """
    Returns primary download path for a file with index.
    """
    filename_body, extension = os.path.splitext(filename)
    if extension == '.deb':
        package_name = filename.replace('.','_')
        return '{0}-{1}/{2}'.format(package_name, id, filename)
    else:
        return '{0}-{1}{2}'.format(filename_body, id, extension)

class DownloadsGlue(Component):
    """
    This class provides glue to replace wiki macros, download links, etc, when (modified)
    TracDownloads has been used. This uses the tables of TracDownloads.

    Enable this component only for those projects where the TracDownloads have been used.
    The trac-admin command "files import" will auto-enable this component (if not enabled).
    """

    implements(IRequestHandler, IWikiSyntaxProvider, IWikiMacroProvider)

    def match_request(self, req):
        if req.path_info.startswith('/downloads/'):
            return True
        return False

    def process_request(self, req):
        req.perm.require('FILES_DOWNLOADS_VIEW')
        file_identifier = req.path_info[11:] # 11 == len('/downloads/')
        id_, filename = self._get_id_filename(file_identifier)
        if not id_ or not filename:
            add_warning(req, _("The download for url url %(url)s was not found.",
                url='/downloads/{0}'.format(file_identifier)))
        else:
            files_core = FilesCoreComponent(self.env)
            node_factory, download_config = files_core.files_node_factory_and_config(req)
            primary_path = get_download_path(id_, filename)
            node = MappedFileNode.from_download_path(primary_path, node_factory, True)
            if node.exists() and node.is_download():
                req.redirect(req.href.files(node.relative_path))

            node = MappedFileNode.from_download_path(filename, node_factory, True)
            if node.exists() and node.is_download():
                req.redirect(req.href.files(node.relative_path))

            add_warning(req, _("The old-style download link seems to be broken. "
                               "Checked from %(primary_path)s and %(filename)s",
                                primary_path=primary_path, filename=filename))
        req.redirect(req.href.files({'redirect': 'downloads'}))

    def _get_id_filename(self, param):
        if not param:
            return None, None

        if param.isdigit():
            where_cond = 'id = %s'
        else:
            where_cond = 'file = %s'
        query = "SELECT id, file FROM download WHERE {0} LIMIT 1".format(where_cond)
        try:
            db = self.env.get_read_db()
            cursor = db.cursor()
            cursor.execute(query, param)
            row = cursor.fetchone()
            if row:
                return row[0], row[1]

        except Exception as e:
            env_name = conf.resolveProjectName(self.env)
            # this is the only way, since there are no common exceptions
            if e.__class__.__name__ == 'ProgrammingError':
                self.log.info('Error: "%s". DownloadsGlue should be disabled for "%s".' % (e, env_name))
            else:
                self.log.exception("Download link could not be resolved in %s" % env_name)

        return None, None

    def _get_id_filename_by_filename(self, filename):
        try:
            db = self.env.get_read_db()
            cursor = db.cursor()
            cursor.execute("SELECT id, file FROM download WHERE file = %s", filename)
            row = cursor.fetchone()
            if row:
                return row[0]
        except Exception as e:
            env_name = conf.resolveProjectName(self.env)
            # this is the only way, since there are no common exceptions
            if e.__class__.__name__ == 'ProgrammingError':
                self.log.warning('Error: "%s". DownloadsGlue should be disabled for "%s".' % (e, env_name))
            else:
                self.log.exception("Download link could not be resolved in %s" % env_name)
        return None

    # IWikiSyntaxProvider
    def get_link_resolvers(self):
        yield ('download', self.download_link)

    def get_wiki_syntax(self):
        return []

    def get_macros(self):
        yield 'DownloadsCount'
        yield 'ListDownloads'
        yield 'FeaturedDownloads'
        yield 'ListFeaturedDownloads'
        yield 'CustomListDownloads'
        yield 'CustomFeaturedDownloads'
        yield 'CustomListFeaturedDownloads'

    def get_macro_description(self, name):
        if 'Featured' in name:
            return "Displays featured downloads. Note: This macro is deprecated! Replace by FilesDownloads macro."
        else:
            return "Displays all downloads. Note: This macro is deprecated! Replace by FilesDownloads macro."

    def expand_macro(self, formatter, name, content):
        """
        Stub implementation forwarding the requests to the ProjectDownloadsWiki.
        """
        wiki = ProjectDownloadsWiki(self.env)
        if name == 'DownloadsCount':
            return wiki.expand_macro(formatter, 'FilesDownloadsCount', content)
        elif name in ('ListDownloads', 'FeaturedDownloads', 'ListFeaturedDownloads',
                      'CustomListDownloads', 'CustomFeaturedDownloads',
                      'CustomListFeaturedDownloads'):
            only_featured = str('Featured' in name)
            return wiki.expand_macro(formatter, 'FilesDownloads', '', {'only_featured':only_featured,
                                                                'title': ''})

    def download_link(self, formatter, ns, target, label):
        if ns == 'download':
            if 'FILES_DOWNLOADS_VIEW' not in formatter.req.perm:
                return html.a(label, href='#',
                    title = _('Missing %(permission)s permission',
                                permission='FILES_DOWNLOADS_VIEW'),
                        class_ = 'missing')
            files_core = FilesCoreComponent(self.env)
            wiki = ProjectDownloadsWiki(self.env)
            node_factory, download_config = files_core.files_node_factory_and_config(formatter.req)
            id_, filename = self._get_id_filename(target)
            if id_ and filename:
                primary_path = get_download_path(id_, filename)
                node = MappedFileNode.from_download_path(primary_path, node_factory, True)
                if node.exists() and node.is_download():
                    return wiki.file_link(formatter, 'filesdownload',
                        node.download().download_path, label)

                node = MappedFileNode.from_download_path(filename, node_factory, True)
                if node.exists() and node.is_download():
                    return wiki.file_link(formatter, 'filesdownload',
                        node.download().download_path, label)
            return wiki.file_link(formatter, 'filesdownload', target, label)

class TracDownloadsImporter(Component):
    implements(IAdminCommandProvider)
    def get_admin_commands(self):
        yield ('files import', '[dryrun:flag]',
               """Import files from trac downloads to Files

Optional dryrun:  If equal to -n or --dry-run, dry run

Note: You should run this command as web server user
               """,
               None, self.import_files)

    def import_files(self, dry_run=False):
        dry_run = True if dry_run in ['-n', '--dry-run'] else False
        try:
            env_name = self.env.project_identifier
        except AttributeError:
            # Since open_environment is not used in trac-admin commands
            # we need to manually set the project_identifier
            env_name = self.env.path.split('/')[-1]
            self.env.project_identifier = env_name
        download_data_list = self.get_download_data()
        path = conf.getEnvironmentDownloadsPath(self.env)
        if download_data_list is None:
            printout("env:%(env_name)s, download table was not found" %
                     {'env_name': self.env.project_identifier})
            return
        files_core = FilesCoreComponent(self.env)
        node_factory, download_config = files_core.files_node_factory_and_config()
        env_name = download_config.env_name

        project_files = {}
        first_file = {}
        for download_data in download_data_list:
            filename = download_data['file']
            id_ = download_data['id']
            if filename not in project_files:
                project_files[filename] = []
                first_file[filename] = id_
            project_files[filename].append(id_)

        for download_data in download_data_list:
            filename = download_data['file']
            id_ = download_data['id']
            if not download_data['author_id']:
                printout("env:%(env_name)s file:%(download)s id:%(id_)s: "
                         "The author %(author)s of download %(download)s was not found." %
                         {'env_name':env_name, 'download': filename, 'id_': id_,
                          'author':download_data['author']})
                continue
            base_downloads_path = filesystem.safe_path(path, to_unicode(id_))
            original_node = FileSystemNode(base_downloads_path)
            original_node.populate_file_data(filename)
            from_path = original_node._abs_path_encoded
            existing_node = MappedFileNode.from_download_path(filename, node_factory, True)
            download_path = filename
            if len(project_files[filename]) > 1:
                download_path = get_download_path(id_, filename)
                to_node = MappedFileNode.from_download_path(download_path, node_factory, True)
            else:
                # No duplicate downloads, put it into root
                to_node = existing_node
            if not to_node.is_download():
                printout("env:%(env_name)s file:%(download)s id:%(id_)s: "
                         "With %(rel_path)s: Download information is incorrect" %
                         {'env_name':env_name, 'download': filename, 'id_': id_,
                          'rel_path':to_node.relative_path})
                continue
            if to_node.download().is_available():
                printout("env:%(env_name)s file:%(download)s id:%(id_)s: "
                         "With %(rel_path)s: The download information is already available" %
                         {'env_name':env_name, 'download': filename, 'id_': id_,
                          'rel_path':to_node.relative_path})
                continue
            elif to_node.exists():
                printout("env:%(env_name)s file:%(download)s id:%(id_)s: "
                         "With %(rel_path)s: The download already exists" %
                         {'env_name':env_name, 'download': filename, 'id_': id_,
                          'rel_path':to_node.relative_path})
                continue
            can_be_removed = False
            download = self.populate_new_download(to_node.download(), original_node,
                download_data)
            if len(project_files[filename]) > 1:
                # If there were duplicate filenames, special handling for them is needed
                if (existing_node.exists() and existing_node.is_file()
                        and existing_node.is_download()):
                    old_download = existing_node.download()
                    if (old_download.is_available() and old_download.hash == download.hash
                        and old_download.version == 1
                        and download.uploader_id == old_download.uploader_id
                        and download.created == old_download.created):
                        # Copy all information, which might be changed
                        download.clone_user_values(old_download)
                        download.count = old_download.count
                        can_be_removed = True
                    else:
                        # Else, we just accept that there has been changes
                        # Download count might be duplicated. In that case, manual work
                        # could be done.
                        printout("env:%(env_name)s file:%(download)s id:%(id_)s: "
                             "Cannot remove download because it is not original or has changed, "
                             "download count was %(count)s" %
                             {'env_name':env_name, 'id_': id_, 'download': filename,
                              'count': download.count})
            if not dry_run:
                if os.path.sep in download_path:
                    parent_dir = to_node.get_parent_dir()
                    if not parent_dir.exists():
                        data = {'type': 'dir'}
                        FileSystemNode.create_check(parent_dir, data)
                        FileSystemNode.create_do(parent_dir, data)
                        FileSystemNode.create_post_process(parent_dir, data)
                shutil.copy2(from_path, to_node._abs_path_encoded)
                to_node.chmod()
                self.save_new_download(download)
                if can_be_removed:
                    existing_node.download().delete_completely()
                    existing_node.remove_do({})
            else:
                printout("env:%(env_name)s file:%(download)s id:%(id_)s: "
                         "Would copy file to %(download_path)s%(other)s" %
                         {'env_name':env_name, 'id_': id_, 'download': filename,
                          'download_path': to_node.download().download_path,
                          'other': can_be_removed and ', and would also remove original' or ''})

        was_enabled = False
        if not self.env.is_component_enabled(DOWNLOADS_GLUE_COMPONENT):
            if not dry_run:
                self.env.config.set('components', DOWNLOADS_GLUE_COMPONENT, 'enabled')
                self.env.config.save()
            was_enabled = True
        if download_data_list:
            if was_enabled:
                printout("env:%(env_name)s: downloads handled, component %(component)s enabled."
                         %{'env_name': env_name, 'component': DOWNLOADS_GLUE_COMPONENT})
            else:
                printout("env:%(env_name)s: downloads handled." % {'env_name': env_name})
        else:
            printout("env:%(env_name)s: no downloads found, component %(component)s enabled."
                    %{'env_name': env_name, 'component': DOWNLOADS_GLUE_COMPONENT})

    def populate_new_download(self, download, node, download_data):
        status = ProjectDownloadEntry.STATUS_FILE
        if download_data['featured']:
            status = ProjectDownloadEntry.STATUS_FEATURED
        node.populate_file_data(node.relative_path)
        download.populate_download(node, download_data['author_id'])
        download.description = download_data['description']
        download.platform = download_data['platform']
        download.status = status
        download.created = datefmt.from_utimestamp(download_data['time'] * 1000000)
        download.count = download_data['count']
        return download

    def save_new_download(self, download):
        try:
            download.create_new_version()
        except TracError:
            printout("Could not create download entry for %(filename)s"
                     % {'filename':download.download_path})

    def get_download_data(self):
        platforms = {}
        downloads = []

        def download_from_sql_row(row):
            return {
                'id': row[0],
                'file': row[1],
                'description': row[2],
                'time': row[3], # in timestamp, not in utimestamp
                'count': row[4],
                'author': row[5],
                'platform': row[6], # Will be string instead
                'featured': row[7]
            }

        try:
            db = self.env.get_read_db()
            cursor = db.cursor()
            cursor.execute("SELECT id, name FROM platform")
            for row in cursor:
                platforms[row[0]] = row[1]
            cursor.execute("SELECT id, file, description, time, count, author, platform, featured FROM download")
            for row in cursor:
                downloads.append(download_from_sql_row(row))
        except Exception as e:
            env_name = conf.resolveProjectName(self.env)
            # this is the only way, since there are no common exceptions
            if e.__class__.__name__ == 'ProgrammingError':
                printout("{0}: Get download data failed: {1}".format(env_name, e))
                return None
            else:
                raise
        userstore = get_userstore()
        for download in downloads:
            user = userstore.getUser(download['author'])
            if user:
                download['author_id'] = user.id
            else:
                download['author_id'] = None
            if not download['platform']:
                download['platform'] = ''
            else:
                download['platform'] = platforms[download['platform']]
        return downloads
