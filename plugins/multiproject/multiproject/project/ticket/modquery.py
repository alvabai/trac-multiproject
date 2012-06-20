# -*- coding: utf-8 -*-
from pkg_resources import resource_filename #@UnresolvedImport

from genshi.filters.transform import Transformer #@UnresolvedImport

from trac.core import Component, implements
from trac.web.api import ITemplateStreamFilter
from trac.web.chrome import ITemplateProvider, Chrome

class QueryModifyModule(Component):
    implements(ITemplateProvider, ITemplateStreamFilter)

    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        return []
    
    def get_templates_dirs(self):
        
        return [resource_filename(__name__, 'templates')]
     
    # ITemplateStreamFilter methods
    def filter_stream(self, req, method, filename, stream, formdata):
        """Adds Batch modify as foldable and defaults filters and columns as collapsed"""

        if filename == 'query.html':
            return stream | Transformer('//div[@id="altlinks"]'). \
                                before(self._generate_form(req, formdata) )
                                
        if filename == 'batchmod.html':
            return stream | Transformer('//form[@id="batchmod-form"]//fieldset'). \
                                attr('id', 'batchmod') \
                          | Transformer('//form[@id="batchmod-form"]/fieldset/legend'). \
                                attr('class', 'foldable')

        return stream
 


    def _generate_form(self, req, data):
        batchFormData = dict(data)

        stream = Chrome(self.env).render_template(req, 'querymod.html',
              batchFormData, fragment=True)
        return stream.select('.')
