# -*- coding: utf-8 -*-
"""
Module contains components for message administration.
Component introduces new permissions:

- MESSAGE_VIEW: User can view messages

  - When set to home project env: Can view messages sent to home project
  - When set to project env: Can view messages sent to project env

- MESSAGE_CREATE: User can send messages

  - When set to home project env: Private message to anyone
  - When set to project env: Project wide message specific to project

"""
from datetime import datetime, timedelta

from trac.admin import IAdminCommandProvider
from trac.core import Component, implements
from trac.perm import IPermissionRequestor
from trac.util.text import printout

from multiproject.core.db import cursors, admin_query
from multiproject.common.messages.api import MessageService


class MessagesAdminPanel(Component):
    implements(IPermissionRequestor, IAdminCommandProvider)

    # IPermissionRequestor methods

    def get_permission_actions(self):
        """
        Introduces new permissions
        """
        return ['MESSAGE_VIEW', 'MESSAGE_CREATE']

    # IAdminCommandProvider methods

    def get_admin_commands(self):
        yield ('mp message purge', '<days:old>',
               'Delete messages older than given days. Defaults to 30',
               None, self._do_message_purge)

    def _do_message_purge(self, days=30):
        """
        Do the actual purge
        :param days: Delete messages older than given number of days
        """
        sql = '''
        SELECT id FROM message WHERE created < SUBDATE(NOW(), INTERVAL %s DAY)
        '''

        if isinstance(days, basestring):
            days = int(days)

        # NOTE: Use MessageService to delete the messages so that all the listeners and related actions are run
        ms = self.env[MessageService]
        before = datetime.utcnow() - timedelta(days=int(days))

        with admin_query(cursors.DictCursor) as cursor:
            cursor.execute(sql, days)
            message_ids = [row['id'] for row in cursor.fetchall()]
            ms.delete_messages(user_id=None, message_ids=message_ids, only_hide=False)

            printout('Messages purged before %s: %d' % (before.strftime('%Y-%m-%d'), cursor.connection.affected_rows()))