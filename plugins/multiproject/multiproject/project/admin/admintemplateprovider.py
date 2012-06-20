# -*- coding: utf-8 -*
from pkg_resources import resource_filename

from trac.core import Component, implements
from trac.web.chrome import ITemplateProvider


class MultiprojectAdminTemplateProvider(Component):
    implements(ITemplateProvider)

    def get_templates_dirs(self):
        return [resource_filename('multiproject.project.admin', 'templates')]

    def get_htdocs_dirs(self):
        return [('multiproject', resource_filename(__name__, 'htdocs'))]