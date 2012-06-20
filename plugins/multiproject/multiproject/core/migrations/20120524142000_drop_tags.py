# -*- coding: utf-8 -*-
"""
Drops the project tags tables.
"""
from multiproject.core.db import admin_query
from multiproject.core.migration import MigrateBase, MigrateMgr
from multiproject.core.configuration import Configuration


class DropProjectTags(MigrateBase):

    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = __doc__

    def upgrade(self):
        if self.applied():
            print "Migration already applied".rjust(12)
            return True

        queries = ["DROP TABLE `project_tags`", "DROP TABLE `tags`"]
        return self.manager.db_upgrade(queries)

    def downgrade(self):
        if not self.applied():
            print "Migration hasn't been applied."
            return False

        queries = [
            '''
            CREATE TABLE `tags` (
                `tag_id` MEDIUMINT(8) UNSIGNED NOT NULL AUTO_INCREMENT,
                `tag_name` VARCHAR(64) NOT NULL COLLATE 'utf8_bin',
                `tag_count` MEDIUMINT(8) UNSIGNED NOT NULL,
                PRIMARY KEY (`tag_id`),
                UNIQUE INDEX `tagname_idx` (`tag_name`)
            )
            COMMENT='List of tags'
            COLLATE='utf8_bin'
            ENGINE=InnoDB
            ROW_FORMAT=DEFAULT
            ''',
            '''
            CREATE TABLE `project_tags` (
                `project_key` INT(10) UNSIGNED NOT NULL,
                `tag_key` MEDIUMINT(8) UNSIGNED NOT NULL,
                PRIMARY KEY (`project_key`, `tag_key`),
                INDEX `new_fk_constraint2` (`tag_key`),
                CONSTRAINT `new_fk_constraint` FOREIGN KEY (`project_key`) REFERENCES `projects` (`project_id`) ON UPDATE CASCADE ON DELETE CASCADE,
                CONSTRAINT `new_fk_constraint2` FOREIGN KEY (`tag_key`) REFERENCES `tags` (`tag_id`) ON UPDATE CASCADE ON DELETE CASCADE
            )
            COLLATE='utf8_bin'
            ENGINE=InnoDB
            ROW_FORMAT=DEFAULT
            ''']

        return self.manager.db_downgrade(queries)

    def applied(self):
        """
        Check if column exists or not
        :returns: True if exists, otherwise False
        """
        conf = Configuration.instance()
        with admin_query() as cursor:
            cursor.execute('''
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = '{0}'
                AND table_name = 'tags'
            '''.format(conf.db_admin_schema_name))
            return cursor.rowcount != 1

MigrateMgr.instance().add(DropProjectTags())


