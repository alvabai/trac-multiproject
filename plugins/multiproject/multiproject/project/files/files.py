# -*- coding: utf-8 -*-
from cgi import FieldStorage
from pkg_resources import resource_filename
import time, re, os.path, shutil

from genshi.builder import tag
from trac.core import Component, implements, TracError
from trac.web import IRequestHandler
from trac.web.chrome import ITemplateProvider, INavigationContributor
from trac.web.api import RequestDone
from trac.mimeview.api import Mimeview
from trac.web.chrome import add_warning
from trac.util.translation import _

from multiproject.common.projects import Projects
from multiproject.core.configuration import conf
from multiproject.core.analytics.event import EventLogIO
from multiproject.core.util import filesystem
from multiproject.core.path import syspath
from multiproject.core.timeline import TimelineEvent


CHUNK_SIZE = 4096
FILES_MODULE_REGEXP = re.compile(r'/files(?:_trac)?(?:/.*)?$')


class FilesModule(Component):
    """ Trac component for showing project summary
    """
    implements(ITemplateProvider, IRequestHandler, INavigationContributor)

    def match_request(self, req):
        """ Path used for showing this page
        """

        return FILES_MODULE_REGEXP.match(req.path_info)

    def process_request(self, req):
        """ Process request for listing, creating and removing projects
        """
        req.perm.require('WEBDAV_VIEW')

        file_request_info = FileRequestInfo(self.env, req, req.args.get('path'))
        if req.method == 'POST':
            req.perm.require('WEBDAV')
            action = req.args.get('action')
            # need to delete a file?
            if action == 'delete':
                file_request_info.set_additional_file_name(req.args.get('filename'))
                self.delete_file(file_request_info)
            # is there a file coming?
            if action == 'add':
                if 'Filedata' in req.args:
                    upload = req.args.get('Filedata')
                    self.save_file(file_request_info, upload)
            # If deleting or adding file, next view should show the parent view of the current file.
            file_request_info.set_additional_file_name(None)

        # Show the thing in the path
        return self._show_path(file_request_info)

    def _show_path(self, file_request_info):
        """
        Select proper action for path (file, dir or error)

        :param FileRequestInfo file_request_info: File Request Info
        """
        target_path = file_request_info.get_resulting_filesystem_path()
        target_path_encoded = target_path.encode(FILESYSTEM_ENCODING)
        if os.path.isdir(target_path_encoded):
            return self._show_dir(file_request_info)
        if os.path.isfile(target_path_encoded):
            return self._show_file(file_request_info)
        else:
            self.log.debug("Invalid path requested: %s" % target_path)
            raise TracError("Invalid path requested", "Invalid path")

    def _show_file(self, file_request_info):
        """
        Send file to user

        :param FileRequestInfo file_request_info: File Request Info
        """
        req = file_request_info.req

        fs = DavFilesProvider()
        file = fs.get_file(file_request_info)


        fd = open(file.abs_path.encode(FILESYSTEM_ENCODING), "rb")

        try:
            mimeview = Mimeview(self.env)

            # MIME type detection
            str_data = fd.read(1000)
            fd.seek(0)

            mime_type = mimeview.get_mimetype(file.name, str_data)

            req.send_header('Content-Disposition', 'attachment')
            if file.name.endswith('.txt'):
                mime_type = 'text/plain'
            elif not mime_type:
                mime_type = 'application/octet-stream'

            if 'charset=' not in mime_type:
                charset = mimeview.get_charset(str_data, mime_type)
                mime_type = mime_type + '; charset=' + charset

            try:
                req.send_file(file.abs_path.encode(FILESYSTEM_ENCODING), mime_type)
            except RequestDone:
                self.log_event(file_request_info, 'file_downloaded')
        finally:
            fd.close()
            raise RequestDone

    def _show_dir(self, file_request_info):
        """
        Shows the content of a dir in a browser

        :param FileRequestInfo file_request_info: File Request Info
        """
        # Fetch information for showing dir content
        fs = DavFilesProvider()
        project = Projects().get_project(env_name = file_request_info.env_name)
        params = {'domain':conf.domain_name,
                  'project':project.env_name,
                  'dav_path':conf.url_dav_path,
                  'scheme':conf.default_http_scheme}

        dav_url = "%(scheme)s://%(domain)s%(dav_path)s/%(project)s" % params

        data = {'path':"/" + file_request_info.request_path.strip(' '),
                'files':fs.get_files(file_request_info),
                '_project_':project,
                'url' : file_request_info.req.base_path,
                'dav_url': dav_url,
                'helpurl' : conf.dav_help_url}

        # AJAX inplace request handling
        if file_request_info.req.args.get('action') == 'inplace':
            return 'fs_entries.html', data, None

        return 'fs_browser.html', data, None

    def get_active_navigation_item(self, req):
        return 'files'

    def get_navigation_items(self, req):
        if 'WEBDAV_VIEW' in req.perm or 'WEBDAV' in req.perm:
            yield ('mainnav', 'files',
                   tag.a('Files', href = req.href.files()))

    def get_templates_dirs(self):
        return [resource_filename('multiproject.project.files', 'templates')]

    def get_htdocs_dirs(self):
        return []

    def save_file(self, file_request_info, upload):
        """
        Save file

        :param FileRequestInfo file_request_info: FileRequestInfo with paths set
        :param any upload: The file object posted
        """
        if not isinstance(upload, FieldStorage):
            add_warning(file_request_info.req, _('No file was uploaded.'))
            return

        if not upload.filename:
            raise TracError("Can't find filename")

        upload_filename = upload.filename.replace('\\', '/').replace(':', '/')
        upload_filename = os.path.basename(upload_filename)
        if not upload_filename:
            raise TracError('No file uploaded')

        file_request_info.set_additional_file_name(upload_filename)

        target_path = file_request_info.get_resulting_filesystem_path()
        target_path_encoded = target_path.encode(FILESYSTEM_ENCODING)

        if os.path.isfile(target_path_encoded):
            raise TracError('File name "%s" already exists' % upload_filename)

        # Open a file
        fd = os.open(target_path_encoded, os.O_RDWR | os.O_CREAT)

        # Now get a file object for the above file.
        target_file = os.fdopen(fd, "w+")

        try:
            shutil.copyfileobj(upload.file, target_file)

            # '///' has to be here, since also the dav access provides similar urls
            argument = '///' + file_request_info.get_resulting_request_path()
            self.log_event(file_request_info, 'file_uploaded')
            self.log.warning('File %s uploaded', target_path)
            TimelineEvent(file_request_info.env_name, file_request_info.req.authname).filestab_event("PUT", argument)
        except:
            self.log.exception("Failed to save the file: %s / %s" % (target_path, upload_filename))
            raise TracError("Failed to save the file")

        finally:
            target_file.close()

    def delete_file(self, file_request_info):
        """
        Delete file

        :param FileRequestInfo file_request_info: file_request_info with paths and filename set
        """
        # check that user can access ONLY own project files. If there is .. in some part of path, stop!
        target_path = file_request_info.get_resulting_filesystem_path()
        target_path_encoded = target_path.encode (FILESYSTEM_ENCODING)

        self.log.debug("trying to delete " + target_path)
        if not os.path.isfile(target_path_encoded):
            self.log.warning("file %s does not exist", target_path)
            raise TracError('Specified file name does not exist')

        if os.path.isdir(target_path_encoded):
            self.log.warning("%s is a directory, can't delete", target_path)
            raise TracError("Target path is a directory, can't delete")

        try:
            os.remove(target_path_encoded)
            # '///' has to be here, since also the dav access provides similar urls
            argument = '///' + file_request_info.get_resulting_request_path()
            self.log_event(file_request_info, 'file_deleted')
            self.log.warning('File %s removed', target_path)
            TimelineEvent(file_request_info.env_name, file_request_info.req.authname).filestab_event("DELETE", argument)
        except:
            self.log.exception("Failed to delete the file %s" % target_path)
            raise TracError('Failed to delete the file')

    def log_event(self, file_request_info, event_name):
        """
        Method to log events by calling EventLogIO()

        :param FileRequestInfo file_request_info: file_request_info with paths and filename set
        :param str event_name: string describing the event
        """
        event_names = ['file_uploaded', 'file_deleted', 'file_downloaded']
        if event_name not in event_names:
            conf.log.error("Files tab ValueError")
            raise ValueError

        log = EventLogIO()
        event = {
            'event': event_name,
            'project': file_request_info.env_name,
            'username': file_request_info.req.authname,
            'comment': 'Action via Files tab'
        }
        log.write_event(event)


