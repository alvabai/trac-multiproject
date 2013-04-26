# -*- coding: utf-8 -*-
import urllib

from trac.core import Component, implements
from trac.web.api import IRequestFilter

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
        repository_name = None
        conf.log.exception("Path length: %s" % len(req.path_info.split("/")))
        if len(req.path_info.split("/")) > 2:
            repository_name = req.path_info.split("/")[-1]
        conf.log.exception("Repo name: %s" % repository_name)
        if template == 'browser.html':
            username = urllib.quote(req.authname)
            if repository_name:
                scm_type = repository_name + ".type"
                scm = self.env.config.get('repositories', scm_type)
            else:
                scm = self.env.config.get('trac', 'repository_type')

            project = Project.get(self.env)

            names = {'git':'GIT', 'svn':'Subversion', 'hg':'Mercurial'}
            cmd_kinds = {'git':'Clone', 'hg':'Clone', 'svn':'Check out'}

            type = names[scm]
            schemes = self.protocols(project, scm)

            data['kinds'] = cmd_kinds
            data['schemes'] = schemes
            data['name'] = names[scm]
            data['type'] = scm

            co_commands = {}
            for scheme in schemes:
                co_commands[scheme] = self.create_co_command(scm, username, scheme, repository_name)
            data['co_commands'] = co_commands

        return template, data, content_type

    def protocols(self, project, scm):
        protocol_manager = ProtocolManager(project.id)
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
        co_commands['git'] = 'git clone %(scheme)s://%(domain)s/%(project)s/%(scm)s/%(repository_name)s'
        co_commands['gitssh'] = 'git clone %(scheme)s://git@%(domain)s/%(project)s/%(scm)s/%(repository_name)s'
        co_commands['svn'] = 'svn co %(scheme)s://%(domain)s/%(project)s/%(scm)s/%(repository_name)s'
        co_commands['hg'] = 'hg clone %(scheme)s://%(domain)s/%(project)s/%(scm)s/%(repository_name)s'

        return co_commands[scm] % params
