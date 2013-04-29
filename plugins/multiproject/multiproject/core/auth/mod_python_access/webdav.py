# -*- coding: utf-8 -*-
from multiproject.core.auth.dav_access import DownloadsDAVAccessControl
from multiproject.core.configuration import Configuration
conf = Configuration.instance()
try:
    # If this file is included via python console, the following import would cause problems
    from mod_python.apache import HTTP_UNAUTHORIZED, HTTP_FORBIDDEN, HTTP_BAD_REQUEST, OK
except ImportError as e:
    OK = 200
    HTTP_BAD_REQUEST = 400
    HTTP_UNAUTHORIZED = 401
    HTTP_FORBIDDEN = 403

def headerparserhandler(req):

    control = DownloadsDAVAccessControl(req)
    # Lets store the control into req.multiproject_control:
    req.multiproject_control = control

    if not control.is_authentic():
        req.err_headers_out['WWW-Authenticate'] = 'Basic realm="%s", accept-charset="UTF-8"' % control.options['realm']
        return HTTP_UNAUTHORIZED

    # Check if blocked or expired
    if control.is_blocked():
        return HTTP_FORBIDDEN

    # Special case for handling destination move and copy
    if not control.destination_path_ok():
        return HTTP_BAD_REQUEST

    if not control.has_permission():
        if 'Authorization' not in req.headers_in:
            req.err_headers_out['WWW-Authenticate'] = 'Basic realm="%s", accept-charset="UTF-8"' % control.options['realm']
            return HTTP_UNAUTHORIZED
        return HTTP_FORBIDDEN

    if not control.is_allowed_scheme('dav'):
        return HTTP_FORBIDDEN

    return OK

def cleanuphandler(req):
    """
    We do the post-permission hooks here, as this way the request gets sent and connection closed
    before actually calculating the hash.
    """
    control = req.multiproject_control

    # Run post permission check hooks and make sure
    # we do not leak exceptions from here
    control.post_permission_check_hooks()

    return OK
