# -*- coding: utf-8 -*-
"""
Migration adds new columns:

- ``contexts.summary_name`` (name for the context in Summary page)
- ``contexts.explore_projects_visibility`` (defaults to 'separate')
- ``contexts.admin_type`` (how the context is displayed, defaults to 'tree')
- ``contexts.edit_type`` (defaults to 'none')

"""
from multiproject.core.db import admin_query, cursors
from multiproject.core.migration import MigrateBase, MigrateMgr
from multiproject.core.configuration import conf

class ContextTableConfiguration(MigrateBase):

    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = __doc__

    def upgrade(self):
        if self.applied():
            print "Migration already applied".rjust(12)
            return True

        main_context_id = 0
        with admin_query() as cursor:
            try:
                query = """
                SELECT context_id FROM contexts
                WHERE LOWER(context_name) IN ('main categories', 'categories') LIMIT 1
                """
                cursor.execute(query)

                for row in cursor:
                    main_context_id = int(row[0])
            except:
                conf.log.exception("Failed to read contexts from database.")


        # summary_name - name shown before the list of
        # categories in the Summary view, NULL if not shown separately there
        # (hidden categories not shown)

        # explore_projects_visibility
        # - 'separate': listed separately
        # - 'combined': combined to the root level

        # admin_type
        # - 'list'
        # - 'select_box'
        # - 'tree'
        # - 'main' (means also: tree)
        # - 'autocomplete' (means also: combined)
        # - 'combined'

        # edit_type
        # - 'add' means that the normal project admins can add categories
        #   into this context
        # - 'none'

        queries = ["""
        ALTER TABLE contexts
        ADD COLUMN `summary_name` VARCHAR(63)
        NOT NULL DEFAULT '' AFTER `context_description`
        """, """
        ALTER TABLE contexts
        ADD COLUMN `explore_projects_visibility` ENUM ('separate', 'combined')
        NOT NULL DEFAULT 'separate' AFTER `summary_name`
        """, """
        ALTER TABLE contexts
        ADD COLUMN `admin_type` ENUM ('list', 'select_box', 'tree', 'main', 'autocomplete', 'combined')
        NOT NULL DEFAULT 'tree' AFTER `explore_projects_visibility`
        """, """
        ALTER TABLE contexts
        ADD COLUMN `edit_type` ENUM ('add', 'none')
        NOT NULL DEFAULT 'none' AFTER `admin_type`
        """]

        if main_context_id:
            queries.append("""
            UPDATE contexts
            SET admin_type = 'main', explore_projects_visibility = 'combined'
            WHERE context_id = {0}
            """.format(int(main_context_id)))
        if 'Custom' in conf.combined_contexts:
            queries.append("""
            UPDATE contexts
            SET admin_type = 'autocomplete', explore_projects_visibility = 'combined', edit_type = 'add'
            WHERE context_name = 'Custom'
            """)

        queries.append("""
        UPDATE contexts SET summary_name = 'Language', admin_type = 'select_box' WHERE context_name = 'Natural language'
        """)
        queries.append("""
        UPDATE contexts SET summary_name = 'License' WHERE context_name = 'License'
        """)
        queries.append("""
        UPDATE contexts SET summary_name = 'Development status' WHERE context_name = 'Development status'
        """)

        return self.manager.db_upgrade(queries)

    def downgrade(self):
        if not self.applied():
            print "Migration {0} not applied yet".format(__file__).rjust(12)
            return False

        queries = [
            "ALTER TABLE contexts DROP COLUMN edit_type",
            "ALTER TABLE contexts DROP COLUMN admin_type",
            "ALTER TABLE contexts DROP COLUMN explore_projects_visibility",
            "ALTER TABLE contexts DROP COLUMN summary_name"
        ]

        return self.manager.db_downgrade(queries)

    def applied(self):
        """
        Check if column exists or not
        :returns: True if exists, otherwise False
        """
        with admin_query(cursors.DictCursor) as cursor:
            cursor.execute('DESC contexts')
        return 'edit_type' in [row['Field'] for row in cursor]

MigrateMgr.instance().add(ContextTableConfiguration())


