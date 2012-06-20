# -*- coding: utf-8 -*-
import re, MySQLdb

from trac.core import Component, implements
from trac.web import IRequestHandler

from multiproject.core.db import admin_query, safe_int


class IconRenderer(Component):
    """ Component for rendering user icons

        Reads icon from database and makes http-response where Content-Type
        is set to correspond content type of the image

        Image data is then written into response body
    """
    implements(IRequestHandler)

    def match_request(self, req):
        """ Path for icon rendering
        """
        return re.match(r'/usericon(?:_trac)?(?:/.*)?$', req.path_info)

    def process_request(self, req):
        """ Process image request

            Image is fetch based on username or user_id if both given, id is
            used on query

            Example query parts of request:
            ?username=jdoe
            ?user_id=238
        """
        user_id = req.args.get('user_id')
        username = req.args.get('username')

        # Prefer user id if available
        if username:
            where = "user.username = '%s'" % MySQLdb.escape_string(username)
        if user_id:
            where = "user.user_id = %s" % safe_int(user_id)

        content = ""
        content_type = "/image/png"

        query = ("SELECT user_icon.* FROM user_icon "
                 "INNER JOIN user ON user.icon_id = user_icon.icon_id "
                 "WHERE %s" % where)

        with admin_query() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone()
                if row:
                    content = row[1]
                    content_type = row[2]
            except:
                self.log.exception("IconRenderer.process_request failed with query %s" % query)

        # Create response
        req.send_response(200)
        req.send_header('Content-Type', content_type)
        req.send_header('Content-Length', len(content))
        req.end_headers()
        req.write(content)
