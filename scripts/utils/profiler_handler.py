# -*- coding: utf-8 -*-
"""
Mod python frontend to profile execution of requests with multiproject plugin enabled.

This essentially provides a mod_python handler, that is executed instead of trac's own
handler, but it does execute trac's web handler in the end.

All request times are written into a log.

Inspired by http://stackoverflow.com/questions/5511301/performance-analysis-of-mod-python-trac-instance

Requires handler configuration to be set as following in apache config::

<LocationMatch "^/(?!htdocs/.+)(?!dav/.+)(?!svn/.+)(?!git/.+)(?!hg/.+)(?!images/.+)(?!robots\.txt)">
    SetHandler mod_python
    PythonInterpreter main_interpreter
    PythonHandler multiproject.core.profiler_handler
    PythonOption TracEnvParentDir /var/www/trac/projects
    PythonOption TracUriRoot /
    PythonOption PYTHON_EGG_CACHE /dev/shm
    Order deny,allow
    Allow from all
</LocationMatch>

The handler then needs to be copied to /usr/local/lib/python2.7/dist-packages/TracMultiProject-../multiproject/core
"""
import pkg_resources

from trac import __version__ as TRAC_VERSION
from trac.web.modpython_frontend import ModPythonGateway
from mod_python import apache


def handler(req):
    pkg_resources.require('Trac==%s' % TRAC_VERSION)
    gateway = ModPythonGateway(req, req.get_options())

    from trac.web.main import dispatch_request
    import cProfile
    from datetime import datetime

    def profile_request(*args, **kwargs):
        prof = cProfile.Profile()
        prof.runcall(dispatch_request, *args, **kwargs)
        timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S.%f')
        prof.dump_stats('/var/www/trac/logs/request-%s' % timestamp)

    gateway.run(profile_request)
    return apache.OK
