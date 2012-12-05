# -*- coding: utf-8 -*-
"""
Migration to add global_announcements table.

mysql> desc global_announcements;
+------------------+------------------+------+-----+---------+-------+
| Field            | Type             | Null | Key | Default | Extra |
+------------------+------------------+------+-----+---------+-------+
| project_name     | varchar(64)      | NO   |     | NULL    |       |
| environment_name | varchar(32)      | NO   | PRI | NULL    |       |
| time             | bigint(20)       | NO   |     | 0       |       |
| subject          | text             | YES  |     | NULL    |       |
| author           | text             | YES  |     | NULL    |       |
| body             | text             | YES  |     | NULL    |       |
| topic_id         | int(10) unsigned | NO   |     | NULL    |       |
| icon_id          | int(10) unsigned | YES  |     | NULL    |       |
+------------------+------------------+------+-----+---------+-------+
"""

from multiproject.core.db import admin_query
from multiproject.core.migration import MigrateBase, MigrateMgr
from multiproject.core.configuration import Configuration


class CreateGlobalAnnouncementsTable(MigrateBase):
    """
    Migration to create global_announcements table into trac_admin database.
    The table is used to store the latest announcement per (public) project.
    """
    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = self.__doc__

    def upgrade(self):
        """
        Create global_announcements table into trac_admin database.
        """
        if self.applied():
            print "global_announcements table is already in database"
            return True

        queries = [
            '''
            CREATE TABLE `global_announcements` (
                `project_name` varchar(64) CHARACTER SET utf8 NOT NULL,
                `environment_name` varchar(32) COLLATE utf8_bin NOT NULL,
                `time` bigint(20) NOT NULL DEFAULT '0',
                `subject` text COLLATE utf8_bin,
                `author` text COLLATE utf8_bin,
                `body` text COLLATE utf8_bin,
                `topic_id` int(10) unsigned NOT NULL,
                `icon_id` int(10) unsigned DEFAULT NULL,
                PRIMARY KEY (`environment_name`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
            ''']

        return self.manager.db_upgrade(queries)

    def downgrade(self):
        """
        Remove the global_announcements table from trac_admin database.
        """
        if not self.applied():
            return False

        queries = [
            'DROP TABLE `global_announcements`'
        ]
        return self.manager.db_downgrade(queries)

    def applied(self):
        """
        Check if the global_announcements table already exist in trac_admin database.

        :returns: True if the table is there, False if it's not.
        """
        conf = Configuration.instance()

        with admin_query() as cursor:
            cursor.execute('''
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = '{0}'
                AND table_name = 'global_announcements'
            '''.format(conf.db_admin_schema_name))
            if cursor.rowcount != 1:
                return False

        return True


MigrateMgr.instance().add(CreateGlobalAnnouncementsTable())
