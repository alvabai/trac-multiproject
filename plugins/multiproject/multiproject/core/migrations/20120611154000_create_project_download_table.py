# -*- coding: utf-8 -*-
"""
Migration to add project download tables.

mysql> desc project_download;
+---------------+----------------------+------+-----+---------+----------------+
| Field         | Type                 | Null | Key | Default | Extra          |
+---------------+----------------------+------+-----+---------+----------------+
| id            | int(10) unsigned     | NO   | PRI | NULL    | auto_increment |
| project_id    | int(10) unsigned     | NO   | MUL | NULL    |                |
| download_path | text                 | NO   |     | NULL    |                |
| version       | smallint(5) unsigned | NO   |     | NULL    |                |
| uploader_id   | int(10) unsigned     | NO   | MUL | NULL    |                |
| hash          | varchar(64)          | NO   |     | NULL    |                |
| size          | int(10)              | NO   |     | NULL    |                |
| created       | bigint(20) unsigned  | YES  |     | NULL    |                |
| changed       | bigint(20) unsigned  | YES  |     | NULL    |                |
| count         | int(10) unsigned     | NO   |     | 0       |                |
| description   | text                 | NO   |     | NULL    |                |
| platform      | text                 | NO   |     | NULL    |                |
| status        | tinyint(3) unsigned  | NO   |     | NULL    |                |
+---------------+----------------------+------+-----+---------+----------------+
13 rows in set (0.00 sec)

"""

from multiproject.core.db import admin_query
from multiproject.core.migration import MigrateBase, MigrateMgr
from multiproject.core.configuration import conf


class CreateProjectDownloadTable(MigrateBase):
    """
    Migration to create project download tables into trac_admin database. The tables are
    used to store meta-information about the downloads.
    """
    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = self.__doc__

    def upgrade(self):
        if self.applied():
            print "project_download table is already in database"
            return True

        queries = [
        '''
        CREATE TABLE `project_download` (
            `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `project_id` INT(10) UNSIGNED NOT NULL,
            `download_path` TEXT NOT NULL COLLATE 'utf8_bin',
            `version` SMALLINT UNSIGNED NOT NULL,
            `uploader_id` INT(10) UNSIGNED NOT NULL,
            `hash` VARCHAR(64) NOT NULL COLLATE 'utf8_bin',
            `size` INT(10) NOT NULL,
            `created` BIGINT(20) UNSIGNED DEFAULT NULL,
            `changed` BIGINT(20) UNSIGNED DEFAULT NULL,
            `count` INT(10) UNSIGNED NOT NULL DEFAULT 0,
            `description` TEXT NOT NULL COLLATE utf8_bin,
            `platform` TEXT NOT NULL COLLATE utf8_bin,
            `status` TINYINT(3) UNSIGNED NOT NULL,
            PRIMARY KEY (`id`),
            UNIQUE INDEX `uniq_download_version` (`project_id`, `download_path`(255), `version`),
            INDEX `user_fk` (`uploader_id`),
            CONSTRAINT `project_fk` FOREIGN KEY (`project_id`) REFERENCES `projects` (`project_id`) ON UPDATE CASCADE ON DELETE CASCADE,
            CONSTRAINT `user_fk` FOREIGN KEY (`uploader_id`) REFERENCES `user` (`user_id`) ON UPDATE CASCADE ON DELETE CASCADE
        ) DEFAULT CHARSET=utf8 COLLATE='utf8_bin' ENGINE=InnoDB;
        ''']

        return self.manager.db_upgrade(queries)

    def downgrade(self):
        if not self.applied():
            print "project_download table is not in database"
            return True

        queries = [
            'DROP TABLE `project_download`',
            ]
        return self.manager.db_downgrade(queries)

    def applied(self):
        with admin_query() as cursor:
            cursor.execute('''
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = %s
                AND table_name = 'project_download'
            ''', conf.db_admin_schema_name)
            if cursor.rowcount != 1:
                return False

        return True


MigrateMgr.instance().add(CreateProjectDownloadTable())
