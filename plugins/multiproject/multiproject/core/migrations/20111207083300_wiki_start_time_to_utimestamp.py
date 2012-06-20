__author__ = 'alhannin'

from multiproject.core.migration import MigrateBase, MigrateMgr
from multiproject.core.db import db_query, admin_query
from multiproject.core.configuration import conf
import MySQLdb


class WikiStartTimeToUTimeStamp(MigrateBase):
    """
    Updates DB to correspond the fix in Ticket #663:
    Incorrect wiki page create time.

    Multiplies the time with 1 000 000 for the automatically created wiki pages
    WikiStart and Downloads.

    Note, that the datatype of column time must be BIGINT(20).
    Warning will be shown if it is not for some database.
    """

    def __init__(self):
        MigrateBase.__init__(self)
        self.id = __name__.split('.')[-1]
        self.description = "Change wiki start time to be utimestamp: multiply with 10**6 those less than 20 * 10**9"

    def upgrade(self):
        if self.applied():
            print "            Migration 20111207083300_wiki_start_time_to_utimestamp.py already applied"
            return True

        identifier_rows = self._get_project_identifier_rows()

        # Note: If the upgrade fails, it can be because the time column is int instead of bigint in wiki table.

        procedures = []
        for row in identifier_rows:
            procedures.append("""
            UPDATE `%(identifier)s`.`wiki`
               SET time = time * 1000000
             WHERE (name = 'WikiStart' OR name = 'Downloads') AND version = 1
               AND time < 2147483648;
            """ % { 'identifier' : MySQLdb.escape_string(row[0])})

        return self.manager.db_upgrade(procedures)

    def downgrade(self):
        if not self.applied():
            print "            Migration 20111207083300_wiki_start_time_to_utimestamp.py not applied"
            return False

        identifier_rows = self._get_project_identifier_rows()

        procedures = []
        for row in identifier_rows:
            procedures.append("""
            UPDATE `%(identifier)s`.`wiki`
               SET time = time / 1000000
             WHERE (name = 'WikiStart' OR name = 'Downloads') AND version = 1
               AND time >= 2147483648;
            """ % { 'identifier' : MySQLdb.escape_string(row[0])})

        return self.manager.db_downgrade(procedures)

    def applied(self):
        """
        Called by migration manager to check if the migration is already run into the
        database. This performs two queries; checks if any of project wiki time stamp
        columns are of type BIGINT(20). Then checks if the time stamp in question is already
        big enough to be correct.

        :returns: True if the migration has already been run
        """

        identifier_rows = self._get_project_identifier_rows()

        was_applied = True
        with db_query() as cursor:
            for identifier, in identifier_rows:
                query = ("DESCRIBE `%(identifier)s`.`wiki` `time`;" %
                         { 'identifier' : MySQLdb.escape_string(identifier)})
                cursor.execute(query)
                describe_row = cursor.fetchone()
                # Returning columns:
                # +-------+------------+------+-----+---------+-------+
                # | Field | Type       | Null | Key | Default | Extra |
                # +-------+------------+------+-----+---------+-------+
                if describe_row and describe_row[1] != 'bigint(20)':
                    print ("ERROR: Type of column `time` of `wiki` table is wrong in database `%s`: %s "
                           % (identifier, describe_row[1]))
                    was_applied = False

                query =  """
                SELECT count(*)
                  FROM `%(identifier)s`.`wiki`
                 WHERE (name = 'WikiStart' OR name = 'Downloads') AND version = 1
                   AND time < 2147483648;
                """ % { 'identifier' : MySQLdb.escape_string(identifier)}
                cursor.execute(query)
                # Above select always returns a row, unless an exception is thrown
                count = cursor.fetchone()[0]
                if count and count != 0:
                    was_applied = False
                    break

        return was_applied

    def _get_project_identifier_rows(self):
        """
        Queries trac environment names from ``trac_admin`` database

        :returns: All trac environment names from ``trac_environment`` table
        """
        # TODO: instead of identifier_rows, return project_schema_names as a list
        rows = []

        with admin_query() as cursor:
            cursor.execute("SELECT identifier FROM `trac_environment`;")
            rows = cursor.fetchall()

        return rows


MigrateMgr.instance().add(WikiStartTimeToUTimeStamp())
