# -*- coding: utf-8 -*-
"""
Removes ``insider`` column from ``user`` table
"""
from multiproject.core.db import admin_query
from multiproject.core.migration import MigrateBase, MigrateMgr


class DropInsiderColumn(MigrateBase):
    """
    Removes ``insider`` column from ``user`` table
    """
    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = self.__doc__
        self.pretend_to_be_not_applied = False

    def upgrade(self):
        """
        Runs the upgrade queries
        """
        if self.applied():
            return

        queries = ['ALTER TABLE user DROP COLUMN `insider`']
        return self.manager.db_upgrade(queries)

    def downgrade(self):
        """
        Runs the downgrade queries
        """
        queries = ['ALTER TABLE `user` ADD COLUMN `insider` tinyint(1) NOT NULL DEFAULT 0 AFTER `SHA1_PW`']
        return self.manager.db_upgrade(queries)

    def applied(self):
        """
        Check if migration is already applied
        :return: True if already applied, otherwise False
        """
        with admin_query() as cursor:
            try:
                cursor.execute('SELECT insider FROM user')
            # Failure means no column
            except Exception:
                return True
        return False


MigrateMgr.instance().add(DropInsiderColumn())
