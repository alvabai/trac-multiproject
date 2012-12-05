# -*- coding: utf-8 -*-
"""
Contains helpers and tools for building RESTful API
"""
from datetime import datetime
import json


def json_encoder(o):
    """
    Custom JSON encoder: look for __json__ function
    and use it for generating dict (and finally JSON) presentation
    from the multiproject database objects.

    >>> class MyObject(object):
    >>>     def __init__(self, id, title):
    >>>         self.id = id
    >>>         self.title = title
    >>>
    >>>     def __json__(self):
    >>>         return {'id':self.id, 'title':self.title}
    >>> json.dumps(myobject, default=json_encoder)
    {'id':324, 'title':foo}

    """
    if hasattr(o, '__json__'):
        return o.__json__()

    if isinstance(o, datetime):
        # Ensure everyone gets the timezone info
        if o.tzinfo is None:
            return '%sZ' % o.isoformat()
        return o.isoformat()

    # Encoder must raise TypeError if encoding should be delegated
    raise TypeError(type(o))


def send_json(req, data, status=200):
    """
    Return Trac response in JSON. Example usage::

        from multiproject.core.restful import send_json

        def process_request(req):
            data = ['data', {'to': 'send'}]
            return send_json(req, data)

    Shortcut to::

        from multiproject.core.restful import json_encoder
        data = {'key':'data}
        req.send(json.dumps(data, default=json_encoder), content_type='application/json', status=200)

    :param Request req: Trac request
    :param data: Any data that can be serialized
    :param int status: HTTP response code. 200 by default.
    :returns: Trac response

    """
    json_data = json.dumps(data, default=json_encoder)
    return req.send(json_data, content_type='application/json', status=status)