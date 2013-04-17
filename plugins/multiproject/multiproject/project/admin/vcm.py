# -*- coding: utf-8 -*-
import sys
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
        vcs_types = self.get_enabled_vcs(self.env)
        conf.log.exception("VCS types: %s" % vcs_types)
        add_script(req, 'multiproject/js/admin_vcm.js')
        add_stylesheet(req, 'multiproject/css/vcm.css')
        data = {
            'repositories':repos,
            'repository_types':vcs_types
        }
        
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

    def get_enabled_vcs(self, env):
        """ This function checks from the trac configuration
        what scm systems are enabled.
        """
        # FIXME: Home environment should not have any scm systems enabled
        #        this function should simply return a list from configuration
        vcsi = {}
        vcs_list = []
        from trac.core import ComponentMeta
        for component in ComponentMeta._components:
            module = sys.modules[component.__module__].__name__
            module = module.lower()
            if env.is_component_enabled(component):
                if module.startswith('tracext.git.') and 'git' not in vcsi.keys():
                    vcs_list.append({ 'name': 'GIT', 'id': 'git' })
                    vcsi['git'] = 1
                elif module.startswith('tracext.hg.') and 'hg' not in vcsi.keys():
                    vcs_list.append({ 'name': 'Mercurial', 'id': 'hg' })
                    vcsi['hg'] = 1
                elif module.startswith('tracbzr.') and 'bzr' not in vcsi.keys():
                    vcs_list.append({ 'name': 'Bazaar', 'id': 'bzr' })
                    vcsi['bzr'] = 1
                elif module.startswith('tracext.perforce.') and 'pf' not in vcsi.keys():
                    vcs_list.append({ 'name': 'Perforce', 'id': 'pf' })
                    vcsi['pf'] = 1

        return vcs_list
