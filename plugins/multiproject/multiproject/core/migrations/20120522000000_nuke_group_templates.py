# -*- coding: utf-8 -*-
"""
Migration to remove group template procedures and tables from trac_admin database.
"""
from multiproject.core.db import admin_query
from multiproject.core.migration import MigrateBase, MigrateMgr
from multiproject.core.configuration import Configuration


class NukeGroupTemplates(MigrateBase):
    """
    Removes the group template procedures and tables from
    the trac_admin database. If downgrading, the procedure and tables with
    default data are created again.
    """

    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = self.__doc__

    def upgrade(self):
        """
        Upgrade implementation. Removes the procedure from database.
        """
        if self.applied():
            print "group templates already removed from database.".rjust(12)
            return True

        queries = [
            'DROP PROCEDURE `create_group_from_template`',
            'DROP PROCEDURE `get_all_template_permissions`',
            'DROP PROCEDURE `get_templates`',
            'DROP PROCEDURE `get_template_id`',
            'DROP PROCEDURE `add_permission_to_template`',
            'DROP TABLE `group_template_permission`',
            'DROP TABLE `group_template`',
        ]
        return self.manager.db_upgrade(queries)

    def downgrade(self):
        """
        Downgrade implementation, creates the procedures and tables into the database.
        """
        if not self.applied():
            return False

        queries = [
        '''
            CREATE TABLE `group_template` (
                `group_template_id` SMALLINT(5) UNSIGNED NOT NULL AUTO_INCREMENT,
                `group_template_name` VARCHAR(255) NOT NULL COLLATE 'utf8_bin',
                PRIMARY KEY (`group_template_id`),
                UNIQUE INDEX `name` (`group_template_name`)
            )
            COMMENT='User group template'
            COLLATE='utf8_bin'
            ENGINE=InnoDB
            ROW_FORMAT=DEFAULT
        ''',
        '''
            CREATE TABLE `group_template_permission` (
                `group_template_key` SMALLINT(5) UNSIGNED NOT NULL,
                `permission_key` TINYINT(3) UNSIGNED NOT NULL,
                PRIMARY KEY (`group_template_key`, `permission_key`),
                INDEX `fk_template_permissions` (`permission_key`),
                CONSTRAINT `fk_template_permissions` FOREIGN KEY (`permission_key`) REFERENCES `action` (`action_id`) ON UPDATE CASCADE ON DELETE CASCADE,
                CONSTRAINT `fk_template_template` FOREIGN KEY (`group_template_key`) REFERENCES `group_template` (`group_template_id`) ON UPDATE CASCADE ON DELETE CASCADE
            )
            COMMENT='Permissions belonging for group templates'
            COLLATE='utf8_bin'
            ENGINE=InnoDB
            ROW_FORMAT=DEFAULT
        ''',
        '''
            CREATE PROCEDURE `create_group_from_template`(IN `template_id` INT, IN `new_group_name` VARCHAR(128), IN `trac_environment_id` INT)
                LANGUAGE SQL
                NOT DETERMINISTIC
                CONTAINS SQL
                SQL SECURITY DEFINER
                COMMENT ''
            BEGIN
            DECLARE new_group_id INT;
            START TRANSACTION;
            INSERT INTO `group` VALUES(null, new_group_name, trac_environment_id);
            SELECT LAST_INSERT_ID() INTO new_group_id FROM `group` LIMIT 0,1;
            INSERT INTO `group_permission`
            (
            SELECT new_group_id, permission_key
            FROM group_template_permission
            WHERE group_template_permission.group_template_key = template_id
            );
            COMMIT;
            END
        ''',
        '''
            CREATE PROCEDURE `get_templates`()
                LANGUAGE SQL
                NOT DETERMINISTIC
                CONTAINS SQL
                SQL SECURITY DEFINER
                COMMENT ''
            BEGIN
            SELECT group_template_name FROM group_template WHERE 1;
            END
        ''',
        '''
            CREATE PROCEDURE `get_template_id`(IN `template_name` VARCHAR(128))
                LANGUAGE SQL
                NOT DETERMINISTIC
                CONTAINS SQL
                SQL SECURITY DEFINER
                COMMENT ''
            BEGIN
            SELECT group_template_id FROM group_template WHERE group_template_name = template_name;
            END
        ''',
        '''
            CREATE PROCEDURE `get_all_template_permissions`()
                LANGUAGE SQL
                NOT DETERMINISTIC
                CONTAINS SQL
                SQL SECURITY DEFINER
                COMMENT ''
            BEGIN

            SELECT group_template.group_template_name, action.action_string
            FROM `group_template`
            LEFT JOIN group_template_permission ON group_template_permission.group_template_key = group_template.group_template_id
            LEFT JOIN action ON action.action_id = group_template_permission.permission_key;

            END
        ''',
        '''
            CREATE PROCEDURE `add_permission_to_template`(IN `template_name` VARCHAR(128), IN `permission_name` VARCHAR(128))
                LANGUAGE SQL
                NOT DETERMINISTIC
                CONTAINS SQL
                SQL SECURITY DEFINER
                COMMENT ''
            BEGIN
            DECLARE permission_key INT;
            DECLARE template_key INT;

            START TRANSACTION;

            SELECT action_id INTO permission_key FROM action
            WHERE action_string = permission_name;

            SELECT group_template_id INTO template_key FROM group_template
            WHERE group_template_name = template_name;

            INSERT INTO group_template_permission VALUES(template_key, permission_key);

            COMMIT;

            END
        '''
        ]

        return self.manager.db_downgrade(queries)

    def applied(self):
        """
        Checks from database if the the procedure exists
        """
        conf = Configuration.instance()
        with admin_query() as cursor:
            cursor.execute('''
                SHOW PROCEDURE STATUS
                WHERE
                    Name = 'create_group_from_template' AND
                    Db = '{0}'
            '''.format(conf.db_admin_schema_name))
            return cursor.rowcount == 0


MigrateMgr.instance().add(NukeGroupTemplates())
