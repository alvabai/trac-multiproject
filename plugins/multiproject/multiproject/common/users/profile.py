# -*- coding: utf-8 -*-
"""
Module provides the in-place user profile information.
The actions listed in user profile box can be registered by the components implementing
the interface :py:class:`multiproject.common.users.api.IUserProfileActions`

.. note::

    This module returns pre-rendered HTML.
    If you're looking for JSON data, use ``/api/user?user_id=<uid>`` instead.
    :see:`multiproject.common.users.api`

"""
import pkg_resources
import re
import os

from trac.core import Component, implements, ExtensionPoint
from trac.env import open_environment
from trac.perm import PermissionCache
from trac.resource import Resource
from trac.ticket.query import Query
from trac.web.api import IRequestFilter
from trac.web.chrome import ITemplateProvider, IRequestHandler, _, tag, add_script, add_stylesheet

from multiproject.core.users import get_userstore
from multiproject.common.users.api import IUserProfileActions


# Regexp for getting username from request
MATCHREGX = re.compile(r'/user/(?P<username>[a-zA-Z0-9.@_ ]*)/profilebox$')


class UserProfileBox(Component):
    implements(IRequestHandler, ITemplateProvider, IUserProfileActions, IRequestFilter)
    profile_action_providers = ExtensionPoint(IUserProfileActions)

    # IRequestHandler methods

    def match_request(self, req):
        return req.path_info.endswith('/profilebox')

    def process_request(self, req):
        """
        Handles the profile box request, which is expected to be in format::

            /user/<username>/profilebox

        :returns:
            Pre-rendered user profile box HTML using templates:

            - multiproject_user_profilebox.html: To show the content
            - multiproject_user_profilebox_default.html: In a case of failures, missing data etc
        """
        # Read and validate arguments
        #account_id = req.args.get('user_id', None)
        #account_username = req.args.get('username', None)

        match = MATCHREGX.match(req.path_info)
        if not match:
            msg = _('Account cannot be found')
            return 'multiproject_user_profilebox_default.html', {'msg': msg}, False

        # Load specified account
        userstore = get_userstore()
        account = userstore.getUser(match.group('username'))
        if not account:
            msg = _('Account cannot be found')
            return 'multiproject_user_profilebox_default.html', {'msg': msg}, False

        # Check if user has USER_VIEW permission to view other users in home project
        homeperm = self._get_home_perm(req)
        if req.authname != account.username and 'USER_VIEW' not in homeperm:
            msg = _('Access denied')
            return 'multiproject_user_profilebox_default.html', {'msg': msg}, False

        # Load registered actions
        actions = []
        for aprovider in self.profile_action_providers:
            # Iterate actions and validate them
            for new_action in aprovider.get_profile_actions(req, account):
                # Ensure each action is in tuple format: (order, fragment)
                if not isinstance(new_action, tuple):
                    new_action = (0, new_action)
                # Add to list
                actions.append(new_action)

        # Sort the actions by hints given in actions:
        # the smaller the value, the higher the priority
        actions.sort(key=lambda tup: tup[0])

        # Construct list items: put first and class values
        litems = []
        llen = len(actions)
        for index, action in enumerate(actions):
            classes = []
            # If last
            if index == 0:
                classes.append('first')
            if llen == index + 1:
                classes.append('last')

            litems.append(tag.li(action[1], **{'class': ' '.join(classes)}))

        # If empty, put empty list element in place for easier styling
        if not litems:
            litems.append(tag.li('li', **{'class':'first last'}))

        # Pass data to template. Generate ul/li list from registered actions
        data = {
            'account':account,
            'actionlist':tag.ul(*litems)
        }

        return 'multiproject_user_profilebox.html', data, False

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        return [('multiproject', pkg_resources.resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        return [pkg_resources.resource_filename('multiproject.common.users', 'templates')]

    # IUserProfileActions

    def get_profile_actions(self, req, user):
        """
        Return list of actions
        """
        actions = []
        homeperm = self._get_home_perm(req)
        uresource = Resource('user', user.id)

        # Project settings for own account
        if user.username == req.authname:
            actions.append((-40, tag.a(_('View your projects'), href=homeperm.env.href('myprojects'))))
            actions.append((0, tag.a(_('Edit your settings'), href=homeperm.env.href('prefs'))))
        # View other user profile
        else:
            actions.append((-50, tag.a(_('View service profile'), href=homeperm.env.href('user', user.username))))

        # If user can fully manage account
        if homeperm.has_permission('USER_EDIT', uresource):
            label = 'Manage your account' if user.username == req.authname else 'Manage account'
            actions.append((-2, tag.a(_(label), href=homeperm.env.href('admin/users/manage', username=user.username))))

        # Tickets assigned to or created by user (if component is enabled and user has permissions to view them)
        # Note: href.kwargs cannot be used because of reserved word 'or' and un-ordered nature of dict
        if (self.env.is_component_enabled('trac.ticket.query.QueryModule') or
            self.env.is_component_enabled('multiproject.project.tickets.viewtickets.QueryModuleInterceptor')) \
            and 'TICKET_VIEW' in req.perm:
            qstring = 'owner={0}&or&reporter={0}&group=status'.format(user.username)
            query = Query.from_string(self.env, qstring)
            actions.append((5, (tag.a(_('View tickets'), href=query.get_href(req.href)))))

        return actions

    def _get_home_perm(self, req):
        """
        Returns permission cache from home environment
        """
        home_env = open_environment(os.path.join(
            self.env.config.get('multiproject', 'sys_projects_root'),
            self.env.config.get('multiproject', 'sys_home_project_name')),
            use_cache=True
        )
        return PermissionCache(home_env, req.authname)

    # IRequestFilter methods

    def pre_process_request(self, req, handler):
        """
        Process request to add some data in request
        """
        return handler

    def post_process_request(self, req, template, data, content_type):
        """
        Add global javascript data on post-processing phase
        """
        # When processing template, add global javascript json into scripts
        if template:
            add_stylesheet(req, 'multiproject/css/multiproject.css')
            add_script(req, 'multiproject/js/multiproject.js')
            add_script(req, 'multiproject/js/profile.js')

        return template, data, content_type