# -*- coding: utf-8 -*-
import re

from trac.core import Component, implements
from trac.web import IRequestHandler

class HealthCheckModule(Component):
    """ Keep this minimal
    """
    implements(IRequestHandler)

    def match_request(self, req):
        return re.match(r'/health(?:_trac)?(?:/.*)?$', req.path_info)

    def process_request(self, req):
        req.send("OK")