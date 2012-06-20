# -*- coding: utf-8 -*-
"""
Migration adds new field: ``user.created``
"""
from multiproject.core.db import admin_query, cursors
from multiproject.core.migration import MigrateBase, MigrateMgr


class UserCreationField(MigrateBase):

    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = __doc__

    def upgrade(self):
        if self.applied():
            print "Migration already applied".rjust(12)
            return True

        queries = ["""
        ALTER TABLE user
        ADD COLUMN created DATETIME DEFAULT NULL
        """]

        return self.manager.db_upgrade(queries)

    def downgrade(self):
        if not self.applied():
            print "Migration {0} not applied yet".format(__file__).rjust(12)
            return False

        queries = ["""
        ALTER TABLE user
        DROP COLUMN created
        """]

        return self.manager.db_downgrade(queries)

    def applied(self):
        """
        Check if column exists or not
        :returns: True if exists, otherwise False
        """
        with admin_query(cursors.DictCursor) as cursor:
            cursor.execute('DESC user')
        return 'created' in [row['Field'] for row in cursor]

MigrateMgr.instance().add(UserCreationField())


