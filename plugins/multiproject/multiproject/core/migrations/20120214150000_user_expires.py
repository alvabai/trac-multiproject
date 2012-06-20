# -*- coding: utf-8 -*-
"""
Migration adds new columns:

- ``user.expires`` (defaults to now + 3 months for local users)
- ``user.author_id`` (defaults to None)

"""
from multiproject.core.db import admin_query, cursors
from multiproject.core.migration import MigrateBase, MigrateMgr


class UserExpiresField(MigrateBase):

    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = __doc__

    def upgrade(self):
        if self.applied():
            print "Migration already applied".rjust(12)
            return True

        # Add columns expires & author_id and
        # set expire date three months from now for local users
        queries = ["""
        ALTER TABLE user
        ADD COLUMN `expires` DATETIME DEFAULT NULL AFTER `created`
        """, """
        ALTER TABLE user
        ADD COLUMN author_id int(10) unsigned DEFAULT NULL AFTER `expires`
        """, """
        UPDATE user
        LEFT JOIN authentication AS auth ON auth.id = user.authentication_key
        SET expires = (NOW() + INTERVAL 3 MONTH)
        WHERE LOWER(auth.method) = 'localdb'
        """]

        return self.manager.db_upgrade(queries)

    def downgrade(self):
        if not self.applied():
            print "Migration {0} not applied yet".format(__file__).rjust(12)
            return False

        queries = [
            "ALTER TABLE user DROP COLUMN expires",
            "ALTER TABLE user DROP COLUMN author_id"
        ]

        return self.manager.db_downgrade(queries)

    def applied(self):
        """
        Check if column exists or not
        :returns: True if exists, otherwise False
        """
        with admin_query(cursors.DictCursor) as cursor:
            cursor.execute('DESC user')
        return 'expires' in [row['Field'] for row in cursor]

MigrateMgr.instance().add(UserExpiresField())


