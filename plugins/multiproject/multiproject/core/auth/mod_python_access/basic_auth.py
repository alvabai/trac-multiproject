# -*- coding: utf-8 -*-
from multiproject.core.auth.basic_access import BasicAccessControl


def headerparserhandler(req):
    from mod_python.apache import HTTP_UNAUTHORIZED, HTTP_FORBIDDEN, OK

    control = BasicAccessControl(req)

    # Check authentication
    if not control.is_authentic():
        req.err_headers_out['WWW-Authenticate'] = 'Basic realm="%s"' % control.options['realm']
        return HTTP_UNAUTHORIZED

    # Check if blocked or expired
    if control.is_blocked():
        return HTTP_FORBIDDEN

    return OK
