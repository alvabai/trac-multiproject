# -*- coding: utf-8 -*-
"""
Module for displaying Site Admin link in the user header
"""
import pkg_resources

from genshi.filters import Transformer
from trac.core import Component, implements
from trac.perm import PermissionCache
from trac.web import ITemplateStreamFilter
from trac.web.api import IRequestHandler, IRequestFilter
from trac.web.chrome import INavigationContributor, ITemplateProvider, add_script, tag, _
from multiproject.common.projects import HomeProject

class SiteAdmin(Component):
    implements(ITemplateStreamFilter)

    # ITemplateStreamFilter methods

    def filter_stream(self, req, method, filename, stream, data):
        """
        Add Site Admin link to user header area.

        """
        home_perm = PermissionCache(HomeProject().get_env(), username=req.authname)
        if 'USER_AUTHOR' not in home_perm and 'USER_CREATE' not in home_perm:
            return stream

        # Add following link into user header
        trans = Transformer('//div[@id="login_link"]/a[@class="author"]')\
            .after(tag.a('Site admin', href="#", class_="site_admin"))\
            .after(tag.span('|', class_="sep"))

        return stream | trans

class SiteAdminBox(Component):
    """
    Component injects required javascript resource to request, to provide Site Admin menu
    in every view.
    """
    implements(INavigationContributor, IRequestFilter, IRequestHandler, ITemplateProvider)

    # INavigationContributor methods

    def get_active_navigation_item(self, req):
        return 'site_admin'

    def get_navigation_items(self, req):
        yield ('metanav', 'site_admin', tag.a(_('Site admin'), **{'class': 'site_admin', 'href': '#'}))

    # IRequestFilter methods

    def pre_process_request(self, req, handler):
        """
        Process request to add some data in request
        """
        return handler

    def post_process_request(self, req, template, data, content_type):
        """
        Add global javascript data on post-processing phase
        """
        # When processing template, add global javascript json into scripts
        if template:
            # NOTE: Expecting other dependencies to be imported already
            add_script(req, 'multiproject/js/site_admin_box.js')

        return template, data, content_type

    # IRequestHandler methods

    def match_request(self, req):
        return req.path_info.startswith('/siteadmin/list')

    def process_request(self, req):
        home_perm = PermissionCache(HomeProject().get_env(), username=req.authname)
        user_author = False
        user_create = False
        if 'USER_AUTHOR' in home_perm:
            user_author = True
        if 'USER_CREATE' in home_perm:
            user_create = True
        data = {
            'user_author': user_author,
            'user_create': user_create
        }
        return 'multiproject_site_admin_box.html', data, None

    # ITemplateProvider methods

    def get_templates_dirs(self):
        return [pkg_resources.resource_filename('multiproject.common.siteadmin', 'templates')]

    def get_htdocs_dirs(self):
        return [('multiproject', pkg_resources.resource_filename(__name__, 'htdocs'))]
