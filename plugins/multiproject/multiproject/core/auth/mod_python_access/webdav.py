# -*- coding: utf-8 -*-
from multiproject.core.auth.dav_access import DAVAccessControl
from multiproject.core.configuration import conf


def headerparserhandler(req):
    # If this file is included via python console, the following import would cause problems
    from mod_python.apache import HTTP_UNAUTHORIZED, HTTP_FORBIDDEN, HTTP_BAD_REQUEST, OK

    control = DAVAccessControl(req)

    if not control.is_authentic():
        req.err_headers_out['WWW-Authenticate'] = 'Basic realm="%s", accept-charset="UTF-8"' % control.options['realm']
        return HTTP_UNAUTHORIZED

    # Special case for handling destination move and copy
    if not control.destination_path_ok():
        return HTTP_BAD_REQUEST

    # Check if blocked or expired
    if control.is_blocked():
        return HTTP_FORBIDDEN

    if not control.has_permission():
        if 'Authorization' not in req.headers_in:
            req.err_headers_out['WWW-Authenticate'] = 'Basic realm="%s", accept-charset="UTF-8"' % control.options['realm']
            return HTTP_UNAUTHORIZED
        return HTTP_FORBIDDEN

    if not control.is_allowed_scheme('dav'):
        return HTTP_FORBIDDEN

    # Run post permission check hooks and make sure
    # we do not leak exceptions from here
    try:
        control.post_permission_check_hooks()
    # Failed to write event in timeline: that's ok'ish
    except:
        conf.log.exception("DAVAccessControl: Failed running post permission check hooks")

    return OK
