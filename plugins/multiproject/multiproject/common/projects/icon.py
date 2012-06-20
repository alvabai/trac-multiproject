# -*- coding: utf-8 -*-
"""
Module contains the IconRendered Trac component that returns the project icon
as a HTTP request response. Component checks for SUMMARY_VIEW permission - otherwise
returns default icon.

Example queries:

- http://setup/home/projecticon?environment_name=funnyname
- http://setup/projectx/projecticon?environment_name=funnyname
- http://setup/projecty/projecticon?project_id=342

"""
import re
from hashlib import md5

from trac.core import Component, implements
from trac.resource import Resource
from trac.web import IRequestHandler

from multiproject.common.projects import Projects
from multiproject.core.db import admin_query
from multiproject.core.configuration import conf
from multiproject.core.cache.project_cache import ProjectCache


class IconRenderer(Component):
    """
    Component for rendering project icons

    Reads icon from database and makes http-response where Content-Type
    is set to correspond content type of the image

    Image data is then written into response body
    """
    implements(IRequestHandler)

    def match_request(self, req):
        """ Path for icon rendering
        """
        return re.match(r'/projecticon(?:_trac)?(?:/.*)?$', req.path_info)

    def process_request(self, req):
        """
        Process image request

        Image is fetch based on environment_name or project_id if both given, id is
        used on query

        Example query parts of request:
        ?environment_name=funnyname
        ?project_id=238
        """
        content = ''
        content_type = 'image/png'
        environment_name = req.args.get('environment_name')
        project_id = req.args.get('project_id')

        # Either env name or numeric id must be given
        if not any((environment_name, project_id)) or (project_id and not project_id.isdigit()):
            return req.send('Arguments required', status=400)

        # Load project with project id or env name
        if not project_id:
            project_id = Projects().get_project_id(env_name=environment_name)

        # If still no project id
        if not project_id:
            return req.send('', status=404)

        # Check permissions: if user has no permission, return default icon
        if  req.perm.has_permission('SUMMARY_VIEW', Resource('project', id=project_id)):
            icon = self.get_icon(project_id)
        else:
            self.log.info('User {0} has no SUMMARY_VIEW permission to see project icon: {1}'.format(req.authname, environment_name))
            icon = self.get_default_icon()

        # Split data
        if icon:
            content, content_type = icon

        # Calculate unique id for the the icon, for browser caching
        hash = md5()
        hash.update(content)
        etag = hash.hexdigest()

        # If browser already has it, response with 'not modified'
        if etag == dict(req._inheaders).get('if-none-match', ''):
            return req.send(content='', content_type=content_type, status=304)

        # Response with image data
        req.send_response(200)
        req.send_header('Content-Type', content_type)
        req.send_header('Content-Length', len(content))
        req.send_header('ETag', etag)
        req.end_headers()
        req.write(content)

    def get_icon(self, project_id):
        """ Fetch icon from database or from cache
        """
        cache = ProjectCache.instance()
        icon = cache.getProjectIcon(project_id)
        if not icon:
            icon = self.query_icon(project_id)
            if icon:
                cache.setProjectIcon(project_id, icon)
        if not icon:
            icon = self.get_default_icon()
        return icon

    def get_default_icon(self):
        cache = ProjectCache.instance()
        icon = cache.getDefaultProjectIcon()
        if not icon:
            icon = self.query_default_icon()
            if icon:
                cache.setDefaultProjectIcon(icon)
        return icon

    def query_icon(self, project_id):
        with admin_query() as cursor:
            query = """
            SELECT project_icon.* FROM project_icon
            LEFT JOIN projects ON projects.icon_id = project_icon.icon_id
            WHERE projects.project_id = %s
            """
            try:
                cursor.execute(query, project_id)
                row = cursor.fetchone()
                if not row:
                    return None
                # (content, content_type)
                return row[1], row[2]
            except Exception:
                conf.log.exception("Failed query icon: %s" % query)

    def query_default_icon(self):
        with admin_query() as cursor:
            query = """
            SELECT *
            FROM project_icon
            WHERE icon_id = %s
            """
            try:
                cursor.execute(query, conf.default_icon_id)
                row = cursor.fetchone()
                if not row:
                    self.log.warning('Default project icon is not set or found (see: default_icon_id)')
                    return None

                # (content, content_type)
                return row[1], row[2]
            except Exception:
                conf.log.exception("Failed query icon: %s" % query)
