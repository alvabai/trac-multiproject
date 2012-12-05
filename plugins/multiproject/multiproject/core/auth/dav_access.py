# -*- coding: utf-8 -*-
import urllib
from trac.core import TracError
from trac.env import open_environment
from trac.perm import PermissionCache, PermissionError

from multiproject.core.auth.basic_access import BasicAccessControl
from multiproject.core.files.api import MappedFileNode, normalized_base_url
from multiproject.core.configuration import conf
from multiproject.common.projects import Project
from multiproject.core.files.files_conf import FilesDownloadConfig, FilesConfiguration
from multiproject.project.files.timeline import FilesEventNotifier


class DAVAccessControl(BasicAccessControl):
    # Constants
    # For more details See. http://www.webdav.org/specs/rfc4918.html
    DAV_READ_METHODS = set(['HEAD', 'GET', 'OPTIONS', 'PROPFIND', 'REPORT'])
    # The following are not listed: 'LOCK', 'UNLOCK', 'PROPPATCH', 'POST'
    DAV_FILE_METHODS = set(['PUT', 'DELETE', 'MOVE', 'MKCOL', 'COPY'])
    DAV_DESTINATION_METHODS = set(['MOVE', 'COPY'])

    def __init__(self, req):
        BasicAccessControl.__init__(self, req)
        self.req = req
        self.method = req.method
        self._identifier = None

    def environment_identifier(self):
        # PythonOption project projectname
        # Parametrization for special cases
        if self._identifier:
            return self._identifier

        if 'project' in self.options:
            self._identifier = self.options['project']
        else:
            # Try from uri
            self._identifier = self.parse_identifier_from_uri()

        return self._identifier

    def is_read(self):
        """ True read, False write
        """
        return self.method in self.DAV_READ_METHODS


