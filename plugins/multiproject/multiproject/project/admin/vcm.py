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
        req.perm.require('TRAC_ADMIN')
        repos = self.get_repositories()
        add_script(req, 'multiproject/js/admin_vcm.js')
        add_stylesheet(req, 'multiproject/css/vcm.css')
        data = {'multiproject': {
            'repositories':"GIT RULES!"
        }}
        
        return 'admin_vcm.html', data

    def get_repositories(self):
        raw_data = self.config.options('repositories')
        repos = []
        for option in raw_data:
            if option[0].endswith('.type'):
                temp = []
                temp.append(option[0].split('.')[0])
                temp.append(option[1])
                repos.append(temp)
        return repos

    def create_new_repository(self, repo_name, repo_type):
        pass
