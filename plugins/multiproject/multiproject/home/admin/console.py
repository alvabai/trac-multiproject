# -*- coding: utf-8 -*-
"""
Module implements trac-admin commands related to home project functionality
"""
from datetime import datetime
from trac.core import *
from trac.admin import IAdminCommandProvider
from trac.util.text import print_table

from multiproject.core.configuration import conf


class HomeUserAdminCommandProvider(Component):

    implements(IAdminCommandProvider)

    # IAdminCommandProvider methods

    def get_admin_commands(self):
        yield ('mp user list expired', '<when:YYYY-MM-DD>',
               'Print list expired or soon to be expiring users. Optional date argument to check from future: YYYY-MM-DD',
               None, self._list_expired)

    def _list_expired(self, when=None):
        # Parse optional date argument
        when = when if when is None else datetime.strptime(when, '%Y-%m-%d')

        userstore = conf.getUserStore()
        users = [(user.username, user.expires) for user in userstore.get_expired_users(when=when)]

        print_table(users, ('User', 'Expires'))

