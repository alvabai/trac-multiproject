# -*- coding: utf-8 -*-
from multiproject.core.auth.hg_access import MercurialAccessControl


def headerparserhandler(req):
    from mod_python.apache import HTTP_UNAUTHORIZED, HTTP_FORBIDDEN, OK

    control = MercurialAccessControl(req)

    if not control.is_authentic():
        req.err_headers_out['WWW-Authenticate'] = 'Basic realm="%s"' % control.options['realm']
        return HTTP_UNAUTHORIZED

    # Check if blocked or expired
    if control.is_blocked():
        return HTTP_FORBIDDEN

    if not control.has_permission():
        if 'Authorization' not in req.headers_in:
            req.err_headers_out['WWW-Authenticate'] = 'Basic realm="%s"' % control.options['realm']
            return HTTP_UNAUTHORIZED
        return HTTP_FORBIDDEN

    if not control.is_allowed_scheme('hg'):
        return HTTP_FORBIDDEN

    return OK
