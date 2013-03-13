# -*- coding: utf-8 -*-
"""
:py:class:`ProjectDownloads`::

    A class containing methods to get and manipulate project downloads.

:py:class:`ProjectDownload`::

    A class representing one download item.

:py:class:`ProjectDownloadHistory`

    A class representing one download history item, created when the download item is deleted.

"""
from hashlib import sha256
import stat
import os
import shutil
from datetime import datetime
from cgi import FieldStorage
from urlparse import urlparse
import weakref

from trac.core import TracError, Interface
from trac.web.api import RequestDone, HTTPNotFound
from trac.web.chrome import add_warning
from trac.util import datefmt
from trac.util.translation import _

from multiproject.core.configuration import conf
from multiproject.core.db import admin_query, admin_transaction, safe_int
from multiproject.core.util import filesystem
from multiproject.core.util.filesystem import InvalidFilenameOrPath


FILESYSTEM_ENCODING = 'utf-8'


def normalized_base_url(base_url):
    parsed_url = urlparse(base_url)[2]
    if not parsed_url:
        raise filesystem.InvalidFilenameOrPath(_("Invalid base url"))
    return parsed_url.rstrip('/')


class FileSystemNode(object):
    """
    Represents a file system node with a given path inside base_path.
    For security reasons, creation will fail if path is not base_path or inside it.

    For creating new node when you have already one FileSystemNode instance,
    use the static method FileSystemNode.from_path.

    If you don't have one, first create FileSystemNode,
    normalize it via self.normalize(), and then populate file related data with
    populate_file_data(relative_path).
    """

    def __init__(self, base_path):
        """

        :param base_path: normalized base path.
        """
        # These are populated in populate_file_data

        # base_path is absolute path without trailing slash.
        # Example values: '/foobar/other'
        self.base_path = base_path
        # example values: '.', 'foobar/other'
        self.relative_path = None
        self._abs_path_encoded = None
        self.filename = None
        self._exists = False
        self._is_file = None
        self._is_dir = None

        # If dir, this is used to cache dirs and files in self.get_dirs_and_files()
        self._dirs_and_files = None

        # If self.exists, these are populated in populate_file_data
        # These are in UTC timezone
        self.time_modified = None
        self.time_accessed = None
        self.time_changed = None
        self.size = None

        self._hash = None
        self._is_empty_dir = None
        self._parent_dir = None

    def node(self):
        """
        :return: un-populated instance of self.__class__ (FileSystemNode in this case).
        """
        return FileSystemNode(self.base_path)

    def normalize(self):
        self.base_path = filesystem.get_normalized_base_path(self.base_path)

    @staticmethod
    def from_path(path, node_factory, assume_relative_path=False):
        """
        Create FileSystemNode (a file or dir) from path.

        :param path: unicode string
        :param :py:class:`FileSystemNode` node_factory: node, which is used as factory
        :param assume_relative_path: whether the path is relative to base_path or absolute
        """

        # validate and secure paths
        base_path = node_factory.base_path
        relative_path = filesystem.get_normalized_relative_path(base_path, path,
            assume_relative_path)

        node = node_factory.node()
        node.populate_file_data(relative_path)
        return node

    def populate_file_data(self, relative_path, exists_and_is_dir=False, exists_and_is_file=False):
        """
        .. NOTE::

            time_* and size are not set when exists_and_is_dir or exists_and_is_file are True.

        :param str base_path: normalized base path
        :param str relative_path: relative path (relative to base path)
        :param bool exists_and_is_dir: for short circuit
        :param bool exists_and_is_file: for short circuit
        """
        relative_path = filesystem.get_normalized_relative_path(self.base_path, relative_path)
        self.relative_path = relative_path

        if self.relative_path == '.':
            self._abs_path_encoded = self.base_path.encode(FILESYSTEM_ENCODING)
            self.filename = os.path.basename(self.base_path)
        else:
            abs_path = os.path.join(self.base_path, self.relative_path)
            self._abs_path_encoded = abs_path.encode(FILESYSTEM_ENCODING)
            self.filename = os.path.basename(self.relative_path)

        # setup file related data from os: _exists, _is_dir, _is_file, time_* and size
        if exists_and_is_dir:
            self._exists = True
            self._is_dir = True
            self._is_file = False
            self.time_modified = None
            self.time_accessed = None
            self.time_changed = None
            self.size = None
        elif exists_and_is_file:
            self._exists = True
            self._is_dir = False
            self._is_file = True
            self.time_modified = None
            self.time_accessed = None
            self.time_changed = None
            self.size = None
        else:
            try:
                (mode, ino, dev, nlink, uid,
                 gid, size, st_atime, st_mtime,
                 st_ctime) = os.stat(self._abs_path_encoded)
                times = [st_atime, st_mtime, st_ctime]
                # If no exception was raised, exists
                self._exists = True
                self._is_dir = stat.S_ISDIR(mode)
                self._is_file = stat.S_ISREG(mode)

                datetimes = []
                for ts in times:
                    dt = datetime.fromtimestamp(ts, tz=datefmt.localtz).astimezone(datefmt.utc)
                    datetimes.append(dt)

                self.time_accessed = datetimes[0]
                self.time_modified = datetimes[1]
                self.time_changed = datetimes[2]
                self.size = size
            except OSError:
                self._exists = False
                self._is_dir = None
                self._is_file = None
        self._hash = None

    def is_file(self):
        if self._is_file is not None:
            return self._is_file
        self._is_file = os.path.isfile(self._abs_path_encoded)
        return self._is_file

    def is_dir(self):
        if self._is_dir is not None:
            return self._is_dir
        self._is_dir = os.path.isdir(self._abs_path_encoded)
        return self._is_dir

    def exists(self):
        if self._exists is not None:
            return self._exists
        self._exists = os.path.exists(self._abs_path_encoded)
        return self._exists

    def get_dirs_and_files(self):
        if self._dirs_and_files is None:
            self._dirs_and_files = self._get_filesystem_dirs_and_files()
        return self._dirs_and_files

    def calculate_hash(self):
        if self._hash is not None:
            return self._hash
        file = open(self._abs_path_encoded, "rb")
        block_size = 2048
        hasher = sha256()
        block = file.read(block_size)
        while block:
            hasher.update(block)
            block = file.read(block_size)
        file.close()
        self._hash = hasher.hexdigest()
        return self._hash

    def get_parent_dir(self):
        """
        .. NOTE::

            os.stat related info is NOT populated by default, otherwise
            this method returns fully populated nodes.

        """
        if self._parent_dir is not None:
            return self._parent_dir
        if self.relative_path == '.':
            raise InvalidOperationError(_("Cannot get parent dir for Home directory"))

        parent_node = self.node()
        if self.exists():
            parent_node.populate_file_data(os.path.join(self.relative_path, '..'),
                exists_and_is_dir=True)
        else:
            parent_node.populate_file_data(os.path.join(self.relative_path, '..'))

        self._parent_dir = parent_node

        return self._parent_dir

    def chmod(self):
        """
        Changes the permissions for the file or dir.
        For directory: read, write, execute for user and group, none to others.
        For file: read, write for user and group, none to others.
        """
        if self.is_dir():
            os.chmod(self._abs_path_encoded,
                stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                stat.S_IRGRP | stat.S_IXGRP)
        elif self.is_file():
            # Read, write for user, read for others
            os.chmod(self._abs_path_encoded,
                stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP)

    def remove_check(self, data):
        """
        Checks whether the file or dir can be removed.
        Param data is a dict which can have bool value force_remove, and sanity_check.
        If sanity_check is False, does not check whether the file exist.
        If force_remove is True, removes a dir even if it is not empty.

        :param data: A dict to be shared with *_check, *_do, *_post_process method calls
        :raises: TracError or HTTPNotFound
        """
        conf.log.debug("trying to delete %s" % self)
        force_remove = data.get('force_remove', False)
        sanity_check = data.setdefault('sanity_check', True)
        if sanity_check and not self.exists():
            conf.log.debug("file %s/%s does not exist", self.base_path, self.relative_path)
            raise HTTPNotFound('Specified file name does not exist')

        if self.is_dir():
            if not self.is_empty_dir() and not force_remove:
                conf.log.debug("%s is a non-empty directory, can't delete", self)
                raise TracError(_("Folder was not empty and not forced remove."))
        if self.relative_path == '.':
            raise TracError(_("Cannot delete Home directory"))
        elif sanity_check and not self.exists():
            raise TracError("The file or folder to be deleted was not found")

    def remove_do(self, data):
        """
        Actually removes the file or dir.

        :param data: A dict to be shared with *_check, *_do, *_post_process method calls
        """
        if self.is_dir():
            try:
                if self.is_empty_dir():
                    os.rmdir(self._abs_path_encoded)
                else:
                    shutil.rmtree(self._abs_path_encoded)
            except Exception:
                conf.log.exception("Failed to delete directory %s/%s",
                    self.base_path, self.relative_path)
                raise TracError('Failed to delete the directory')
        elif self.is_file():
            try:
                os.remove(self._abs_path_encoded)
            except Exception:
                conf.log.exception("Failed to delete file %s/%s",
                    self.base_path, self.relative_path)
                raise TracError('Failed to delete the file')

    def remove_post_process(self, data):
        """
        Does post-processing for removing the file, like updating the node's attributes.

        :param data: A dict to be shared with *_check, *_do, *_post_process method calls
        """
        self._exists = False
        self._is_dir = None
        self._is_file = None
        # Remove cache
        self._is_empty_dir = None
        self._parent_dir = None
        self._dirs_and_files = None
        self._hash = None

    def remove(self, data=None):
        """
        :param data: A dict to be shared with *_check, *_do, *_post_process method calls
        """
        if data is None:
            data = {}
        self.remove_check(data)
        self.remove_do(data)
        self.remove_post_process(data)

    def is_empty_dir(self):
        """
        :return: False, if this is an empty dir, otherwise True
        :raises: OSError when node is not a dir (should be checked before)
        """
        if self._is_empty_dir is not None:
            return self._is_empty_dir
        self._is_empty_dir = len(os.listdir(self._abs_path_encoded)) == 0
        return self._is_empty_dir

    def move(self, to_relative_path, data=None):
        """
        Checks whether the file or dir can be removed.
        Param data is a dict which can have bool value force_remove, and sanity_check.
        If destination_is_dir is True, the actual relative path is considered to be
        to_relative_path appended with the filename of this file.
        If sanity_check is False, does not check whether the parent dir exist, etc.
        Is is_move is False, does copy instead of moving.

        :param data: A dict to be shared with *_check, *_do, *_post_process method calls
        :raises: TracError
        """
        if data is None:
            data = {}
        node = self.move_get_destination(to_relative_path, data)
        self.move_check(node, data)
        self.move_do(node, data)
        return self.move_post_process(node, data)

    def move_get_destination(self, to_relative_path, data):
        """
        Gets destination node for move (or copy) operation.
        If to_relative_path starts with '/', it is assumed to be relative to the base_path,
        otherwise, it is relative to the current node.
        """
        try:
            # TODO: Not Windows compatible
            if data.get('destination_is_dir', False):
                to_relative_path = os.path.join(to_relative_path, self.filename)
            if to_relative_path.startswith(os.sep):
                relative_path = filesystem.safe_path(self.base_path, to_relative_path.lstrip(os.sep))
            else:
                relative_path = os.path.join(self.relative_path, '..', to_relative_path)
            node = self.node()
            node.populate_file_data(relative_path)
            return node
        except filesystem.InvalidFilenameOrPath:
            raise TracError(_('The target filename is invalid'))
        except TracError:
            raise

    def move_check(self, node, data):
        """
        Validates destination node:
        - self exists.
        - the source is not root directory
        - the destination will not be root directory either
        - destination node must not exist

        :param data: A dict to be shared with *_check, *_do, *_post_process method calls
        :raises: TracError
        """
        overwrite = data.setdefault('overwrite', False)
        sanity_check = data.setdefault('sanity_check', True)
        is_move = data.setdefault('is_move', True)
        if self.relative_path == '.':
            if is_move:
                raise TracError(_('Cannot move Home directory'))
            else:
                raise TracError(_('Cannot copy Home directory'))
        if node.relative_path == '.':
            raise TracError(_('Destination is the Home directory'))
        if node.exists() and not overwrite:
            raise TracError(_('Destination file or folder already exists'))
        if sanity_check:
            parent_dir = node.get_parent_dir()
            if not self.exists():
                raise TracError(_('Cannot move non-existing file or folder'))
            if not parent_dir.exists():
                raise TracError(_('Path to destination does not exist'))
            if not parent_dir.is_dir():
                raise TracError(_('Destination parent dir is a file'))
            if node.relative_path.startswith(self.relative_path+'/'):
                raise TracError(_('Cannot move folder inside its sub folder'))

    def move_do(self, to_node, data):
        """
        Actually do the moving.

        :param data: A dict to be shared with *_check, *_do, *_post_process method calls
        :raises: TracError
        """
        try:
            if data['is_move']:
                shutil.move(self._abs_path_encoded, to_node._abs_path_encoded)
            else:
                if self.is_dir():
                    shutil.copytree(self._abs_path_encoded, to_node._abs_path_encoded)
                elif self.is_file():
                    shutil.copy2(self._abs_path_encoded, to_node._abs_path_encoded)
        except IOError as e:
            raise TracError(_("Error when moving file"))

    def move_post_process(self, to_node, data):
        """
        Do post-processing for the move operation, like update attributes.

        :param data: A dict to be shared with *_check, *_do, *_post_process method calls
        :raises: TracError
        """
        if data['is_move']:
            # The original node was deleted
            self._exists = False
            self._is_dir = None
            self._is_file = None
            # Remove cache
            self._is_empty_dir = None
            self._parent_dir = None
            self._dirs_and_files = None
            self._hash = None
        # Must be done without any shortcuts, to get the proper os.stat values
        to_node.populate_file_data(to_node.relative_path)
        return to_node

    def _get_filesystem_dirs_and_files(self):
        if not self.is_dir():
            raise InvalidOperationError("Node %s is not directory! '%s'" % (self, self._is_dir))
        _dirs = []
        _files = []
        try:
            for filename_encoded in os.listdir(self._abs_path_encoded):
                # filename_encoded is in FILESYSTEM_ENCODING
                filename = filename_encoded.decode(FILESYSTEM_ENCODING)
                rel_path = os.path.join(self.relative_path, filename)
                node = self.node()
                node.populate_file_data(rel_path)
                node._parent_dir = weakref.ref(self)
                if node.is_dir():
                    _dirs.append(node)
                elif node.is_file():
                    _files.append(node)
        except OSError:
            conf.log.exception("listing dirs and files failed in %s ", self)
        if self._is_empty_dir is None:
            self._is_empty_dir = (len(_dirs) + len(_files)) == 0
        return _dirs, _files

    def create_dir(self, filename, data=None):
        """
        Creates a directory inside this folder.

        :param filename: A filename of the created folder.
        :param data: A dict to be shared with *_check, *_do, *_post_process method calls
        :raises: TracError
        """
        if not data:
            data = {'type': 'dir', 'can_be_subdir': False}
        node = self.create_get_destination(filename, data)
        node.create_check(data)
        node.create_do(data)
        node.create_post_process(data)
        return node

    def create_get_destination(self, relative_path, data):
        """
        Gets the destination node for the creation.
        If relative_path starts with slash, can be any node inside base path.
        If can_be_subdir is True, allows filename to have '/' or '\' marks.

        :param data: A dict to be shared with *_check, *_do, *_post_process method calls
        :raises: TracError on error
        """
        if relative_path.startswith(os.sep):
            relative_path = filesystem.safe_path(self.base_path, relative_path.lstrip(os.sep))
        else:
            if not data.get('can_be_subdir') and ('/' in relative_path
                                                  or '\\' in relative_path):
                raise TracError(_('File or folder name cannot contain slash or backslash'))
            relative_path = os.path.join(self.relative_path, relative_path)
        node = self.node()
        node.populate_file_data(relative_path)
        return node

    def create_check(self, data):
        """
        Checks whether creation can be done. Data can contain the following keys and values:
        - If sanity_check is False, does not check whether the parent dir exist, etc.
        - Is is_move is False, does copy instead of moving.

        :param data: A dict to be shared with *_check, *_do, *_post_process method calls
        :raises: TracError on not permitted operation.
        """
        overwrite = data.setdefault('overwrite', False)
        sanity_check = data.setdefault('sanity_check', True)
        if self.relative_path == '.':
            raise TracError(_("Cannot overwrite Home directory"))
        if self.exists() and not overwrite:
                raise TracError(_('File or folder "%(filename)s" already exists',
                    filename=self.filename))
        if sanity_check:
            parent_dir = self.get_parent_dir()
            if not parent_dir.exists():
                raise TracError(_('Path to destination does not exist'))
            if not parent_dir.is_dir():
                raise TracError(_('Destination parent dir is a file'))
        data.setdefault('type', '')

    def create_do(self, data):
        """
        Actually create the file. Implemented only for a directory.

        :param data: A dict to be shared with *_check, *_do, *_post_process method calls
        :raises: TracError
        """
        if data['type'] == 'dir':
            # Read, write, execute for server, read, execute rights to groupd and others
            os.mkdir(self._abs_path_encoded,
                stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    def create_post_process(self, data):
        """
        Do post-processing for the move operation, like updating the attributes.
        If dir was created, does the exists_and_is_dir short circuit.

        :param data: A dict to be shared with *_check, *_do, *_post_process method calls
        :raises: TracError
        """
        if data['type'] == 'dir':
            self.populate_file_data(self.relative_path, exists_and_is_dir=True)
        else:
            self.populate_file_data(self.relative_path)

    def __repr__(self):
        return "<{0}:'{1}':'{2}'>".format(self.__class__.__name__, self.base_path, self.relative_path)


class MappedFileNode(FileSystemNode):
    """
    Class adding url and downloads information above the FileSystemNode.

    For creating new node when you have already one MappedFileNode instance,
    use the static methods from_path, from_download_entry, or from_request_path_info.

    If you don't have one, first create MappedFileNode,
    normalize it via self.normalize(), and then populate file related data with
    populate_file_data(relative_path) and populate_url_data().
    """
    def __init__(self, project_id, base_path, base_url, downloads_dir):
        super(MappedFileNode, self).__init__(base_path)
        self.project_id = project_id
        self.base_url = base_url
        self.downloads_dir = downloads_dir

        # Bool corresponding whether the file is download directory or inside it.
        self._is_download = None
        # ProjectDownloadEntry (if is_download) or None
        self._download = None

    def node(self):
        """
        :return: un-populated instance of self.__class__ (MappedFileNode in this case).
        """
        return MappedFileNode(self.project_id, self.base_path, self.base_url, self.downloads_dir)

    def normalize(self):
        super(MappedFileNode, self).normalize()
        self.base_url = normalized_base_url(self.base_url)

    def populate_url_data(self, project_download_entry=None):
        """
        Populates the url-related data, that is, is_download and download.

        project_download_entry is False if this file entry is known to not have
        project download entry.
        :param project_download_entry: If known beforehand, can be given
        """
        self._is_download = None
        if self.is_download():
            self._download = project_download_entry
            if self._download is None:
                download_path = ProjectDownloadEntry.get_download_path(self.downloads_dir,
                    self.relative_path)
                self._download = ProjectDownloadEntry.from_download_path(self.project_id,
                    download_path)
            if not self._download:
                self._download = self._not_existing_download_entry()
            conf.log.debug("Resulting _download: %s, %s" % (self, self._download))

    def _not_existing_download_entry(self):
        download_path = ProjectDownloadEntry.get_download_path(self.downloads_dir,
            self.relative_path)
        return ProjectDownloadEntry.not_existing(self.project_id, download_path)

    def is_download(self):
        """
        Checks whether or not the node is downloads dir or path inside it.
        .. Note::

            The downloads_dir itself is considered to be download.

        """
        if self._is_download is not None:
            return self._is_download
        if not self.downloads_dir:
            self._is_download = False
        elif self.downloads_dir == '.':
            self._is_download = True
        else:
            len_path = len(self.relative_path)
            len_dir = len(self.downloads_dir)
            if len_path < len_dir:
                self._is_download = False
            elif (self.relative_path.startswith(self.downloads_dir)
                and (len_path == len_dir or self.relative_path[len_dir] == os.sep)):
                self._is_download = True
            else:
                self._is_download = False

        return self._is_download

    def download(self):
        """
        :returns: ProjectDownloadEntry
        """
        if not self.is_download():
            raise InvalidOperationError("tried to get download for a non-download file")
        return self._download

    def get_url(self, req):
        return req.href(self.base_url, self.relative_path)

    @staticmethod
    def from_request_path_info(path_info, node_factory):
        """
        :param node_factory: MappedFileNode
        :returns: MappedFileNode
        :raises: InvalidFilenameOrPath if path_info is not inside base_url.
        """
        if path_info == node_factory.base_url:
            relative_path = '.'
        elif path_info.startswith(node_factory.base_url + '/'):
            relative_path = path_info[len(node_factory.base_url) + 1:]
            if not relative_path:
                relative_path = '.'
        else:
            raise InvalidFilenameOrPath(_("Cannot determine file or folder from request"))
        node = node_factory.node()
        node.populate_file_data(relative_path)
        node.populate_url_data()
        conf.log.debug('get node from_request -> node %s', node)
        return node

    @staticmethod
    def from_path(path, node_factory, assume_relative_path=False):
        """
        :param node_factory: MappedFileNode
        :param assume_relative_path: whether or not to assume relative path.
        :returns: MappedFileNode
        """
        node = FileSystemNode.from_path(path, node_factory, assume_relative_path)
        node.populate_url_data()
        return node

    @staticmethod
    def from_download_path(path, node_factory, assume_relative_path=False):
        """
        :param node_factory: MappedFileNode
        :param assume_relative_path: whether or not to assume relative path.
        :returns: MappedFileNode
        """
        path = filesystem.safe_path(node_factory.downloads_dir, path)
        return MappedFileNode.from_path(path, node_factory, assume_relative_path)

    @staticmethod
    def from_download_entry(download_entry, node_factory, exists_and_is_file=True):
        relative_path = filesystem.safe_path(node_factory.downloads_dir,
            download_entry.download_path)
        node = node_factory.node()
        node.populate_file_data(relative_path, exists_and_is_file=exists_and_is_file)
        if exists_and_is_file:
            node.time_modified = download_entry.changed
            node.time_accessed = download_entry.changed
            node.time_changed = download_entry.changed
            node.size = download_entry.size
        node.populate_url_data(project_download_entry=download_entry)
        return node

    def create_file_from_request(self, req, upload, uploader_id, timeline_notifier,
                                 is_multiple_upload=False):
        """
        :returns: MappedFileNode or None
        """

        if not isinstance(upload, FieldStorage):
            raise TracError(_("No file was uploaded."))
        if not upload.filename:
            raise TracError(_("Can't find filename"))

        upload_filename = upload.filename.replace('\\', '/').replace(':', '/')
        upload_filename = os.path.basename(upload_filename)
        if not upload_filename:
            raise TracError(_("Can't find filename"))

        relative_path = unicode(upload_filename)
        data = {
            'uploader_id': uploader_id,
            'req': req,
            'perm': req.perm,
            'update_also': not is_multiple_upload,
            'timeline_notifier': timeline_notifier,
            'username': req.authname,
        }

        node = self.create_get_destination(relative_path, data)
        node.create_check(data)

        # Open a file
        fd = os.open(node._abs_path_encoded, os.O_RDWR | os.O_CREAT)
        # Now get a file object for the above file.
        target_file = os.fdopen(fd, "w+")
        try:
            shutil.copyfileobj(upload.file, target_file)
        except Exception:
            self.log.exception("Failed to save the file: %s" % node)
            raise TracError(_("Failed to save the file"))
        finally:
            target_file.close()

        # Create meta data
        node.create_post_process(data)
        return node

    def create_check(self, data):
        """
        Checks whether creation can be done.
        The data dict must contain keys uploader_id and timeline_notifier,
        and can contain keys update_also, and req.

        :param data: A dict to be shared with *_check, *_do, *_post_process method calls
        :return:
        """
        self.require_write_perm(data['perm'])
        super(MappedFileNode, self).create_check(data)
        if 'uploader_id' not in data:
            raise InvalidOperationError("Did not get uploader id")
        if self.relative_path == self.downloads_dir:
            raise TracError(_('Download folder cannot be created or overwritten'))
        data.setdefault('req', None)
        data.setdefault('update_also', False)
        data['orig_target_node'] = self
        if data['overwrite'] and self.exists() and self.is_download():
            self.get_dirs_and_files_recursively()

    def create_post_process(self, data):
        """
        Do post-processing for the create operation, like updating the attributes and
        logging the operation.

        :param data: A dict to be shared with *_check, *_do, *_post_process method calls
        :raises: TracError
        """
        if data['overwrite'] and self.exists() and self.is_download():
            self.remove_download_entries_recursively()
        super(MappedFileNode, self).create_post_process(data)
        # Url data was not changed

        if self.is_download():
            if self.is_file():
                uploader_id = data['uploader_id']
                req = data['req']
                update_also = data['update_also']
                self.create_new_download_version(uploader_id, req=req, update_also=update_also)
            elif self.is_dir() and self.download().is_available():
                self.download().delete()

        try:
            self.chmod()
        except Exception as e:
            self.log.exception("Changing mode failed for file or folder %s", self)
        if data['orig_target_node'] == self:
            data['timeline_notifier'].node_created(data['username'], self)

    def create_dir_from_request(self, req, uploader_id, timeline_notifier):
        """
        Returns the created directory or none, if no folder_filename was given.
        """
        new_dir_filename = req.args.get('folder_filename')
        if not new_dir_filename:
            return None
        data = {
            'req': req,
            'perm': req.perm,
            'type': 'dir',
            'uploader_id': uploader_id,
            'timeline_notifier': timeline_notifier,
            'username': req.authname,
        }
        return self.create_dir(new_dir_filename, data=data)

    def create_get_destination(self, filename, data):
        node = super(MappedFileNode, self).create_get_destination(filename, data)
        node.populate_url_data()
        return node

    def update_metadata_from_request(self, req, uploader_id):
        """
        Updates the metadata (download information) for the download.
        If download information is not available (or is deleted and the deleted version
        is not related to the current file), new download version is created.
        Else, if the same file is in question, sets the description, platform and featured
        flag as in request.

        .. Note::

            Deleted download can become an existing download again.

        """
        self.require_write_perm(req.perm)
        if self.is_dir():
            raise TracError(_("Cannot update directories"))
        elif self.is_file() and self.is_download():
            download = self.download()
            version = safe_int(req.args.get('version', '0'))
            if (not download.entry_exists() or (download.is_deleted()
                                                and not download.is_same_file(self))):
                if not version:
                    try:
                        self.create_new_download_version(uploader_id, req=req, update_also=True)
                    except TracError:
                        add_warning(req, _('Failed when saving download information'))
                        return
                else:
                    raise TracError(_("Version did not match. "
                                      "Check that the download information haven't been deleted."))
            else:
                # version == 0 corresponds to deleted download
                if version != 0 and version != download.version:
                    conf.log.warning("VERSION == %s, version == %s"%(version, download.version))
                    raise TracError(_("Version did not match. "
                                      "Check that the file hasn't been changed."))
                if version == 0 and not download.is_deleted():
                    conf.log.warning("VERSION == %s, deleted == %s"%(version, download.is_deleted()))
                    raise TracError(_("Version did not match. "
                                  "Check that the file hasn't been changed."))
                if version != 0 and not download.is_same_file(self):
                    download.delete()
                    raise TracError(_("The file has been replaced with another file."))
                download.update_user_values(req)
                if not download.description or not download.platform:
                    add_warning(req, _("Provide the download information for %(filename)s",
                        filename=self.filename))

                download.update()
        else:
            raise TracError(_("File does not exist"))

    def create_new_download_version(self, uploader_id, req=None, other_node=None,
                                     update_also=False, move_download=False):
        """
        :param other_node: MappedFileNode, which was copied/moved to become this.
        :param update_also: Update also from req
        :param move_download: If is True, delete completely other_node download.
        :return:
        """
        download = self.download()
        other_download = other_node and other_node.download() or None
        if download.is_available():
            if not download.delete():
                raise TracError(_("Could not delete old download information version"))

        # Sanity check
        if not other_download or not other_download.is_available():
            other_download = None
            move_download = False

        # Setup user inputted meta information, like description
        if update_also and req:
            download.update_user_values(req)
        elif other_download:
            download.clone_user_values(other_download)
        else:
            download.reset_user_values()

        # Setup automatic meta information, like hash
        if other_download:
            hash = None
            if other_download.is_available():
                hash = other_download.hash
            uploader_id = other_download.uploader_id or uploader_id
            created = other_download.created or None
            if move_download:
                download.count = other_download.count
                other_download.count = 0
            download.populate_download(self, uploader_id, hash=hash, created=created)
        else:
            download.populate_download(self, uploader_id)

        try:
            download.create_new_version()
            if move_download:
                other_download.delete_completely()
        except TracError:
            raise TracError(_("Could not create download entry"))

        if req and (not download.description or not download.platform):
            add_warning(req, _("File %(filename)s needs download information.",
                filename=self.filename))

    def get_dirs_and_files(self):
        """
        .. Note::

            The returned nodes where entry_exists() returns False might be only deleted
            (there has been an optimization used).

        :return: (dirs, files) tuple.
        """
        if self._dirs_and_files is not None:
            return self._dirs_and_files
            # If not in downloads dir, set _is_download to False for all dirs and files
        dirs, files = self._get_filesystem_dirs_and_files()
        if self.relative_path == '.':
            if self.downloads_dir:
                for dir in dirs:
                    # Populate url data for download dir
                    if dir.relative_path == self.downloads_dir:
                        dir.populate_url_data()
            self._dirs_and_files = dirs, files
        elif not self.is_download():
            # No need to populate file downloads dir
            # Currently, dir nodes don't have download entries
            self._dirs_and_files = dirs, files
        else:
            # The hard case
            self._dirs_and_files = self._merge_db_dirs_and_files(dirs, files)
        return self._dirs_and_files

    def _merge_db_dirs_and_files(self, fs_dirs, fs_files):
        """
        Attaches ProjectDownloadEntry items to each file, and deletes those files which exist
        in non-existing subfolders or should exist in current directory but does not.
        """
        project_download_entries = ProjectDownloadEntry.downloads_in_folder(
            self.project_id, self.download().download_path)

        this_path = ''
        if self._download.download_path != '.':
            this_path = self._download.download_path + '/'

        file_node_per_filename = {}
        dir_node_per_filename = {}
        for file_node in fs_files:
            file_node_per_filename[file_node.filename] = file_node
        for dir_node in fs_dirs:
            dir_node_per_filename[dir_node.filename] = dir_node

        # Currently, dir nodes don't have download entries

        for download_entry in project_download_entries:
            path_below_this = download_entry.download_path[len(this_path):]
            # path_below_this is the downloads file name
            try:
                # del this key -> Mark this item as handled
                file_node_per_filename[path_below_this].populate_url_data(
                    project_download_entry=download_entry)
                del file_node_per_filename[path_below_this]
            except KeyError:
                # download entry not found from the folder
                # -> set entry state deleted
                download_entry.delete()

        for file_node in file_node_per_filename.values():
            file_node.populate_url_data(file_node._not_existing_download_entry())
        for dir_node in fs_dirs:
            dir_node.populate_url_data(dir_node._not_existing_download_entry())

        return fs_dirs, fs_files

    def show_file(self, req, mimeview, timeline_notifier):
        data = {
            'timeline_notifier': timeline_notifier,
            'perm': req.perm,
            'username': req.authname,
        }
        self.show_check(data)
        if not self.exists():
            if self.is_download():
                if self.download().is_available():
                    self.download().delete()
            if self.is_download() and self.download().is_deleted():
                add_warning(req, _("The download has been removed."))
            else:
                add_warning(req, _("The file you tried to download does not exist."))
            raise InvalidOperationError("File does not exist")
        elif not self.is_file():
            add_warning(req, _("The file you tried to download is not a file."))
            raise InvalidOperationError("File is not file")
        elif self.is_download():
            not_existing_download = True
            if not self.download().is_available():
                add_warning(req, _("Cannot show file: "
                    "The file does not have any download information available. "))
            elif not self.download().is_same_file(self):
                add_warning(req, _("Cannot show file: "
                    "The file does not have correct download information available."))
                self.download().delete()
            else:
                not_existing_download = False
            if not_existing_download:
                conf.log.error("Error with download entry when showing MappedFileNode: %s"%self)
                # This should not happen, since the files should always have download information.
                raise InvalidOperationError("The operation was invalid")

        fd = open(self._abs_path_encoded, "rb")
        success = False

        try:
            # MIME type detection
            str_data = fd.read(1000)
            fd.seek(0)

            mime_type = mimeview.get_mimetype(self.filename, str_data)

            req.send_header('Content-Disposition', 'attachment')
            if self.filename.endswith('.txt'):
                mime_type = 'text/plain'
            elif not mime_type:
                mime_type = 'application/octet-stream'

            if 'charset=' not in mime_type:
                charset = mimeview.get_charset(str_data, mime_type)
                mime_type = mime_type + '; charset=' + charset

            try:
                req.send_file(self._abs_path_encoded, mime_type)
            except RequestDone:
                success = True
                self.show_post_process(data)
                raise
        finally:
            fd.close()
        # This function should always return False
        return success

    def show_check(self, data):
        self.require_read_perm(data['perm'])

    def show_post_process(self, data):
        if self.is_file():
            if self.is_download() and self.download().is_available():
                self.download().file_downloaded()
            data['timeline_notifier'].node_downloaded(data['username'], self)

    def move_by_request(self, req, uploader_id, timeline_notifier, destination_is_dir=False,
                        update_also=False):
        """
        Takes 'to_relative_path' param from request: '/' corresponds to the base_path

        .. NOTE::

            Checks also permissions
        """
        to_relative_path = os.path.normpath(req.args.get('to_relative_path',''))
        data = {
            'req': req,
            'uploader_id': uploader_id,
            'perm': req.perm,
            'update_also': update_also,
            'destination_is_dir': destination_is_dir,
            'timeline_notifier': timeline_notifier,
            'username': req.authname,
        }
        return self.move(to_relative_path, data=data)

    def move_get_destination(self, to_relative_path, data):
        node = super(MappedFileNode, self).move_get_destination(to_relative_path, data)
        node.populate_url_data()
        return node

    def move_check(self, node, data):
        """
        The data can contain is_move, context ('web' or 'webdav'), sanity_check, overwrite
        Must contain: uploader_id, timeline_notifier, perm

        :param data: A dict to be shared with *_check, *_do, *_post_process method calls
        :raises: TracError
        """
        # Check permissions:
        # Since we also delete the file, we need write perm to source as well and
        # write to destination.
        # Checks also, that the destination doesn't exist yet
        is_move = data.setdefault('is_move', True)
        if is_move:
            self.require_write_perm(data['perm'])
        else:
            self.require_read_perm(data['perm'])
        node.require_write_perm(data['perm'])
        super(MappedFileNode, self).move_check(node, data)

        if is_move and self.relative_path == self.downloads_dir:
            raise TracError(_('Download folder cannot be moved'))
        if node.relative_path == self.downloads_dir:
            raise TracError(_('Cannot replace download folder'))
        context = data.setdefault('context', 'web')
        if self.is_file() and context == 'web':
            extension1 = os.path.splitext(self.filename)
            extension2 = os.path.splitext(node.filename)
            if (extension1[0] or extension2[0]) and extension1[1] != extension2[1]:
                raise TracError(_('Cannot change file extension from %(before)s to %(after)s',
                    before = extension1, after = extension2))

        if data['overwrite'] and node.exists():
            # Prepare for removing recursively also the contents of the existing file
            node.get_dirs_and_files_recursively()

        data['orig_target_node'] = self
        if self.is_dir() and (self.is_download() or node.is_download()):
            # Since root dir cannot be moved, this check is enough
            self.get_dirs_and_files_recursively()

        if 'uploader_id' not in data:
            raise InvalidOperationError("Did not get uploader id")
        data.setdefault('req', None)
        data.setdefault('update_also', False)

    def move_post_process(self, to_node, data):
        """
        Called after successful move or copy operation

        If data['is_move'], is move, otherwise, doesn't affect self.
        :param to_node: for dirs, the original to node, otherwise, the destination node.
        :param data: A dict to be shared with *_check, *_do, *_post_process method calls
        """
        # the download data was not changed, thus no need to populate_url_data
        is_move = data['is_move']
        if data['orig_target_node'] is self:
            if data['overwrite'] and to_node.exists():
                to_node.remove_download_entries_recursively()
            if is_move:
                data['timeline_notifier'].node_moved(data['username'], self, to_node)
            else:
                data['timeline_notifier'].node_copied(data['username'], self, to_node)

        if self.is_file():
            super(MappedFileNode, self).move_post_process(to_node, data)
            if not self.is_download() and to_node.is_download():
                conf.log.debug("files: moving/copying file %s => to be download %s", self,
                    to_node.download())
                # create new entry, delete old if exists
                to_node.create_new_download_version(data['uploader_id'], req=data['req'],
                    update_also=data['update_also'])
            elif self.is_download():
                if to_node.is_download():
                    conf.log.debug("files: moving/copying download %s => to be download %s",
                        self.download(), to_node.download())
                    # Copy download information from another download entry to new download entry
                    to_node.create_new_download_version(data['uploader_id'], req=data['req'],
                        other_node=self, update_also=data['update_also'],
                        move_download=is_move)
                else:
                    conf.log.debug("files: moving/copying download %s => to be file %s",
                        self.download(), to_node)
        elif self.is_dir() and (self.is_download() or to_node.is_download()):
            moved_dirs, moved_files = self.get_dirs_and_files()
            super(MappedFileNode, self).move_post_process(to_node, data)
            if self.is_download():
                node = self.node()
                for moved_file in moved_files:
                    # Create the destination with speed up
                    node.populate_file_data(to_node.relative_path
                                            + moved_file.relative_path[len(self.relative_path):],
                        exists_and_is_file=True)
                    node.populate_url_data()
                    moved_file.move_post_process(node, data)
                for moved_dir in moved_dirs:
                    node.populate_file_data(to_node.relative_path
                                            + moved_dir.relative_path[len(self.relative_path):],
                        exists_and_is_dir=True)
                    node.populate_url_data()
                    moved_dir.move_post_process(node, data)
                # Always delete download entries for dirs
                if to_node.download().entry_exists():
                    to_node.download().delete()
        # Only when every sub node download information is moved, do this:
        if data['orig_target_node'] is self and is_move:
            self.remove_download_entries_recursively()
        return to_node

    def remove_by_request(self, req, timeline_notifier):
        data = {
            'force_remove': req.args.get('force_remove', '') == 'yes',
            'perm': req.perm,
            'timeline_notifier': timeline_notifier,
            'username': req.authname,
        }
        return self.remove(data)

    def remove_check(self, data):
        """
        Checks whether the removeing can be done.

        :param data: A dict to be shared with *_check, *_do, *_post_process method calls
        :return:
        """
        self.require_write_perm(data['perm'])
        super(MappedFileNode, self).remove_check(data)
        if self.is_dir() and self.relative_path == self.downloads_dir:
            raise TracError(_("Cannot delete downloads dir"))
        if self.is_download() and self.download().is_featured():
            raise TracError(_("Cannot delete featured download"))
        data.setdefault('orig_target_dir', self)
        self.get_dirs_and_files_recursively()

    def remove_post_process(self, data):
        """
        Does post-processing for the remove operation, like removing the attributes
        and removing the download information from db.

        :param data: A dict to be shared with *_check, *_do, *_post_process method calls
        """
        if data['orig_target_dir'] is self:
            data['timeline_notifier'].node_removed(data['username'], self)
        self.remove_download_entries_recursively()
        super(MappedFileNode, self).remove_post_process(data)

    def get_dirs_and_files_recursively(self):
        """
        Makes sure that the self._dirs_and_files is populated recursively
        for all sub-folders also.
        """
        if self.is_dir():
            dirs, files = self.get_dirs_and_files()
            for dir in dirs:
                dir.get_dirs_and_files_recursively()

    def remove_download_entries_recursively(self):
        """
        Removes meta info for the file or dir (recursively).
        Called after actually deleting the file or folder,
        and before populating the data to self.
        Populates the download entry data, but not other.
        """
        if not self.is_download():
            return
        if self.download().is_available():
            self.download().delete()
        if self.is_dir():
            # If orig_dir exists, the removed dir was a download dir
            dirs, files = self.get_dirs_and_files()
            for file in files:
                if file.download().is_available():
                    file.download().delete()
            for dir in dirs:
                dir.remove_download_entries_recursively()

    def get_parent_dir(self):
        if self._parent_dir is not None:
            return self._parent_dir
        super(MappedFileNode, self).get_parent_dir()
        self._parent_dir.populate_url_data()
        return self._parent_dir

    def require_write_perm(self, perm):
        if self.is_download():
            perm.require('FILES_DOWNLOADS_ADMIN')
        else:
            perm.require('FILES_ADMIN')

    def require_read_perm(self, perm):
        if self.is_download():
            perm.require('FILES_DOWNLOADS_VIEW')
        else:
            perm.require('FILES_VIEW')

    def get_div_class(self):
        """
        Gets a class for div element representing the icon of the file or directory.
        """
        css_class = ''
        if self.is_dir():
            if self.is_download():
                css_class = 'icon_downloads'
            else:
                css_class = 'icon_folder'
        else:
            css_class = get_div_class(self.filename)
            if self.is_download():
                if self.download().is_featured():
                    css_class += ' icon_featured'
                if not self.download().is_available():
                    css_class += ' icon_error'
                elif not self.download().description or not self.download().platform:
                    css_class += ' icon_missing'

        return css_class

    def get_href(self, req, **kwargs):
        if self.relative_path == '.':
            return req.href.files(**kwargs)
        else:
            return req.href.files(self.relative_path, **kwargs)

def get_div_class(filename):
    """
    Returns div class corresponding filename. This is also used for download entries.
    Supported file types: pdf, txt, deb, rpm, xml, swf, binary, archive, docs,
    spread, pres, images, audio, video
    :param filename:
    :return: string 'icon_file extension_image' for filename 'temp.jpg' see supported file types
    """
    known_extensions = {'pdf': 'pdf', 'txt': 'txt', 'deb': 'deb', 'rpm': 'rpm',
    'xml': 'xml', 'swf': 'swf', 'apk': 'binary', 'exe': 'binary',
    'jar': 'binary', 'jad': 'binary', 'war': 'binary', 'sis': 'binary',
    'sisx': 'binary', 'zip': 'archive', 'rar': 'archive', 'arj': 'archive',
    'lhz': 'archive', 'bz2': 'archive', 'gz': 'archive', 'tgz': 'archive',
    'tb2': 'archive', '7z': 'archive', 'kgb': 'archive', 'ace': 'archive',
    'egg': 'archive', 'ott': 'docs', 'doc': 'docs', 'docx': 'docs',
    'odt': 'docs', 'rtf': 'docs', 'abw': 'docs', 'sxw': 'docs', 'xls': 'spread',
    'xlsx': 'spread', 'ods': 'spread', 'gnumeric': 'spread', 'ppt': 'pres',
    'pptx': 'pres', 'odp': 'pres', 'wav': 'audio', 'mp3': 'audio', 'wma': 'audio',
    'ogg': 'audio', 'flac': 'audio', 'mid': 'audio', 'ac3': 'audio',
    'avi': 'video', 'mp4': 'video', 'mov': 'video', 'flv': 'video',
    'mkv': 'video', 'wmv': 'video', 'ogm': 'video', 'xvid': 'video',
    'divx': 'video', 'jpg': 'image', 'jpeg': 'image', 'gif': 'image', 
    'bmp': 'image', 'png': 'image', 'tiff': 'image', 'psd': 'image', 'xcf': 'image'}
    file_ext = filename.split(".")
    file_extension = file_ext[-1].lower()
    try: 
        ext = known_extensions[file_extension]
        css_class = 'icon_file extension_' + ext
    except:
        css_class = 'icon_file'
    return css_class


class InvalidOperationError(Exception):
    """
    Raised when method is called inappropriately.
      For example, when get_dirs_and_files is called for non-dir node.
    """
    pass


class ProjectDownloadEntry(object):
    """
    Class representing one project download entry with a constant url.
    Also few static methods for querying download entries are provided,
    which are used to fetch ProjectDownloadEntries.
    """

    STATUS_NOT_EXISTS = 1
    # Currently, only files are stored in DB
    # STATUS_DIR = 2
    STATUS_FILE = 3
    STATUS_FEATURED = 4
    STATUS_DELETED = 5
    STATUSES_AVAILABLE = [STATUS_FILE, STATUS_FEATURED]

    STATUS_TO_TEXT_MAP = {
        STATUS_NOT_EXISTS: 'Not existing',
        STATUS_FILE: 'File',
        STATUS_FEATURED: 'Featured',
        STATUS_DELETED: 'Deleted'
    }

    def __init__(self, id=None, project_id=None,
                 download_path=None, version=None, uploader_id=None, hash=None,
                 size=None, created=None, changed=None, count=None, description=None, platform=None,
                 status=None):
        """
        """
        self.id = id
        self.project_id = project_id
        self.download_path = download_path
        self.version = version
        self.uploader_id = uploader_id
        # hash == SHA256 hash
        self.hash = hash
        self.size = size
        # created == datetime time_changed of FileSystemNode
        # In DB, created == datetime.utcnow().replace(tzinfo=datefmt.utc) when db entry is created
        self.created = created
        # In DB, created == datefmt.to_utimestamp(changed)
        # When entry is deleted, 'changed' will be the deletion time.
        self.changed = changed
        self.count = count
        self.description = description
        self.platform = platform
        self.status = status
        if not self.status:
            self.status = ProjectDownloadEntry.STATUS_NOT_EXISTS

    @staticmethod
    def get_download_path(downloads_dir, relative_path):
        """
        .. NOTE::

            Can return '.' for the downloads_dir itself

        :param str relative_path: normalized relative path.
        """
        if not downloads_dir:
            conf.log.warning('get_download_path called when there is no download')
            raise InvalidOperationError('Could not get download path')

        if downloads_dir == relative_path:
            return '.'
        if downloads_dir == '.':
            return relative_path
        return relative_path[len(downloads_dir) + 1:]

    @staticmethod
    def not_existing(project_id, download_path):
        return ProjectDownloadEntry(project_id=project_id, download_path=download_path,
            status=ProjectDownloadEntry.STATUS_NOT_EXISTS, version=0)

    @staticmethod
    def from_download_path(project_id, download_path, version=None):
        """
        :param int project_id: project_id
        :param download_path: path relative to downloads dir
        :returns: ProjectDownload if download found, None otherwise
        """
        version_match = ' ORDER BY version DESC LIMIT 1 '
        if version:
            version_match = ' AND VERSION = {0} '.format(str(safe_int(version)))
        query = """
        SELECT * FROM project_download
        WHERE project_id = %s AND download_path = %s
            {0}
        """.format(version_match)
        download = None
        try:
            with admin_query() as cursor:
                cursor.execute(query, (project_id, download_path))
                row = cursor.fetchone()
                if row:
                    download = ProjectDownloadEntry.from_sql_row(row)
        except Exception:
            conf.log.exception("Exception. get_all_existing_downloads failed."
                               " Project %s, download_path %s" % (project_id, download_path))
            raise
        return download

    @staticmethod
    def get_all_download_entries(project_id, only_featured=False, only_deleted=False):
        statuses = ProjectDownloadEntry.STATUSES_AVAILABLE
        if only_featured:
            statuses = [ProjectDownloadEntry.STATUS_FEATURED]
        if only_deleted:
            statuses = [ProjectDownloadEntry.STATUS_DELETED]
        query = """
        SELECT * FROM project_download
        WHERE project_id = %s AND status IN ({0})
        ORDER BY download_path ASC
        """.format(','.join([str(status) for status in statuses]))
        download_list = []
        try:
            with admin_query() as cursor:
                cursor.execute(query, project_id)
                for row in cursor:
                    download_list.append(ProjectDownloadEntry.from_sql_row(row))
        except:
            conf.log.exception("Exception. get_all_download_entries failed. Project %s, statuses %s"
            % (project_id, statuses))
            raise
        return download_list

    @staticmethod
    def downloads_in_folder(project_id, download_folder,
                                           only_featured=False, only_deleted=False):
        statuses = ProjectDownloadEntry.STATUSES_AVAILABLE
        if only_featured:
            statuses = [ProjectDownloadEntry.STATUS_FEATURED]
        elif only_deleted:
            statuses = [ProjectDownloadEntry.STATUS_DELETED]
        if download_folder == '.':
            query = """
            SELECT *
            FROM project_download
            WHERE project_id = %s
            AND status IN ({0})
            AND LOCATE('/', download_path) = 0
            ORDER BY download_path ASC, version DESC
            """.format(
                ','.join([str(status) for status in statuses]))
            params = (project_id,)
        else:
            query = """
            SELECT *
            FROM project_download
            WHERE project_id = %s
            AND download_path LIKE CONCAT(%s, '%%')
            AND status IN ({0})
            AND LOCATE('/', download_path, LENGTH(%s) + 1) = 0
            ORDER BY download_path ASC
            """.format(
                ','.join([str(status) for status in statuses]))
            download_folder = download_folder + '/'
            params = (project_id, download_folder, download_folder)
        download_list = []
        try:
            with admin_query() as cursor:
                cursor.execute(query, params)
                for row in cursor:
                    download_list.append(ProjectDownloadEntry.from_sql_row(row))
        except:
            conf.log.exception("Exception. downloads_in_folder failed. "
                "Project %s, query %s, params %s" % (project_id, query, params))
            raise
        return download_list

    @staticmethod
    def total_download_count(project_id):
        query = """
        SELECT SUM(count) FROM project_download
        WHERE project_id = %s
        """
        download_list = []
        try:
            with admin_query() as cursor:
                cursor.execute(query, project_id)
                return cursor.fetchone()[0]
        except:
            conf.log.exception("Exception. get_all_download_entries failed. Project %s"
            % (project_id))
            raise

    @staticmethod
    def from_sql_row(row):
        # Note, that it seems that the row[2] is NOT utf-8, thus we need to decode it ourselves
        # This is because '\xc3\xa4 and u'\xe4' are not equal
        download_path = row[2]
        if not isinstance(download_path, unicode):
            download_path = download_path.decode('utf-8')
        download = ProjectDownloadEntry(id=row[0],
            project_id=row[1],
            download_path=download_path,
            version=row[3],
            uploader_id=row[4],
            hash=row[5],
            size=row[6],
            created=datefmt.from_utimestamp(row[7]),
            changed=datefmt.from_utimestamp(row[8]),
            count=row[9],
            description=row[10],
            platform=row[11],
            status=row[12])
        return download

    def populate_download(self, file_system_node,
                                     uploader_id, hash=None, created=None):
        """
        Called when a new file has been created.
        The file_system_node must be populated.

        Populates hash, size, created from file ("automatic values")
        Sets version to 0 by default.
        :param FileSystemNode file_system_node: file from which read is done
        :param int uploader_id: uploader id
        :param str hash: hash if pre-calculated
        """
        if not file_system_node.exists():
            raise InvalidOperationError("populate_download called with not existing file")

        self.count = 0
        self.uploader_id = uploader_id
        self.created = created or datetime.now(datefmt.utc)
        self.changed = file_system_node.time_changed
        self.size = file_system_node.size

        if hash is None:
            self.hash = file_system_node.calculate_hash()
        else:
            self.hash = hash

    def update_user_values(self, req):
        """
        Update user-defined values from request.
        """
        self.description = req.args.get('description', self.description)
        self.platform = req.args.get('platform', self.platform)
        self.status = ProjectDownloadEntry.STATUS_FILE
        if req.args.get('is_featured', False):
            self.status = ProjectDownloadEntry.STATUS_FEATURED

    def clone_user_values(self, entry):
        """
        Clone user-defined values from other entry.
        """
        self.description = entry.description
        self.platform = entry.platform
        self.status = entry.status

    def reset_user_values(self):
        """
        Reset user-defined values.
        """
        self.description = ''
        self.platform = ''
        self.status = ProjectDownloadEntry.STATUS_FILE

    def is_same_file(self, file_system_node, force_hash_check=False):
        """
        Check whether this file represents the file_system_node file.
        Does not take path into account.
        """

        if not file_system_node.exists():
            raise InvalidOperationError("is_same_file called with not existing file")
        if file_system_node.is_dir():
            raise InvalidOperationError("is_same_file called with dir")

        if self.size != file_system_node.size:
            return False

        if self.changed != file_system_node.time_changed or force_hash_check:
            if not self.hash:
                return False

            conf.log.info("is_same_file: calculating hash for file %s" % file_system_node)
            if self.hash != file_system_node.calculate_hash():
                return False
            try:
                conf.log.debug("Updating the changed time to DB")
                query = """
            UPDATE project_download
            SET changed = %s
            WHERE id = %s """

                with admin_transaction() as cursor:
                    cursor.execute(query, (datefmt.to_utimestamp(file_system_node.time_changed),self.id))
            except Exception:
                conf.log.exception("Exception. querying download is_same_file failed.")

        return True

    def is_deleted(self):
        return self.status == ProjectDownloadEntry.STATUS_DELETED

    def is_featured(self):
        return self.status == ProjectDownloadEntry.STATUS_FEATURED

    def is_available(self):
        return self.status in ProjectDownloadEntry.STATUSES_AVAILABLE

    def entry_exists(self):
        return self.status != ProjectDownloadEntry.STATUS_NOT_EXISTS

    def is_valid(self):
        if self.status == ProjectDownloadEntry.STATUS_NOT_EXISTS:
            return False
        if self.description and self.platform:
            return True
        return False

    def file_downloaded(self):
        query = """
        UPDATE project_download
        SET count = count + 1
        WHERE id = %s
        """
        try:
            with admin_transaction() as cursor:
                cursor.execute(query, self.id)
                self.count += 1
                return True
        except Exception:
            conf.log.exception("Exception. querying download file_downloaded failed.")
        return False

    def delete(self):
        """
        .. NOTE::

            sets self.status to deleted

        """
        query = """
        UPDATE project_download
        SET status = %s, changed = %s
        WHERE id = %s
        """
        self.changed = datetime.now(datefmt.utc)
        self.status = ProjectDownloadEntry.STATUS_DELETED
        try:
            with admin_transaction() as cursor:
                cursor.execute(query, (self.status, datefmt.to_utimestamp(self.changed), self.id))
                return True
        except Exception:
            conf.log.exception("Exception. querying download delete failed.")
        return False

    def update(self):
        """
        For updating
        """
        query = """
            UPDATE project_download
            SET description = %s, platform = %s, status = %s
            WHERE id = %s """
        try:
            with admin_transaction() as cursor:
                cursor.execute(query, (self.description, self.platform, self.status, self.id))
                return True
        except Exception:
            conf.log.exception("Exception. querying download update failed .")
        return False

    def delete_completely(self):
        """
        For updating
        """
        query = """
            DELETE FROM project_download
            WHERE id = %s """
        try:
            with admin_transaction() as cursor:
                cursor.execute(query, self.id)
                self.status = ProjectDownloadEntry.STATUS_NOT_EXISTS
                return True
        except Exception:
            conf.log.exception("Exception. querying download update failed .")
        return False

    def create_new_version(self, old_version=None):
        if old_version is not None:
            new_version = old_version + 1
        else:
            # Fails, if self.version hasn't been inited
            new_version = self.version + 1

        query = """
            INSERT INTO project_download
            (project_id, download_path, version, uploader_id,
            hash, size, created, changed, count, description,
            platform, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """
        try:
            with admin_transaction() as cursor:
                cursor.execute(query,
                    (self.project_id, self.download_path, new_version, self.uploader_id,
                     self.hash, self.size, datefmt.to_utimestamp(self.created),
                     datefmt.to_utimestamp(self.changed), self.count, self.description,
                     self.platform, self.status))
                self.id = cursor.lastrowid
                self.version = new_version
                return True
        except Exception:
            conf.log.exception("Exception. querying download create save failed .")
            raise TracError("Error while saving download information.")

    def __repr__(self):
        return "<ProjectDownloadEntry:{0}:{1}:{2} [{3}]>".format(self.project_id,
            self.download_path, self.version, ProjectDownloadEntry.STATUS_TO_TEXT_MAP[self.status])


class IFilesEventListener(Interface):
    """
    API for Files event listener components.
    """

    def node_created(username, target_node):
        """
        Node attributes are as after creating the node.
        :param MappedFileNode target_node:
        """
        pass

    def node_moved(username, target_node, destination_node):
        """
        Node attributes are as before moving the node, after deleting
        possibly existing download data.
        :param MappedFileNode target_node:
        :param MappedFileNode destination_node:
        """
        pass

    def node_copied(username, target_node, destination_node):
        """
        Node attributes are as before copying the node.
        :param MappedFileNode target_node:
        :param MappedFileNode destination_node:
        """
        pass

    def node_removed(username, target_node):
        """
        Target node attributes are as before removing the node.
        :param MappedFileNode target_node:
        """
        pass

    def node_downloaded(username, target_node):
        """
        Target node attributes are as after increasing the download count.
        :param str username:
        :param MappedFileNode target_node:
        """
        pass
