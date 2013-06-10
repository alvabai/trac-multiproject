# -*- coding: utf-8 -*-
import sys
import re
import os
from trac.core import Component, implements, ExtensionPoint
from trac.mimeview.api import Context
from trac.util.translation import _
from trac.admin.api import IAdminPanelProvider
from trac.web.api import Href, RequestDone
from trac.web.chrome import add_warning, add_script, add_stylesheet, add_notice
from multiproject.core.configuration import conf
from multiproject.common.projects.commands import CreateTracVersionControl, InitCommitHooks
from multiproject.common.projects.project import Project


class RepositoriesAdminPanel(Component):
    implements(IAdminPanelProvider)

    def get_admin_panels(self, req):
        if 'TRAC_ADMIN' in req.perm:
            yield ('general', _('General'), 'vcm', _('Repository Manager'))

    def render_admin_panel(self, req, cat, page, path_info):
        """
        Returns the admin view and handles the form actions
        """
        req.perm.require('TRAC_ADMIN')
        if req.method == 'POST':
            if req.args.get("repos[]"):
                self.delete(req.args.get("repos[]"))
                url = "/admin/general/vcm"
                req.redirect(req.href(url))
            elif req.args.get("repo_name") and req.args.get("repo_type"):
                self.add_repository(req.args.get("repo_name"), req.args.get("repo_type"), req)
        add_script(req, 'multiproject/js/admin_vcm.js')
        add_stylesheet(req, 'multiproject/css/vcm.css')
        vcs_types = self.get_enabled_vcs(self.env)
        repos = self.get_repositories()
        data = {
            'repositories':repos,
            'repository_types':vcs_types
        }
        
        return 'admin_vcm.html', data

    def get_repositories(self):
        raw_data = self.env.config.options('repositories')
        repos = []
        for option in raw_data:
            if option[0].endswith('.dir'):
                temp = []
                temp.append(option[1].split('/')[-1])
                temp.append(option[1].split('/')[-2])
                repos.append(temp)
        return repos

    def delete(self, repos):
        if not repos:
            return []
        if type(repos) == list:
            for repo in repos:
                to_delete = repo.split('#')
                self.delete_repo(to_delete[1], to_delete[0])
        else:
            to_delete = repos.split('#')
            self.delete_repo(to_delete[1], to_delete[0])

    def delete_repo(self, repo_type, name):
        path = self.conf.getEnvironmentVcsPath(self.env.project_identifier, repo_type, name)
        inifile = self.conf.getEnvironmentConfigPath(self.env.project_identifier)
        self.conf.remove_item_from_section(inifile, 'repositories', name + '.dir')
        self.conf.remove_item_from_section(inifile, 'repositories', name + '.type')
        path2 = path + '.deleted.0'
        i = 0
        while os.path.exists(path2):
            i = i + 1
            path2 = path + '.deleted.' + i
        os.rename(path, path2)

    def add_repository(self, name, repo_type, req):
        premade_repositories = self.get_repositories()
        for repo in premade_repositories:
            if name.lower() in repo[0].lower():
                return add_warning(req, _("Repository name reserved"))
        if not self.validate_repository_name(name):
            return add_warning(req, _("Repository adding failed. Check name."))
        project = Project._get_project(env_name=self.env.project_identifier, use_cache=False)
        ctvc = CreateTracVersionControl(project, {'vcs_type':repo_type, 'vcs_name':name})
        ctvc.do()
        add_hook = InitCommitHooks(project, {'vcs_type':repo_type, 'vcs_name':name})
        add_hook.do()
        self.env.config.set('repositories', name + '.dir', 
                            self.conf.getEnvironmentVcsPath(self.env.project_identifier, repo_type, name))
        self.env.config.set('repositories', name + '.type', repo_type)
        self.env.config.save()
        add_notice(req, _('Added new repository %s to project' % name))

    def validate_repository_name(self, repository_name):
        check = True
        pattern = '^[a-zA-Z0-9-_]*$'
        if repository_name is None:
            check = False
        elif len(repository_name) < 3:
            check = False
        elif not (re.match(pattern,repository_name)):
            check = False
        elif repository_name == "git" or repository_name == "hg" or repository_name == "svn":
            check = False
        print "repo name: %s" % repository_name
        return check

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
