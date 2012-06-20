# -*- coding: utf-8 -*-
import string
from datetime import datetime, timedelta
from random import choice

from trac.admin.api import IAdminPanelProvider
from trac.core import Component, implements, TracError
from trac.web import chrome
from trac.util.translation import _
from trac.web.chrome import add_script, Markup, tag

from multiproject.common.notifications.email import EmailNotifier
from multiproject.core.configuration import conf
from multiproject.core.users import User


# Formatting rules for python and javascript: 25/01/12
DATEFORMATS = {
    'py':'%m/%d/%y',
    'js':'mm/dd/y'
}


class CreateLocalUserAdminPanel(Component):
    """ AdminPanel component for LDAP users creating a new user
    """
    implements(IAdminPanelProvider)

    def get_admin_panels(self, req):
        """ Introduce new component into admin panel navi
        """
        if 'USER_CREATE' in req.perm:
            yield ('users', 'Users', 'create_local', 'Create new user')

    def render_admin_panel(self, req, cat, page, path_info):
        """ Renders admin panel and handles new user creation request
        """
        req.perm.require('USER_CREATE')

        now = datetime.utcnow()
        expires = now + timedelta(days=90)
        data = {
            'dateformats':DATEFORMATS,
            'now':now,
            'expires':expires,
        }
        # Helper class
        add_script(req, 'multiproject/js/multiproject.js')
        add_script(req, 'multiproject/js/admin_user_create.js')

        # Get and set option goto address
        if 'goto' in req.args:
            req.session['goto'] = conf.safe_address(req.args.get('goto', ''))
            req.session.save()

        # Create new user to local database
        if req.method.upper() == 'GET':
            return 'admin_user_create.html', data

        elif req.method.upper() == 'POST':
            userstore = conf.getUserStore()
            user = self._get_user(req)
            author = userstore.getUser(req.authname)

            # Update data for pre-filled form
            data['username'] = user.username
            data['first'] = user.givenName
            data['last'] = user.lastName
            data['mail'] = user.mail
            data['mobile'] = user.mobile

            # Validate and set author
            if not req.perm.has_permission('USER_AUTHOR') or not author:
                chrome.add_warning(req, _("User needs to have author with USER_AUTHOR permission"))
                return 'admin_user_create.html', data
            user.author_id = author.id
            user.expires = expires

            # Validate user object
            error_msg = self.validate_user(req, user)
            if error_msg:
                chrome.add_warning(req, error_msg)
                return 'admin_user_create.html', data

            # Try to store user
            if userstore.storeUser(user):
                userlink = tag.a(user.username, href=req.href('admin/users/manage', username=user.username))
                chrome.add_notice(req, tag(_('Created new local user: '), userlink))
                self.log.info('Created new local user "%s" by "%s"' % (user.username, req.authname))

                # Try to send email notification also
                try:
                    self._send_notification(user)
                except TracError:
                    # Notification sending failed
                    self.log.exception("Notification sending failed")
                    chrome.add_warning(req, _('Failed to send email notification'))

                # Handle optional goto argument
                if 'goto' in req.session:
                    goto = req.session['goto']
                    del req.session['goto']

                    # NOTE: Show redirect address as a system message instead of direct redirection
                    # This is because after moving to another project, the system messages are not shown due the separate
                    # sessions per project
                    chrome.add_notice(req, Markup('Go back to: <a href="%s">%s</a>' % (goto, goto)))

                # Redirect to the page so that we're not showing the created user form with prefilled
                return req.redirect(req.href('admin/users/create_local'))

            return 'admin_user_create.html', data

    def _get_user(self, req):
        user = User()
        user.username = req.args.get('username')
        user.mail = req.args.get('email')
        user.givenName = req.args.get('first')
        user.lastName = req.args.get('last')
        user.password = self._generate_password()
        user.mobile = req.args.get('mobile')
        user.createIcon(req.args.get('icon'))

        # None makes it default (Local users)
        user.organization_key = None

        # FIXME: DEPRECATED: We should remove the insider flag
        user.insider = 0
        if req.args.get('insider') == 'on':
            user.insider = 1

        return user

    def validate_user(self, req, user):
        local_store = conf.getUserStore()
        if local_store.userExists(user.username):
            return 'User name already reserved'

        if not user.username:
            return 'User should have a username'

        if user.username.find(':') != -1 or user.username.find('%') != -1:
            return 'User name cannot contain characters: : %'

        if not user.mail:
            return 'User should have an e-mail address'

        if not user.lastName:
            return 'Last name required'

    def _generate_password(self):
        """
        Generates a random password:

        - Length: 10 character
        - Contains both letters and numbers

        :returns: Password
        :rtype: unicode
        """
        password = u''.join([choice(string.hexdigits) for i in range(10)])
        return password

    def _send_notification(self, user):
        """
        Send account information to new user

        :param User user:
        :raises: TracError if email sending fails
        """
        data = {
            'system':conf.domain_name,
            'username':user.username,
            'password':user.password,
            'expires':user.expires
        }
        enotify = EmailNotifier(self.env, "New user account created", data)
        enotify.template_name = "local_account_created.txt"
        enotify.notify(user.mail)

