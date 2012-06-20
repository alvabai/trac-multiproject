# -*- coding: utf-8 -*-
"""
Migration to remove addactivityforproject procedure from trac_admin database.
"""
from multiproject.core.db import admin_query
from multiproject.core.migration import MigrateBase, MigrateMgr
from multiproject.core.configuration import Configuration


class NukeActivityProcedure(MigrateBase):
    """This migration removes the addactivityforproject procedure from the trac_admin
    database. If downgrading, the procedure is created again."""

    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = self.__doc__

    def upgrade(self):
        """
        Upgrade implementation. Removes the procedure from database.
        """
        if self.applied():
            print "addactivityforproject procedure already removed from database.".rjust(12)
            return True

        return self.manager.db_upgrade(['DROP PROCEDURE `addactivityforproject`'])

    def downgrade(self):
        """
        Downgrade implementation, creates the procedure into the database.
        """
        if not self.applied():
            return False

        queries = ['''
            CREATE PROCEDURE `addactivityforproject`(projectid int, ticketchanges float, wikichanges float,
                                                     scmchanges float, attachmentchanges float, discussionchanges float,
                                                     projectdescription VARCHAR(255))
            BEGIN
            UPDATE `project_activity`
            SET ticket_changes = ticketchanges,
                wiki_changes = wikichanges,
                scm_changes = scmchanges,
                attachment_changes = attachmentchanges,
                discussion_changes = discussionchanges,
                last_update = NOW(),
                project_description = projectdescription
            WHERE project_key = projectid;

            IF ROW_COUNT() = 0 THEN
                INSERT INTO `project_activity`
                SET project_key = projectid,
                    ticket_changes = ticketchanges,
                    wiki_changes = wikichanges,
                    scm_changes = scmchanges,
                    discussion_changes = discussionchanges,
                    attachment_changes = attachmentchanges,
                    last_update = NOW(),
                    project_description = projectdescription;
            END IF;
            END
        ''']

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
                    Name = 'addactivityforproject' AND
                    Db = '{0}'
            '''.format(conf.db_admin_schema_name))
            return cursor.rowcount == 0


MigrateMgr.instance().add(NukeActivityProcedure())
