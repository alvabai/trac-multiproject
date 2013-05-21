# -*- coding: utf-8 -*-
"""
This module contains the category related components, intended for (home/project) admins.
Thus, it is available both in project and home urls:

- http://localhost/home/catautocomplete?q=foo
- http://localhost/projectx/catautocomplete?q=bar&limit=2

"""
import json

from trac.core import Component, implements
from trac.web import IRequestHandler

from multiproject.core.categories import CQDECategoryStore


class CategoriesJSONRequestHandler(Component):
    """
    Implements the request handler that returns the categories in JSON format.
    """
    implements(IRequestHandler)

    def match_request(self, req):
        """
        Check if request should be handled by this handler
        """
        return req.path_info.startswith('/catautocomplete')

    def process_request(self, req):
        """ Process request for listing, creating and removing projects
        """
        categories = []
        q_filter = req.args.get('q')
        limit = req.args.get('limit')
        contexts = req.args.get('contexts[]')
        if contexts:
            if not isinstance(contexts, list):
                contexts = [contexts]

        # Second option: provide contexts in comma separated list
        if not contexts:
            contexts = req.args.get('contexts')
            if contexts:
                contexts = contexts.split(',')

        if q_filter:
            catstore = CQDECategoryStore()
            categories = catstore.get_category_by_name_filter(q_filter, limit, contexts)

        # Construct response in JSON list format
        data = ''
        try:
            data = json.dumps([category.name.encode("utf-8").split("#")[0] for category in categories])
        except Exception, e:
            self.log.exception('Returning JSON from categories failed')

        req.send(data, content_type='application/json', status=200)


