# -*- coding: utf-8 -*-
"""
Migration to add ssh key tables to Collab.

mysql> desc ssh_keys;
+---------+------------------+------+-----+---------+----------------+
| Field   | Type             | Null | Key | Default | Extra          |
+---------+------------------+------+-----+---------+----------------+
| key_id  | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
| user_id | int(10) unsigned | NO   | MUL | NULL    |                |
| ssh_key | text             | NO   |     | NULL    |                |
| comment | varchar(200)     | YES  |     | NULL    |                |
| added   | datetime         | NO   |     | NULL    |                |
+---------+------------------+------+-----+---------+----------------+
5 rows in set (0.00 sec)

mysql> desc ssh_key_update;
+-----------+------------------+------+-----+---------+----------------+
| Field     | Type             | Null | Key | Default | Extra          |
+-----------+------------------+------+-----+---------+----------------+
| update_id | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
| added     | datetime         | NO   |     | NULL    |                |
+-----------+------------------+------+-----+---------+----------------+
2 rows in set (0.00 sec)
"""

from multiproject.core.db import admin_query
from multiproject.core.migration import MigrateBase, MigrateMgr
from multiproject.core.configuration import Configuration


class CreateSshKeysTables(MigrateBase):
    """
    Migration to create SSH key tables into trac_admin database. The tables are
    used to store ssh keys.
    """
    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = self.__doc__

    def upgrade(self):
        """
        Create two ssh related tables into trac_admin database.
        """
        if self.applied():
            print "ssh_keys and ssh_key_update tables are already in database"
            return True

        queries = [
        '''
        CREATE TABLE `ssh_keys` (
            `key_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `user_id` int(10) unsigned NOT NULL,
            `ssh_key` text COLLATE utf8_bin NOT NULL,
            `comment` varchar(200) COLLATE utf8_bin DEFAULT NULL,
            `added` datetime NOT NULL,
            PRIMARY KEY (`key_id`),
            KEY `fk_ssh_keys_to_user` (`user_id`),
            CONSTRAINT `fk_ssh_keys_to_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
        ''',
        '''
        CREATE TABLE `ssh_key_update` (
            `update_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `added` datetime NOT NULL,
            PRIMARY KEY (`update_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
        ''']

        return self.manager.db_upgrade(queries)

    def downgrade(self):
        """
        Remove the ssh keys related tables from trac_admin database.
        """
        if not self.applied():
            return False

        # Umm actually, this is a bad idea I think...
        queries = [
            'DROP TABLE `ssh_keys`',
            'DROP TABLE `ssh_key_update`'
            ]
        return self.manager.db_downgrade(queries)

    def applied(self):
        """
        Check if the ssh key related tables already exist in trac_admin database.

        :returns: True if the tables are there, False if they're not.
        """
        conf = Configuration.instance()

        with admin_query() as cursor:
            cursor.execute('''
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = '{0}'
                AND table_name = 'ssh_keys'
            '''.format(conf.db_admin_schema_name))
            if cursor.rowcount != 1:
                return False

            cursor.execute('''
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = '{0}'
                AND table_name = 'ssh_key_update'
            '''.format(conf.db_admin_schema_name))
            if cursor.rowcount != 1:
                return False

        return True


MigrateMgr.instance().add(CreateSshKeysTables())
