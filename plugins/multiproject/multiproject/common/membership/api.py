# -*- coding: utf-8 -*-
from pkg_resources import resource_filename

from trac.core import Component, implements, TracError
from trac.notification import NotifyEmail
from trac.web.chrome import ITemplateProvider

from multiproject.core.permissions import CQDEPermissionStore
from multiproject.core.configuration import conf
from multiproject.core.db import admin_query, admin_transaction, safe_string


class MembershipApi(object):
    def __init__(self, env, project):
        self.project = project
        self.env = env

    def get_membership_requests(self):
        """ Returns a list of usernames of users that have requested
            membership for this project
        """
        query = """
        SELECT user.username FROM membership_request
        INNER JOIN user ON user.user_id = membership_request.user_key
        WHERE project_key = %s
        """
        with admin_query() as cursor:
            try:
                cursor.execute(query, self.project.id)
                return [row[0] for row in cursor]
            except:
                conf.log.exception("Exception. MembershipApi.get_membership_requests query failed. '''%s'''" % query)

    def request_membership(self, authname, message):
        users = conf.getUserStore()
        user = users.getUser(authname)

        with admin_transaction() as cursor:
            query = "INSERT INTO membership_request VALUES(%s, %s)"
            try:
                cursor.execute(query, (self.project.id, user.id))
            except:
                conf.log.exception("Exception. MembershipApi.request_membership query failed. '''%s'''" % query)

        req_notifier = MembershipRequestedNotifier(self.env, self.project, message, authname)
        req_notifier.notify_admins()

    def accept_membership(self, username):
        """ Notifies user that he is accepted and removes membership
            request row from db
        """
        self._remove_membership_req(username)

        notifier = MembershipRequestHandledNotifier(self.env, self.project, username)
        notifier.notify_accepted()

    def decline_membership(self, username):
        """ Notifies user that he/she is not accepted in project
        """
        self._remove_membership_req(username)

        notifier = MembershipRequestHandledNotifier(self.env, self.project, username)
        notifier.notify_declined()

    def _remove_membership_req(self, username):
        users = conf.getUserStore()
        user = users.getUser(username)

        if not user:
            raise TracError('User cannot be found with name: "%s"' % username)

        query = """
        DELETE FROM membership_request
        WHERE project_key = %s AND user_key = %s
        """
        with admin_transaction() as cursor:
            try:
                cursor.execute(query, (self.project.id, user.id))
            except:
                conf.log.exception("Exception. MembershipApi._remove_membership_req query failed. '''%s'''" % query)


class MemberShipEmailTemplateProvider(Component):
    implements(ITemplateProvider)

    def get_templates_dirs(self):
        return [resource_filename('multiproject.common.membership', 'templates')]

    def get_htdocs_dirs(self):
        return []


class MembershipRequestedNotifier(NotifyEmail):
    """ Notifier for notifying project admins about new
        membership requests
    """
    template_name = "membership_request.txt"

    def __init__(self, env, project, message, authname):
        NotifyEmail.__init__(self, env)

        self.from_email = env.config.get('notification', 'smtp_from')
        add_auth_url = project.get_url() + "admin/permissions/groups"
        self.project = project

        self.data = {'project_name':project.project_name,
                     'message':message,
                     'authname':authname,
                     'add_auth_url':add_auth_url}

    def notify_admins(self):
        self.notify(None, "Request membership")

    def get_recipients(self, resid):
        """ List all admin emails in to field
        """
        cc = []
        to = []
        permissions = CQDEPermissionStore(self.project.trac_environment_key)
        admins = permissions.get_users_with_permissions(['TRAC_ADMIN'])

        # Wrap and escape admins in quotes
        recipients = ", ".join(["'%s'" % safe_string(admin) for admin in admins])

        # Query for admin email addresses
        with admin_transaction() as cursor:
            query = "SELECT mail FROM user WHERE username IN ({0})".format(recipients)
            try:
                cursor.execute(query)
                to = [row[0] for row in cursor]
            except:
                conf.log.exception("Exception. MembershipApi.get_recipients query failed. '''%s'''" % query)

        return to, cc


class MembershipRequestHandledNotifier(NotifyEmail):
    """ Notify user that his membership request is handled
    """
    template_name = "membership_handled.txt"

    def __init__(self, env, project, authname):
        NotifyEmail.__init__(self, env)

        self.from_email = env.config.get('notification', 'smtp_from')

        users = conf.getUserStore()
        self.user = users.getUser(authname)

        self.data = {'_project_':project}

    def notify_accepted(self):
        self.data['status'] = 'accepted'
        self.notify(None, "Membership accepted")

    def notify_declined(self):
        self.data['status'] = 'declined'
        self.notify(None, "Membership declined")

    def get_recipients(self, resid):
        return [self.user.mail], []
