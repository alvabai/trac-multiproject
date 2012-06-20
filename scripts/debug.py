# -*- coding: utf-8 -*-
'''
This file a plain python script for running the tracd, making it possible to
run it directly from the debugger.

When running the debugger, set following environment variables (default values shown next to key):

- TRAC_HOST: 127.0.0.1
- TRAC_PORT: 8000
- TRAC_PARENT_DIR: /storage/trac/projects
- TRAC_AUTORELOAD: false

'''
import sys, os

from trac.util import autoreload
from trac.web.standalone import TracHTTPServer, TracEnvironMiddleware, BasePathMiddleware
from trac.web.main import dispatch_request
from trac.env import open_environment

server_host = os.getenv('TRAC_HOST', '127.0.0.1')
server_reload = True if 'true' == os.getenv('TRAC_AUTORELOAD', 'false') else False
server_port = os.getenv('TRAC_PORT', 8000)
server_address = (server_host, int(server_port))
env_parent_dir = os.getenv('TRAC_PARENT_DIR', '/storage/trac/projects')

class AliasMiddleware(object):
    """
    Custom middleware to imitate the apache alias paths. For example::

        /htdocs/trac/js/trac.js --> http://localhost/htdocs/trac.js
    """
    def __init__(self, application, base_path):
        self.base_path = '/' + base_path.strip('/')
        self.application = application

    def __call__(self, environ, start_response):
        """
        The function is called when middleware class is invoked.
        """

        def custom_start_response(status, headers, exc_info=None):
            """
            Custom response to modify the headers
            """
            url = str(environ['PATH_INFO'])
            url = url.replace('/trac', 'http://localhost/htdocs/trac', 1)
            url = url.replace('/theme', 'http://localhost/htdocs/theme', 1)
            status = '301 Moved Permanently'
            headers.append(('Location', url))
            
            return start_response(status, headers, exc_info)

        if str(environ['PATH_INFO']).startswith('/htdocs/trac'):
            return self.application(environ, custom_start_response)

        if str(environ['PATH_INFO']).startswith('/htdocs/theme'):
            return self.application(environ, custom_start_response)

        return self.application(environ, start_response)

def serve():
    base_path = '/'
    single_env = False
    args = {}

    wsgi_app = TracEnvironMiddleware(dispatch_request, env_parent_dir, args, single_env)
    wsgi_app = BasePathMiddleware(wsgi_app, base_path)
    wsgi_app = AliasMiddleware(wsgi_app, base_path)
    httpd = TracHTTPServer(server_address, wsgi_app, env_parent_dir, args, use_http_11=False)

    # Validate the trac environment (because trac seems to be too quiet sometimes)
    env_path = '%s/home' % env_parent_dir
    env = open_environment(env_path, use_cache=True)

    # Check the access
    for fpath in [env.config.filename]:
        try:
            os.stat(fpath)
        except OSError:
            raise Exception('Cannot access config file: %s - permission issue perhaps?' % fpath)

    httpd.serve_forever()


def modification_callback(file):
    print >> sys.stderr, 'Detected modification of %s, restarting...' % file

if server_reload:
    autoreload.main(serve, modification_callback)
else:
    serve()

