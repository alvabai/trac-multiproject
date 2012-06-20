# -*- coding: utf-8 -*-
import re
from pkg_resources import resource_filename #@UnresolvedImport

from trac.perm import IPermissionRequestor
from trac.core import Component, implements
from trac.web import IRequestHandler
from trac.web.chrome import ITemplateProvider

from multiproject.common.membership.api import MembershipApi
from multiproject.common.projects import Projects
from multiproject.core.configuration import conf
from multiproject.core.permissions import CQDEUserGroupStore


class MembershipRequestModule(Component):
    """ Trac component for requesting membership
    """
    implements(IRequestHandler, ITemplateProvider, IPermissionRequestor)

    def get_permission_actions(self):
        return []

    def match_request(self, req):
        return re.match(r'/membership(?:_trac)?(?:/.*)?$', req.path_info)

    def process_request(self, req):
        req.perm.require('ALLOW_REQUEST_MEMBERSHIP')
        all_members = {}

        project = Projects().get_project(env_name = conf.resolveProjectName(self.env))
        ug = CQDEUserGroupStore(project.trac_environment_key)
        for member, group in ug.get_all_user_groups(): #@UnusedVariable
            all_members[member] = 1

        if req.authname in all_members.keys():
            type = "privilege"
        else:
            type = "membership"

        # Check the message length only if user has clicked 'request'
        msg_ok = 'request' not in req.args or ('message' in req.args and
            len(req.args.get('message')) >= 40)

        # If request, then make request, ow. show form
        if req.args.has_key('request') and msg_ok:
            return self.make_membership_request(req)
        else:
            return 'membership_request_form.html', {'type':type, 'msg_ok':msg_ok,
                                                    'message':req.args.get('message')}, None

    def make_membership_request(self, req):
        # Get project
        env_name = conf.resolveProjectName(self.env)
        project = Projects().get_project(env_name = env_name)

        # Make a request
        members = MembershipApi(self.env, project)
        members.request_membership(req.authname, req.args.get('message'))

        type = 'membership'
        if req.args.has_key('type'):
            type = req.args.get('type')

        return 'membership_requested.html', {'_project_':project, 'type':type}, None

    def get_templates_dirs(self):
        return [resource_filename('multiproject.project.membership', 'templates')]

    def get_htdocs_dirs(self):
        return []
