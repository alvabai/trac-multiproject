# -*- coding: utf-8 -*-
from trac.core import Component

from trac.config import Option, PathOption, BoolOption

from multiproject.common.projects import Project
from multiproject.core.files.files_conf import FilesDownloadConfig
from multiproject.core.util.request import get_context
from multiproject.core.files.api import MappedFileNode, InvalidOperationError, normalized_base_url


class FilesCoreComponent(Component):
    """
    Helper component for the file configurations etc.
    """

    default_downloads_directory = Option('multiproject-files', 'default_downloads_directory',
        default='downloads',
        doc='Default name of the directory which is created for project. ')

    sys_dav_root = PathOption('multiproject-files', 'sys_dav_root',
        default='/var/www/trac/webdav',
        doc='Path to the root directory of the webdav directory. '
            'For example, "/path/to/multiproject/root/webdav". ')

    url_dav_path = Option('multiproject-files', 'url_dav_path',
        default='dav',
        doc='Relative url path to the dav directory after [multiproject] url_projects_path. '
            'For example, "dav". ')

    downloads_dir_customizable = BoolOption('multiproject-files', 'downloads_dir_customizable',
        default='True',
        doc="Whether or not projects can configure their downloads directory, "
            "or whether to use the MultiProject-wide configurations. "
            "Setting this to False improves performance. ")

    def base_url(self, context_name='files'):
        env_name = self.env.project_identifier
        if context_name == 'files':
            return '/files'
        elif context_name == 'webdav':
            return '/'.join([self.config.get('multiproject',
                'url_projects_path', ''), self.url_dav_path, env_name])
        else:
            raise InvalidOperationError("context name was wrong")

    def files_download_config(self, context_name='files', req=None):
        """
        :param str context_name: either 'files' or 'webdav'
        :return: FilesDownloadConfig
        """
        ctx = None
        ctx_key = 'files.download_config.' + context_name
        if req:
            ctx = get_context(req)
            try:
                return ctx[ctx_key]
            except KeyError:
                pass
        env_name = self.env.project_identifier
        base_url = self.base_url(context_name=context_name)
        download_config = FilesDownloadConfig(env_name, base_url=base_url)
        if ctx:
            ctx[ctx_key] = download_config
        return download_config

    def files_node_factory_and_config(self, req=None, context_name='files'):
        """
        :param req: Request object
        :param str context_name: either 'files' or 'webdav'
        :return:
        """
        ctx = None
        ctx_key = 'files.node_factory.' + context_name
        if req:
            ctx = get_context(req)
            try:
                return ctx[ctx_key], self.files_download_config(context_name, req=req)
            except KeyError:
                pass
        download_config = self.files_download_config(context_name=context_name, req=req)
        project = Project.get(self.env)
        project_id = project.id
        node_factory = MappedFileNode(project_id,
            download_config.base_path, download_config.base_url, download_config.downloads_dir)
        if ctx:
            ctx[ctx_key] = node_factory
        return node_factory, download_config

    def order_files_and_dirs(self, req, is_download, dirs=None, files=None):
        order_by = req.args.get('files_order_by', 'filename')
        order_reversed = req.args.get('files_order_in', 'asc') == 'desc'

        dir_key = None
        if order_by == 'filename':
            key = lambda node: node.filename
        elif order_by == 'count' and is_download:
            key = lambda node: (node.download().count, node.filename)
            dir_key = lambda node: node.filename
        elif order_by == 'featured' and is_download:
            key = lambda node: (node.download().is_featured() and 1 or 0, node.filename)
            dir_key = lambda node: node.filename
        elif order_by == 'modified':
            if is_download:
                key = lambda node: (node.download().created, node.filename)
                dir_key = lambda node: (node.time_changed, node.filename)
            else:
                key = lambda node: (node.time_changed, node.filename)
        elif order_by == 'size':
            key = lambda node: (node.size, node.filename)
            dir_key = lambda node: node.filename
        else:
            key = lambda node: node.filename
        if files:
            files.sort(key=key, reverse=order_reversed)
        if dirs:
            if not dir_key:
                dirs.sort(key=key, reverse=order_reversed)
            else:
                dirs.sort(key=dir_key, reverse=order_reversed)