class DavFilesProvider(object):
    """ Helper class for building FSNode:s from paths
    """
    def __init__(self):
        self.ignore_folders = ['.DAV']

    def get_files(self, file_request_info):
        """ Returns a list of all files in a given path

            if not dir, returns None

            :param FileRequestInfo file_request_info: File request info
        """
        names = file_request_info.get_resulting_request_path().split('/')
        for name in names:
            if name in self.ignore_folders:
                raise TracError("Invalid path requested", "Invalid path")

        target_path = file_request_info.get_resulting_filesystem_path()
        target_path_encoded = target_path.encode(FILESYSTEM_ENCODING)

        relative_path = file_request_info.get_resulting_request_path()

        if not os.path.isdir(target_path_encoded):
            return None

        dirs = []
        files = []
        for file in os.listdir(target_path_encoded):
            abs_path = "%s/%s" % (target_path, file)
            abs_path_encoded = abs_path.encode(FILESYSTEM_ENCODING)
            link_path = "%s/%s" % (relative_path, file)
            if os.path.isdir(abs_path_encoded):
                node = FSNode(link_path, abs_path, 'dir')
                if node.name not in self.ignore_folders:
                    dirs.append(node)
            if os.path.isfile(abs_path_encoded):
                files.append(FSNode(link_path, abs_path, 'file'))
        return dirs + files

    def get_file(self, file_request_info):
        """ Creates FSNode from WebDAV dir of environment (env_name)

            if not file, returns None
        """
        target_path = file_request_info.get_resulting_filesystem_path()
        target_path_encoded = target_path.encode(FILESYSTEM_ENCODING)

        if not os.path.isfile(target_path_encoded):
            return None

        return FSNode(file_request_info.get_resulting_request_path(), target_path, 'file')


