# -*- coding: utf-8 -*-
from trac.core import Component, implements, ExtensionPoint
from trac.mimeview.api import Context
from trac.util.translation import _
from trac.admin.api import IAdminPanelProvider
from trac.web.api import Href, RequestDone
from trac.web.chrome import add_warning, add_script, add_stylesheet
from multiproject.core.configuration import conf

class RepositoriesAdminPanel(Component):
    implements(IAdminPanelProvider)
    homeurl = Href(conf.url_home_path)

    def get_admin_panels(self, req):
        if 'TRAC_ADMIN' in req.perm:
            yield ('general', _('General'), 'vcm', _('Repository Manager'))

    def render_admin_panel(self, req, cat, page, path_info):
        """
        Returns the admin view and handles the form actions
        """
        add_script(req, 'multiproject/js/admin_vcm.js')
        add_stylesheet(req, 'multiproject/css/vcm.css')
        data = {'multiproject': {
            'repositories':"GIT RULES!"
        }}
        req.perm.require('TRAC_ADMIN')
        return 'admin_vcm.html', data