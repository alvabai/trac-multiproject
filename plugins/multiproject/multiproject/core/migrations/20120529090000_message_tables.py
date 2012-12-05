# -*- coding: utf-8 -*-
"""
Migration introduces new tables:

- ``message``: Store messages between users
- ``message_group`` Stores message group info
- ``message_group_recipient`` Stores message groups recipients
- ``message_flag``: Storing different kind of flags to messages like 'deleted', 'starred'. The flag is numeric and the
    actual meaning needs to be set in application.

.. NOTE::

    Even if message_group.id is auto increment identifier,
    there is/can be multiple values with same id. Same id means same group!

"""
from multiproject.core.db import admin_query, cursors
from multiproject.core.migration import MigrateBase, MigrateMgr


class MessageTables(MigrateBase):

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
        CREATE TABLE message_group (
            `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `creator_id` int(10) UNSIGNED DEFAULT NULL,
            `created` DATETIME DEFAULT NULL,
            `title` varchar(256) DEFAULT NULL,
            PRIMARY KEY (`id`),
            KEY (`creator_id`),
            FOREIGN KEY (`creator_id`) REFERENCES user(`user_id`) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
        """,
        """
        CREATE TABLE message_group_recipient (
            `message_group_id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `user_id` int(10) UNSIGNED NOT NULL,
            UNIQUE KEY (`message_group_id`, `user_id`),
            KEY (`message_group_id`),
            KEY (`user_id`),
            FOREIGN KEY (`user_id`) REFERENCES user(`user_id`) ON DELETE CASCADE,
            FOREIGN KEY (`message_group_id`) REFERENCES message_group(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
        """,
        """
        CREATE TABLE message (
            `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `sender_id` int(10) UNSIGNED NOT NULL,
            `message_group_id` int(10) UNSIGNED NOT NULL,
            `env` varchar(32) DEFAULT NULL,
            `content` TEXT NOT NULL,
            `created` DATETIME DEFAULT NULL,
            PRIMARY KEY (`id`),
            KEY (`env`),
            KEY (`message_group_id`),
            FOREIGN KEY (`env`) REFERENCES trac_environment(`identifier`) ON DELETE CASCADE,
            FOREIGN KEY (`message_group_id`) REFERENCES message_group(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
        """,
        """
        CREATE TABLE message_flag (
            `message_id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `user_id` int(10) UNSIGNED NOT NULL,
            `flag` int(5) NOT NULL,
            FOREIGN KEY (`message_id`) REFERENCES message(`id`) ON DELETE CASCADE,
            FOREIGN KEY (`user_id`) REFERENCES user(`user_id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
        """]

        return self.manager.db_upgrade(queries)

    def downgrade(self):
        if not self.applied():
            print "Migration {0} not applied yet".format(__file__).rjust(12)
            return False

        queries = [
            "DROP TABLE message_flag",
            "DROP TABLE message",
            "DROP TABLE message_group_recipient",
            "DROP TABLE message_group",
        ]

        return self.manager.db_downgrade(queries)

    def applied(self):
        """
        Check if column exists or not
        :returns: True if exists, otherwise False
        """
        with admin_query(cursors.DictCursor) as cursor:
            try:
                cursor.execute('DESC message')
            except:
                return False
        return True


MigrateMgr.instance().add(MessageTables())