class FSNode(object):
    """
    Simple structure holding all file information of a single file
    :param str rel_path: A relative path like "figure.png" or "folder/figure.png"
    :param str abs_path: An absolute path like "/path/to/figure.png" or "/path/to/folder/figure.png"
    """
    def __init__(self, rel_path, abs_path, kind):

        if kind not in ['dir', 'file']:
            raise AttributeError
        self.kind = kind
        self.path = rel_path
        self.abs_path = abs_path
        parts = rel_path.rsplit('/', 1)
        self.name = parts[-1]
        (self.mode, self.ino, self.dev, self.nlink, self.uid,
         self.gid, self.size, self.st_atime, self.st_mtime,
         self.st_ctime) = os.stat(self.abs_path.encode(FILESYSTEM_ENCODING))

        self.mtime = time.ctime(self.st_mtime)
        self.atime = time.ctime(self.st_atime)
        self.ctime = time.ctime(self.st_ctime)

class FileRequestInfo(object):
    """
    Helper for the files requests, helping to keep the request (url) path
    and the corresponding filesystem path synced.

    :member req: request object
    :member request_path: Request path, can be empty, doesn't contain starting slash '/'
    :member filesystem_request_base_path: Request base path, pointing to the directory corresponding the request path
    :member additional_relative_path: additional relative path (checked for that doesn't contain "..")
    :member additional_file_name: additional file name (checked for that doesn't contain "..")
    :member get_resulting_request_path():
    :member get_resulting_filesystem_path():
    """
    def __init__(self, env, req, additional_relative_path = '', additional_file_name = ''):
        """

        """
        self.req = req
        self.env = env
        self.additional_relative_path = u''
        self.additional_file_name = u''

        self.set_additional_relative_path(additional_relative_path)
        self.set_additional_file_name(additional_file_name)

        # env_name must not contain '/'
        self.env_name = conf.resolveProjectName(self.env)

        # request_path
        # skip the "files/" part of the request
        self.request_path = ''
        request_parts = self.req.path_info.split('/', 2)
        if len(request_parts) > 2:
            tmp_request_path = request_parts[2]
            if tmp_request_path:
                # secure not empty request_path with normpath
                self.request_path = os.path.normpath(tmp_request_path)

        # self.request_path can be empty string in some cases
        self.filesystem_request_base_path = filesystem.safe_path(syspath.dav, self.env_name, self.request_path)
        self.resulting_request_path = None
        self.resulting_filesystem_path = None

    def set_additional_relative_path(self, additional_relative_path):
        self.resulting_request_path = None
        self.resulting_filesystem_path = None
        if additional_relative_path:
            self.additional_relative_path = unicode(additional_relative_path)
        else:
            self.additional_relative_path = u''

    def set_additional_file_name(self, additional_file_name):
        self.resulting_request_path = None
        self.resulting_filesystem_path = None
        if additional_file_name:
            self.additional_file_name = unicode(additional_file_name)
        else:
            self.additional_file_name = u''

    def get_resulting_request_path(self):
        """
        Returns request path.

        This method caches the result.

        For example, if full path is "/MyProject/files/folderX/folderY/", additional relative path is "folderZ"
        and additional file name is "file.txt", returns "folderX/folderY/folderZ/file.txt".
        """
        if self.resulting_request_path:
            return self.resulting_request_path

        self.resulting_request_path = filesystem.safe_path(
            self.request_path,
            self.additional_relative_path,
            self.additional_file_name)

        return self.resulting_request_path

    def get_resulting_filesystem_path(self):
        """
        Returns filesystem path to the folder corresponding get_resulting_request_path.

        This method caches the result.

        If request url is "/MyProject/files/folderX/folderY/file.txt", returns the path to the corresponding file.
        """
        if self.resulting_filesystem_path:
            return self.resulting_filesystem_path

        self.resulting_filesystem_path = filesystem.safe_path(
            self.filesystem_request_base_path,
            self.additional_relative_path,
            self.additional_file_name)
        return self.resulting_filesystem_path


    def __str__(self):
        """
        For debug purposes.
        """
        return """FileRequestInfo  %s:%s (%s),\n  %s:%s (%s),\n  %s:%s (%s),\n  %s:%s (%s),\n  %s:%s (%s)   FileRequestInfo resulting...\n  %s:%s (%s),\n  %s:%s (%s)",""" % (
            "self.req", self.req, self.req.__class__,
            "env_name", self.env_name, self.env_name.__class__,
            "additional_relative_path", self.additional_relative_path, self.additional_relative_path.__class__,
            "additional_file_name", self.additional_file_name, self.additional_file_name.__class__,
            "request_path", self.request_path, self.request_path.__class__,
            "resulting filesystem_path", self.get_resulting_filesystem_path(), self.get_resulting_filesystem_path().__class__,
            "resulting request_path", self.get_resulting_request_path(), self.get_resulting_request_path().__class__)

FILESYSTEM_ENCODING = 'utf-8'
