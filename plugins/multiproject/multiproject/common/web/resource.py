# -*- coding: utf-8 -*-
"""
Module implements two Trac components, providing plugin specific resources and javascript data.

Resources
----------
The resources commonly used to be found from
``multiproject/common/web/htdocs``. Example usage::

    from trac.web.chrome import add_script
    add_script(req, 'multiproject/js/jquery-ui.js')

Following resources are provided by the plugin:

- jquery-ui.js: jQuery UI libraries
- jquery-ui.css: jQuery UI css (default stylesheet)

JavaScript
----------
For each request, some global variables are introduced - making it possible to use
them in javascript and template without re-rendering with Genshi:

.. code-block:: javascript

    // Make AJAX request to fetch users
    element.addClass('loading');
    $.getJSON(multiproject.req.base_path + "/api/user/list", {q:'foo', fields:'id,username'}, function(data){
        response(data);
        element.removeClass('loading');
    });

"""
from collections import Mapping
from pkg_resources import resource_filename

from trac.core import implements, Component, ExtensionPoint, Interface
from trac.web.chrome import ITemplateProvider, add_script_data
from trac.web.api import IRequestFilter


class CommonResourceModule(Component):
    """
    Provides common templates and resources for multiproject plugin.
    Inject the scripts in component with:

        from trac.web.chrome import add_script
        add_script(req, 'multiproject/js/raphael.js')

    """
    implements(ITemplateProvider)

    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        """
        Return a list of directories with static resources (such as style
        sheets, images, etc.)
        """
        return [('multiproject', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        return []


class JQueryUpgradeFilter(Component):
    """
    Filters the jquery version coming with Trac and replaces it with own
    """
    implements(IRequestFilter)

    # IRequestFilter methods

    def pre_process_request(self, req, handler):
        """
        Process request to add some data in request
        """

        return handler

    def post_process_request(self, req, template, data, content_type):
        """
        Does the post processing for the request: removes built-in jquery.js
        from the scriptset and adds own in place.

        :param Request req: Trac request
        :param str template: template name
        :param dict data: Dictionary of data
        :param str content_type: Content type like 'text/html'
        :return: Tuple of data
        """
        scripts = req.chrome['scripts']
        old_jquery = 'common/js/jquery.js'

        def jqupdate(elem):
            if elem['href'].endswith('/js/jquery.js'):
                elem['href'] = str(req.href.chrome('multiproject/js/jquery.js'))
            return elem

        req.chrome['scripts'] = map(jqupdate, scripts)

        if old_jquery in req.chrome['scriptset']:
            req.chrome['scriptset'].remove(old_jquery)

        return template, data, content_type


class IJSONDataPublisherInterface(Interface):
    """
    Interface for publishing objects into global namespace
    """
    def publish_json_data(req):
        """
        Provide data that should be published in global namespace
        Return data in dict format
        """
        return {}


class JSDataFilter(Component):
    """
    Introduces global variables (registered by the components) into template. See
    :class:`IJSONDataPublisherInterface` for more info how to extend the data.

    With this, you can easily access the exposed data directly from javascript:

    .. code-block:: javascript

        // Make AJAX request to fetch users
        element.addClass('loading');
        $.getJSON(multiproject.req.base_path + "/api/user/list", {q:'foo', fields:'id,username'}, function(data){
            response(data);
            element.removeClass('loading');
        });

    """
    implements(IRequestFilter, IJSONDataPublisherInterface)
    json_data_publishers = ExtensionPoint(IJSONDataPublisherInterface)

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
            add_script_data(req, {'multiproject': self._get_published_data(req)})

        return template, data, content_type

    # IJSONDataPublisherInterface methods

    def publish_json_data(self, req):
        return {
            'req': {
                'base_path': req.base_path,
                'authname': req.authname
        }}

    def _get_published_data(self, req):
        """
        Method retrieves the data published by the plugins

        TODO: Cache results?
        """
        data = {}
        for publisher in self.json_data_publishers:
            data = self._update_recursive(data, publisher.publish_json_data(req))

        return data

    def _update_recursive(self, dict1, dict2):
        """
        Update dictionary 1 with dictionary 2 in recursive manner

        :param dict dict1: Dictionary to update
        :param dict2: Dictionary or Mapping to update from
        :return: Updated dictionary
        """
        for k, v in dict2.iteritems():
            if isinstance(v, Mapping):
                r = self._update_recursive(dict1.get(k, {}), v)
                dict1[k] = r
            else:
                dict1[k] = dict2[k]
        return dict1

