# -*- coding: utf-8 -*-
"""
Drops the icon_id from the ``global_announcements`` table.

TODO: Maybe the global_announcement should be maintained with the tracdiscussion plugin instead?
"""
from multiproject.core.db import admin_query
from multiproject.core.migration import MigrateBase, MigrateMgr


class DropGlobalAnnouncementIcon(MigrateBase):
    """
    Dumps the project icons blobs into filesystem
    """
    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = self.__doc__

    def upgrade(self):
        """
        Run DB upgrade steps
        """
        if self.applied():
            return True

        queries = ['''
        ALTER TABLE global_announcements
        DROP COLUMN `icon_id`
        ''']
        return self.manager.db_upgrade(queries)

    def downgrade(self):
        """
        Do downgrade steps.

        .. WARNING::

            This does not restore the data, only the column.

        """
        if not self.applied():
            return False

        queries = ['''
        ALTER TABLE `global_announcements`
        ADD COLUMN `icon_id` int(10) unsigned DEFAULT NULL
        AFTER `topic_id`
        ''']
        return self.manager.db_downgrade(queries)

    def applied(self):
        """
        Check if migration is already applied or not
        :returns: True if migrated, otherwise False
        """
        # Test if icon_id column still exists: Exception = migration already applied
        with admin_query() as cursor:
            try:
                cursor.execute('SELECT icon_id FROM global_announcements')
            except Exception:
                return True

        return False


MigrateMgr.instance().add(DropGlobalAnnouncementIcon())


