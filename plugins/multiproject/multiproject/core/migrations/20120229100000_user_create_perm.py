# -*- coding: utf-8 -*-
"""
Migration adds new columns:

- ``user.expires`` (defaults to now + 3 months for local users)
- ``user.author_id`` (defaults to None)

"""
from multiproject.core.db import admin_query, cursors
from multiproject.core.migration import MigrateBase, MigrateMgr


class UserPermissionRename(MigrateBase):

    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = __doc__

    def upgrade(self):
        if self.applied():
            print "Migration already applied".rjust(12)
            return True

        # Remove USER_CREATE action if it is already there
        # Rename ADMIN_CREATE_USER => USER_CREATE
        queries = ["""
        DELETE FROM action WHERE action_string = 'USER_CREATE'
        """, """
        UPDATE action
        SET action_string = 'USER_CREATE'
        WHERE action_string = 'ADMIN_CREATE_USER'
        """]

        return self.manager.db_upgrade(queries)

    def downgrade(self):
        if not self.applied():
            print "Migration {0} not applied yet".format(__file__).rjust(12)
            return False

        queries = ["""
        UPDATE action
        SET action_string = 'ADMIN_CREATE_USER'
        WHERE action_string = 'USER_CREATE'
        """]

        return self.manager.db_downgrade(queries)

    def applied(self):
        """
        Check if column exists or not
        :returns: True if exists, otherwise False
        """
        count = 0
        with admin_query(cursors.DictCursor) as cursor:
            cursor.execute('SELECT COUNT(action_id) AS count FROM action WHERE action_string = "ADMIN_CREATE_USER"')
            count = int(cursor.fetchone()['count'])

        return count == 0

MigrateMgr.instance().add(UserPermissionRename())


