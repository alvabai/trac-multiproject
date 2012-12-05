# -*- coding: utf-8 -*-
"""
Module contains a simple Trac component that returns partial search results
when ``action=results`` in request.
"""
import pkg_resources

from trac.core import Component, implements
from trac.web.api import IRequestFilter
from trac.web.chrome import add_script, ITemplateProvider


class AjaxSearch(Component):
    """
    Interceptor for using ajax in project's search
    """
    implements(IRequestFilter, ITemplateProvider)

    # IRequestFilter methods

    def pre_process_request(self, req, handler):
        """ No pre-processing required """
        return handler

    def post_process_request(self, req, template, data, content_type):
        """
        Let trac handle searching first, but use a separate template
        for our ajax search request
        """
        if req.path_info == '/search':
            # Replace the template and add some custom js for doing the AJAX requests
            template = 'multiproject_search.html'
            add_script(req, 'multiproject/js/jquery.ba-bbq.js')
            add_script(req, 'multiproject/js/search.js')

            if req.args.get('action') == 'results': # this is our ajax request
                return 'multiproject_search_results.html', data, content_type

        return template, data, content_type

    # ITemplateProvider methods

    def get_templates_dirs(self):
        return [pkg_resources.resource_filename('multiproject.project.search', 'templates')]

    def get_htdocs_dirs(self):
        return [('multiproject', pkg_resources.resource_filename(__name__, 'htdocs'))]
