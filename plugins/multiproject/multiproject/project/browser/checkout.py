# -*- coding: utf-8 -*-
import urllib

from trac.core import Component, implements
from trac.web.api import IRequestFilter
from trac.web.chrome import add_script

from multiproject.common.projects import Project
from multiproject.core.configuration import conf
from multiproject.core.proto import ProtocolManager


class BrowserModifyModule(Component):
    """
    Adds checkout commands to browser
    """

    implements(IRequestFilter)

    def pre_process_request(self, req, handler):
        return handler

    def post_process_request(self, req, template, data, content_type):
        #add_script(req, 'multiproject/js/browser.js')
        repository_name = None
        data_repositories = None
        conf.log.exception("Path length: %s" % len(req.path_info.split("/")))
        if len(req.path_info.split("/")) > 2:
            #Get repository name from path_info
            repository_name = req.path_info.split("/")[2]
        conf.log.exception("Repo name: %s" % repository_name)
        if template == 'browser.html':
            username = urllib.quote(req.authname)
            project = Project.get(self.env)
            schemes = None
            if repository_name:
                scm_type = repository_name + ".type"
                scm_dir = repository_name + ".dir"
                scm = self.env.config.get('repositories', scm_type)
                repository_name = self.env.config.get('repositories', scm_dir).split("/")[-1]
                schemes = self.protocols(project.id, scm)
            else:
                scm = self.env.config.get('trac', 'repository_type')
                schemes = self.protocols(project.id, scm)
                data_repo_names = self.get_repositories()
                if len(data_repo_names) > 0:
                    data_repositories = []
                    for repo in data_repo_names:
                        type_scheme = []
                        for data_scheme in self.protocols(project.id, repo[1]):
                            type_scheme.append(self.create_co_command(repo[1], username, data_scheme, repo[0]))
                        data_repositories.append(type_scheme)

            

            names = {'git':'GIT', 'svn':'Subversion', 'hg':'Mercurial'}
            cmd_kinds = {'git':'Clone', 'hg':'Clone', 'svn':'Check out'}

            type = names[scm]
            

            data['kinds'] = cmd_kinds
            data['schemes'] = schemes
            data['name'] = names[scm]
            data['type'] = scm
            data['data_repositories'] = data_repositories

            co_commands = {}
            for scheme in schemes:
                co_commands[scheme] = self.create_co_command(scm, username, scheme, repository_name)
            data['co_commands'] = co_commands

        return template, data, content_type

    def protocols(self, project_id, scm):
        protocol_manager = ProtocolManager(project_id)
        allowed = protocol_manager.allowed_protocols(scm)

        schemes = []
        for proto in ProtocolManager.available_schemes(scm):
            if proto in allowed:
                schemes.append(proto)
        return schemes

    def create_co_command(self, scm, username, scheme, repository_name):
        if scheme == 'ssh':
            scm = 'gitssh'

        params = {'scheme': scheme,
                  'username': username,
                  'domain': conf.domain_name,
                  'scm': scm,
                  'project': conf.resolveProjectName(self.env),
                  'repository_name': repository_name}

        # username was taken from use because of problems resolving nokia account id
        co_commands = {}
        co_commands['git'] = 'git clone %(scheme)s://%(domain)s/%(project)s/git/%(repository_name)s'
        co_commands['gitssh'] = 'git clone %(scheme)s://git@%(domain)s/%(project)s/git/%(repository_name)s'
        co_commands['svn'] = 'svn co %(scheme)s://%(domain)s/%(project)s/%(scm)s/%(repository_name)s'
        co_commands['hg'] = 'hg clone %(scheme)s://%(domain)s/%(project)s/%(scm)s/%(repository_name)s'

        return co_commands[scm] % params

    def get_repositories(self):
        raw_data = self.config.options('repositories')
        repos = []
        for option in raw_data:
            if option[0].endswith('.dir'):
                temp = []
                temp.append(option[1].split('/')[-1])
                temp.append(option[1].split('/')[-2])
                repos.append(temp)
        return repos
