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
    $.getJSON(multiproject.req.base_path + "/userautocomplete", {q:'foo', fields:'id,username'}, function(data){
        response(data);
        element.removeClass('loading');
    });

"""
from pkg_resources import resource_filename

from trac.core import implements, Component
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


class JSDataFilter(Component):
    """
    Introduces global variables into template::

        multiproject
            req
                base_path: Base path of request
                authname: Authenticated username
            conf

    With this, you can easily access the exposed data directly from javascript:

    .. code-block:: javascript

        // Make AJAX request to fetch users
        element.addClass('loading');
        $.getJSON(multiproject.req.base_path + "/userautocomplete", {q:'foo', fields:'id,username'}, function(data){
            response(data);
            element.removeClass('loading');
        });

    """
    implements(IRequestFilter)

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
            global_js = {
                # Trac request
                'req':{
                    'base_path':req.base_path,
                    'path_info':req.path_info,
                    'authname':req.authname
                },
                'conf':{
                    # For datepicker
                    'dateformat':'mm/dd/y'
                }
            }
            add_script_data(req, {'multiproject':global_js})

        return template, data, content_type