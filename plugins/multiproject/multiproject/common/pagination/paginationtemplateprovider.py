from pkg_resources import resource_filename #@UnresolvedImport

from trac.core import Component, implements
from trac.web.chrome import ITemplateProvider

class PaginationTemplateProvider(Component):
    implements(ITemplateProvider)

    def get_templates_dirs(self):
        return [resource_filename('multiproject.common.pagination', 'templates')]

    def get_htdocs_dirs(self):
        return []
