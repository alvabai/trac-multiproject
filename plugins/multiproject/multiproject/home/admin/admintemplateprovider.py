from pkg_resources import resource_filename

from trac.core import Component, implements
from trac.web.chrome import ITemplateProvider

class MultiprojectAdminTemplateProvider(Component):
    implements(ITemplateProvider)

    def get_templates_dirs(self):
        return [resource_filename('multiproject.home.admin', 'templates')]

    def get_htdocs_dirs(self):
        """
        Return a list of directories with static resources (such as style
        sheets, images, etc.)

        In this case, the resources are added into page with command::

            add_script(req, 'multiproject/js/raphael.js')
            add_script(req, 'multiproject/js/ico.js')

        """
        return [('multiproject', resource_filename(__name__, 'htdocs'))]