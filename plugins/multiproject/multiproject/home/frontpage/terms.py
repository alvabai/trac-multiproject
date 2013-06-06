# -*- coding: utf-8 -*-
import re
from pkg_resources import resource_filename #@UnresolvedImport

from trac.core import Component, implements
from trac.web import IRequestHandler
from trac.web.chrome import ITemplateProvider

class TermsModule(Component):
    """ Trac component for showing terms and conditions
        Should be used on home project only.
    """
    implements(ITemplateProvider, IRequestHandler)
    
    # IRequestHandler methods
    def match_request(self, req):
        """ Match /welcome path to this page 
        """
        return re.match(r'/terms(?:_trac)?(?:/.*)?$', req.path_info)

    def process_request(self, req):
        """ Render welcome page
        """
        
        data = {
            'domain': req.server_name
        }
        
        return "terms.html", data, None
    
    # ITemplateProvider methods
    def get_templates_dirs(self):
        return [resource_filename(__name__, 'templates')]
    
    def get_htdocs_dirs(self):
        return []
