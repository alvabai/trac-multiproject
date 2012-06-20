# -*- coding: utf-8 -*-
"""
This module implements the modpython handler(s) that adds support for
virtualenv environments.

Apache configuration::

    <LocationMatch "/foo/bar">
        PythonPath "['/path/to/folder/where/this/file/is'] + sys.path"
        PythonHandler modpython_handler
        PythonOption virtualenvpath "/path/to/virtualenv"
        PythonOption headerparserhandler "multiproject.core.auth.mod_python_access.basic_auth"
    </LocationMatch>

    <LocationMatch "/foo/baz">
        PythonPath "['/path/to/folder/where/this/file/is'] + sys.path"
        PythonHandler modpython_handler
        PythonOption virtualenvpath "/path/to/virtualenv"
        PythonOption handler "trac.web.modpython_frontend"
    </LocationMatch>

How to configure handler in Apache:

- PythonPath: Ensure this file exists in the PYTHONPATH
- PythonOption virtualenvpath: Path to virtualenv folder
- PythonOption headerparserhandler: Module name that actually implements the handler

.. NOTE::

    Handler can be either:

    - handler
    - headerparserhandler
    - authenhandler

"""
__author__ = 'jumuston'

import sys
import os

def create_handle(name):
    """
    Handle incoming modpython request and access the options given to it
    to import and redirect the request to actual implementation
    """
    def handler(req):
        options = req.get_options()
        virtualenv_path = options.get('virtualenvpath', '')
        handler_name = options.get(name, '')

        if not virtualenv_path:
            raise Exception('Please set PythonOption virtualenvpath "/path/to/env" in Apache configuration')

        # Activate virtualenvironment based on given PythonOption: virtualenvpath
        activate_this = os.path.join(virtualenv_path, 'bin/activate_this.py')
        execfile(activate_this, dict(__file__=activate_this))

        # Import the module based on given PythonOption: 'name': handler, headerparserhandler...
        __import__(handler_name)
        mod = sys.modules[handler_name]

        # Request the actual handler
        return getattr(mod, name)(req)

    return handler

handler = create_handle('handler')
headerparserhandler = create_handle('headerparserhandler')
authenhandler = create_handle('authenhandler')
