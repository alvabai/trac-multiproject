# -*- coding: utf-8 -*-
import sys
import os
from trac.core import Component, implements, ExtensionPoint
from trac.mimeview.api import Context
from trac.util.translation import _
from trac.admin.api import IAdminPanelProvider
from trac.web.api import Href, RequestDone
from trac.web.chrome import add_warning, add_script, add_stylesheet
from multiproject.core.configuration import conf
from multiproject.common.projects.commands import CreateTracVersionControl
from multiproject.common.projects.project import Project

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
        conf.log.exception("args: %s" % req.args)
        if req.method == 'POST':
            if req.args.get("repos[]"):
                self.delete(req.args.get("repos[]"))
            elif req.args.get("repo_name") and req.args.get("repo_type"):
                self.add_repository(req.args.get("repo_name"), req.args.get("repo_type"))
        repos = self.get_repositories()
        vcs_types = self.get_enabled_vcs(self.env)
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

    def delete(self, repos):
        conf.log.exception("delete_repos: %s" % repos)
        if not repos:
            return
        if repos is list:
            for repo in repos:
                to_delete = repo.split('#')
                self.delete_repo(to_delete[1], to_delete[0])
        else:
            to_delete = repos.split('#')
            self.delete_repo(to_delete[1], to_delete[0])

    def delete_repo(self, repo_type, name):
        path = conf.getEnvironmentVcsPath(self.env.project_identifier, repo_type, name)
        inifile = conf.getEnvironmentConfigPath(self.env.project_identifier)
        # FIXME
        conf.remove_item_from_section(inifile, 'repositories', name + '.dir')
        conf.remove_item_from_section(inifile, 'repositories', name + '.type')
        path2 = path + '.deleted.0'
        i = 0
        while os.path.exists(path2):
            i = i + 1
            path2 = path + '.deleted.' + i
        os.rename(path, path2)

    def add_repository(self, name, repo_type):
        project = Project._get_project(env_name=self.env.project_identifier, use_cache=False)
        ctvc = CreateTracVersionControl(project, {'vcs_type':repo_type, 'vcs_name':name})
        ctvc.do()
        self.env.config.set('repositories', name + '.dir', 
                            conf.getEnvironmentVcsPath(self.env.project_identifier, repo_type, name))
        self.env.config.set('repositories', name + '.type', repo_type)
        self.env.config.save()

    def get_enabled_vcs(self, env):
        """ This function checks from the trac configuration
        what scm systems are enabled.
        """
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