class DownloadsDAVAccessControl(DAVAccessControl):

    def __init__(self, req):
        super(DownloadsDAVAccessControl, self).__init__(req)
        self._destination_node = None
        self._target_node = None
        self._req_data = None
        self._download_config = None
        self._env = None

    def environment_identifier(self):
        # PythonOption project projectname
        # Parametrization for special cases
        if self._identifier:
            return self._identifier

        if 'project' in self.options:
            self._identifier = self.options['project']
        else:
            # Try from uri
            self._identifier = self.parse_identifier_from_uri()

        return self._identifier

    def destination_path_ok(self):
        if self.method in DAVAccessControl.DAV_DESTINATION_METHODS:
            try:
                destination_node = self.destination_node
            except NodeError as e:
                conf.log.debug("Failed to destination_path_ok %s %s %s",
                    self.method, self.req.uri, e)
                return False
        return True

    @property
    def destination_node(self):
        if self._destination_node is not None:
            return self._destination_node

        # If req is a sub-request, req.main is the main request.
        destination = self._get_header('Destination')

        if destination:
            # Parse path from url
            try:
                encoded_destination = normalized_base_url(destination)
                destination = urllib.unquote(encoded_destination).decode('UTF-8')
                self._destination_node = MappedFileNode.from_request_path_info(destination,
                    self.target_node)
            except Exception as e:
                raise NodeError('Destination node was invalid: %s'%str(e))

        return self._destination_node

    @property
    def target_node(self):
        if self._target_node is not None:
            return self._target_node
        env_name = self.environment_identifier()
        if not env_name:
            conf.log.warning("Failed reading identifier")
            raise NodeError('Target node was invalid: env_name not found')
        project = Project.get(env_name=env_name)
        # env_name might be different from project.env_name!
        base_url = project.get_dav_url(relative=True)
        path_info = normalized_base_url(self.req.uri)
        project_id = project.id
        download_config = FilesDownloadConfig(project.env_name, base_url=base_url)
        if not path_info.startswith(download_config.base_url):
            raise NodeError('Target node was invalid: uri %s does not start with %s',
                path_info, base_url)
        self._download_config = download_config
        try:
            node_factory = MappedFileNode(project_id,
                download_config.base_path, download_config.base_url, download_config.downloads_dir)
            self._target_node = MappedFileNode.from_request_path_info(path_info, node_factory)
        except Exception as e:
            conf.log.warning("Not node %s", str(e))
            raise NodeError('Target node was invalid: %s', str(e))

        return self._target_node

    def _get_header(self, header):
        if self.req.main is not None:
            # If req is a sub-request, req.main is the main request.
            value = self.req.main.headers_in.get(header)
        else:
            value = self.req.headers_in.get(header)
        return value

    def has_permission(self):
        """
        Returns True, if has permission, otherwise False.

        Must be called after the is_blocked.
        """
        node = None
        destination_node = None
        try:
            node = self.target_node
            if self.method in DAVAccessControl.DAV_DESTINATION_METHODS:
                destination_node = self.destination_node
        except NodeError as e:
            conf.log.warning("Failed to get node %s %s %s"%(self.method, self.req.uri, str(e)))
            return False

        if not self.user:
            # User was not found: for example, 'anonymous' does not exist
            return False

        env = open_environment(conf.getEnvironmentSysPath(self._download_config.env_name),
            use_cache=True)
        perm = PermissionCache(env, self.username)

        timeline_notifier = FilesEventNotifier(env)
        depth = self._get_header('Depth') # ("0" | "1" | "infinity")
        # When checking, let the server to decide whether or not to return 412: Precondition Failed
        overwrite = self._get_header('Overwrite') == 'T' # ( "T" | "F" )
        self._req_data = {
            'uploader_id': self.user.id,
            'perm': perm,
            'context': 'webdav',
            'timeline_notifier': timeline_notifier,
            'username': self.user.username,
        }
        if self.method in self.DAV_READ_METHODS:
            try:
                node.show_check(self._req_data)
            except PermissionError as e:
                conf.log.debug("PermissionError node %s %s", self.method, self.req.uri)
                return False
        # Special case: copy for Collection with depth 0 is equivalent to MKCOL
        elif ((self.method == 'COPY' and depth == '0' and node.is_dir())
              or self.method == 'MKCOL' or self.method == 'PUT'):
            if self.method == 'COPY' and depth == '0' and node.is_dir():
                # For our causes, this method is 'MKCOL', even if it was 'COPY'
                self.method = 'MKCOL'
                node = destination_node
                self._target_node = node
            self._req_data.update({
                'update_also': False,
                # It seems that creating files and folders will overwrite existing ones
                'overwrite': True,
                'type': 'file' if self.method == 'PUT' else 'dir',
                'sanity_check': False,
                })
            try:
                node.create_check(self._req_data)
            except TracError as e:
                return False
            except PermissionError as e:
                conf.log.debug("PermissionError node %s %s", self.method, self.req.uri)
                return False
        elif self.method in self.DAV_DESTINATION_METHODS:
            self._req_data.update({
                'update_also': False,
                'overwrite': overwrite,
                'is_move': self.method == 'MOVE',
                'sanity_check': False,
                })
            try:
                node.move_check(destination_node, self._req_data)
            except TracError as e:
                return False
            except PermissionError as e:
                conf.log.debug("PermissionError node %s %s", self.method, self.req.uri)
                return False
        elif self.method == 'DELETE':
            self._req_data.update({
                'sanity_check': False,
                'force_remove': True,
            })
            try:
                node.remove_check(self._req_data)
            except TracError as e:
                return False
            except PermissionError as e:
                conf.log.debug("PermissionError node %s %s", self.method, self.req.uri)
                return False
        else:
            conf.log.warning("Unknown webdav method: '%s', '%s'", self.method, self.req.uri)
            return False
        return True

    def post_permission_check_hooks(self):
        """
        Insert event in timeline
        """
        try:
            if 200 <= self.req.status < 300:
                node = self.target_node
                if self.method == 'GET':
                    node.show_post_process(self._req_data)
                # Special case: copy for Collection with depth 0 is equivalent to MKCOL
                elif self.method == 'MKCOL' or self.method == 'PUT':
                    node.create_post_process(self._req_data)
                elif self.method in self.DAV_DESTINATION_METHODS:
                    node.move_post_process(self.destination_node, self._req_data)
                elif self.method == 'DELETE':
                    node.remove_post_process(self._req_data)
                else:
                    pass
        except Exception as e:
            # Failed to write event in timeline: that's ok'ish
            conf.log.exception("DAVAccessControl: Failed running post permission check hooks")


class NodeError(Exception):
    pass
