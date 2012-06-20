from trac.core import Component, implements
from trac.web.api import IRequestFilter

class SearchInterceptor(Component):
    """ Interceptor for using ajax in project's search
    """
    implements(IRequestFilter)

    def pre_process_request(self, req, handler):
        """ No pre-processing required """
        return handler

    def post_process_request(self, req, template, data, content_type):
        """ Let trac handle searching first, but use a separate template
            for our ajax search request
        """
        if req.path_info == '/search':
            if req.args.get('action') == 'results': # this is our ajax request
                return 'search_results.html', data, content_type

        return template, data, content_type
