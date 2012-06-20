from trac.core import Component, implements
from trac.web.api import IRequestFilter


class QueryInterceptor(Component):
    """ Interceptor that redirects user to previously used query location
        if no query parameters are given.
    """
    implements(IRequestFilter)
    
    def pre_process_request(self, req, handler):
        """ Redirect to last query location if it's in memory and no query param given
        """
        if req.path_info == '/query':
            defaultmax = self.config.getint('query', 'items_per_page', 100)
            try:
                max = int(req.args.get('max', defaultmax))
                if max == 0:
                    max = defaultmax
                elif max >200:
                    max = 200
                req.args['max'] = max
            except ValueError:
                req.args['max'] = defaultmax

        is_query_req = req.path_info == '/query' and req.method == 'GET'
        no_query_given = len(req.query_string) == 0
        has_stored_query = req.session.has_key('query_href')
            
        if is_query_req and no_query_given and has_stored_query:
            req.redirect(req.session['query_href'])
        return handler
    
    def post_process_request(self, req, template, data, content_type):
        """ This does nothing.. Interface just wants this..
        """
        return template, data, content_type
