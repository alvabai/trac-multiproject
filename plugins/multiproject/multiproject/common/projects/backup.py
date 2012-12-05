# -*- coding: utf-8 -*-
"""
Contents of this module
"""
from datetime import datetime
from exceptions import OSError
from subprocess import Popen, PIPE
import os

from trac.core import TracError
from trac.db import DatabaseManager, api
from trac.env import open_environment
from trac.util import to_unicode
from trac.util.compat import close_fds
from trac.util.datefmt import utc
from trac.util.text import exception_to_unicode
from trac.util.translation import _

from multiproject.core.configuration import conf
from multiproject.core.db import admin_transaction, admin_query


class ProjectBackup(object):
    """
    Class models the project backups (snapshots), doable by the project admin.
    Example usage:

    >>> prj = Project()
    >>> pb = ProjectBackup(prj)
    >>> pb.backup()

    Properties (set automatically on __init__):
        - mysql_path: path to mysql client (default: expect it to found from ``$PATH``)
        - project: reference to project to backup/restore
        - env: environment object based on given project info
        - dm: database manager setup against the environment

    Configuration keys:
        Class uses following configuration keys (placed either in ``project.ini`` or
        to project specific ``conf/trac.ini`` -file) to adjust the functionality:

    """
    def __init__(self, project):
        """
        Initiates the class.

        :param project: Instance of the :class:`Project` to backup/restore
        """
        self.project = project
        self.env = open_environment(self.project.trac_fs_path, use_cache=True)
        backup_dir = self.env.config.get('trac', 'backup_dir', '/tmp')
        self.backup_path_tmpl =  backup_dir + '/project-%s.snapshot-%d.sql'
        self.mysql_path = self.env.config.get('trac', 'mysql_path', 'mysql')

        self.dm = DatabaseManager(self.env)

    def backup(self, user_id, description=None):
        """
        Creates a database backup of the trac instance.

        .. IMPORTANT:: Only the **database** is backed up, while attachments are left as is.

        :param user_id: Id the user who did the restore
        :param description: Optional description about the backup, why it was done or current state...

        Returns:
            True if all went well, otherwise TracError is raised.

        """
        assert isinstance(user_id, long), 'User id needs to be long int'
        description = description if description else ''
        dump_path = None

        # Create database entry about the back
        with admin_transaction() as cursor:
            cursor.execute(("INSERT INTO project_backup (project_key, created_by, description)"
                            "VALUES (%s, %s, %s)"), (self.project.id, user_id, description))

            # Now, take the last inserted id and use it to generate unique dump path
            dump_path = self.backup_path_tmpl % (self.project.env_name, cursor.lastrowid)

            # Use Trac's database manager to dump the database into filesystem
            try:
                self.dm.backup(dump_path)

            except OSError, err:
                self.env.log.exception(err)
                raise TracError('Failed to dump database: %s' % err)

        return True

    def restore(self, backup_id, user_id):
        """
        Restores the database dump over the existing setup

        :param backup_id: Backup identifier, as an integer
        :param user_id: Id the user who did the restore

        Returns:
            A dictionary of the restored backup
        """
        backup = {}

        assert isinstance(user_id, long), 'User id needs to be long integer'
        assert isinstance(backup_id, long), 'Backup id needs to be long integer'

        # Create dictionary containing the info about the backup
        backup = {'id':backup_id, 'restored':datetime.utcnow(), 'restored_by':user_id}

        # Open the db connection for adding the restore information, if any of the operations fail,
        # the database transaction will be rolled back in the context manager
        with admin_transaction() as cursor:
            # Update restore into to project_backup table. Use result count to check if the id was
            # actually found or not
            query = '''
                UPDATE project_backup
                SET restored=%s, restored_by=%s
                WHERE id = %s
            '''
            cursor.execute(query, (backup['restored'], backup['restored_by'] , backup['id']))

            # Check if the backup_id was actually found?
            if not cursor.rowcount:
                raise TracError('Backup cannot be found')

            # Do the actual database restore
            try:
                mysqlp = self._get_mysql_process(self.env)
            except OSError, e:
                raise TracError(_("Unable to run mysql command: %(msg)s", msg=exception_to_unicode(e)))

            # Pass the backup into stdin
            backup_path = self.backup_path_tmpl % (self.project.env_name, backup['id'])

            if not os.path.exists(backup_path):
                conf.log.error('User failed to restore project backup')
                raise TracError(_('Backup file cannot be found'))

            with open(backup_path, 'r+b') as backup_input:
                errmsg = mysqlp.communicate(input=backup_input.read())

            if mysqlp.returncode != 0:
                msg = _('Restoring the database backup failed: %(msg)s', msg=to_unicode(errmsg.strip()))
                conf.log.error(msg)
                raise TracError(msg)

        return backup

    def delete(self, backup_id):
        """
        Deletes the database dump from the filesystem and the database
        row where it is being defined

        :param backup_id: Backup identifier, as an integer

        """
        backup = {}

        assert isinstance(backup_id, long)

        # Create dictionary containing the info about the backup
        backup = {'id':backup_id}

        # Open the db connection for adding the restore information
        with admin_transaction() as cursor:
            # Update restore into to project_backup table. Use result count to check if the id was actually
            # found or not
            query = '''
                DELETE FROM project_backup
                WHERE id = %s
            '''
            cursor.execute(query, backup['id'])

            # Check if the backup_id was actually found?
            if not cursor.rowcount:
                raise TracError('Backup cannot be found')

            # Delete the backup from filesystem (if it can be found)
            dump_path = self.backup_path_tmpl % (self.project.env_name, backup['id'])
            if os.path.exists(dump_path):
                os.remove(dump_path)

        return backup

    def get_backups(self):
        """
        Returns a list of backups, created for the current project.
        Each backup is presented as dictionary:

        .. code-block:: python

            {'id':num, 'name':'Generated name for the backup', 'created':timestamp}

        """
        rows = []

        # NOTE: For some reason, MySQLDB cursor wants the placeholders to be as %s (instead of %d)
        # Reference: http://mysql-python.sourceforge.net/MySQLdb.html#some-examples
        with admin_query() as cursor:
            cursor.execute("""
                SELECT
                    pb.id, pb.project_key, pb.description, pb.created, pb.restored, pb.created_by, pb.restored_by,
                    uc.username AS created_by_username, ur.username AS restored_by_username
                FROM project_backup AS pb
                LEFT JOIN user AS uc ON uc.user_id = pb.created_by
                LEFT JOIN user AS ur ON ur.user_id = pb.restored_by
                WHERE project_key = %s
                ORDER BY created DESC
            """, (self.project.id, ))

            # Iterate results
            for row in cursor:
                # Set the timezone info to datetime objects: entries are saved in UTC
                created = row[3].replace(tzinfo=utc) if row[3] else row[3]
                restored = row[4].replace(tzinfo=utc) if row[4] else row[4]

                rows.append({
                    'id': row[0],
                    'project_key': row[1],
                    'description': row[2],
                    'created': created,
                    'restored': restored,
                    'created_by': row[5],
                    'restored_by': row[6],
                    'created_by_username': row[7],
                    'restored_by_username': row[8],
                })

        return rows

    def _get_mysql_process(self, env):
        """
        Returns the mysql process object, to run the client
        in python process.

        :param env: Environment instance against which the mysql client process should be created.
        """
        db_url = env.config.get('trac', 'database')
        scheme, db_prop = api._parse_db_str(db_url)
        db_name = os.path.basename(db_prop['path'])

        # Construct the mysql client command string
        args = [self.mysql_path]
        if 'host' in db_prop:
            args.extend(['-h', db_prop['host']])
        if 'port' in db_prop:
            args.extend(['-P', str(db_prop['port'])])
        if 'user' in db_prop:
            args.extend(['-u', db_prop['user']])
        args.extend([db_name])

        # Set mysql password into environment variable
        environ = os.environ.copy()
        if 'password' in db_prop:
            environ['MYSQL_PWD'] = str(db_prop['password'])

        return Popen(args, env=environ, stderr=PIPE, stdin=PIPE, close_fds=close_fds)
