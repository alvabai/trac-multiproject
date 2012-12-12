import logging
import MySQLdb

from trac.config import Configuration

from multiproject.core.configuration import conf
from multiproject.core.exceptions import SingletonExistsException
from multiproject.core.db import get_connection, admin_transaction, admin_query
from multiproject.core.decorators import deprecated

# logs to console
log = logging.getLogger('migration')


def printer(msg, title=None, flag='plain'):
    """
    Simple console print. Example usage::

        printok = lambda msg, title=None: printer(msg, title, 'success')
        printerr = lambda msg, title=None: printer(msg, title, 'error')
        self.printok = lambda msg, title=None: printer(msg, title, 'success')

        printerr('Uh-oh')
        printerr('Uh-oh', 'FAIL')
        printok('Looking good')

    :param str msg: Message to show
    :param str title: Optional title to set/highlight
    :param str flag: Message flag that
    """
    templates = {
        'plain': "{0}: {1}",
        'success': "\033[32m{0}\033[0m: {1}",
        'warning': "\033[44m{0}\033[0m: {1}",
        'error': "\033[31m{0}\033[0m: {1}",
    }
    print templates.get(flag, '{0}{1}').format(title or flag.upper(), msg)


class MigrateBase(object):
    def __init__(self):
        self.id = ""
        self.description = ""
        self.manager = MigrateMgr.instance()
        self.printout = lambda msg, title=None: printer(msg, title)
        self.printerr = lambda msg, title=None: printer(msg, title, 'error')
        self.printwarn = lambda msg, title=None: printer(msg, title, 'warning')
        self.printok = lambda msg, title=None: printer(msg, title, 'success')

    def upgrade(self):
        return

    def downgrade(self):
        return

    def applied(self):
        return

    def _print(self, msg, title=None, flag=''):
        """
        Simple console print. Example usage::

            printerr('Uh-oh')
            printerr('Uh-oh', 'FAIL')
            printok('Looking good')

        :param str msg: Message to show
        :param str title: Optional title to set/highlight
        :param str flag: Message flag that
        """
        templates = {
            'success': "\033[32m{0}\033[0m: {1}",
            'warning': "\033[44m{0}\033[0m: {1}",
            'error': "\033[31m{0}\033[0m: {1}",
        }
        print templates.get(flag, '{0}{1}').format(title or flag.upper(), msg)


class MigrateConfigure(object):
    def __init__(self):
        self.conf = conf.instance()

    def set_home_config(self, values):
        syspath = self.conf.getEnvironmentSysPath("home")
        setconf = Configuration(syspath + '/conf/trac.ini')
        try:
            for (main, sub, value) in values:
                setconf.set(main, sub, value)
            setconf.save()
        except:
            return False
        return True

    def get_home_config(self, mainchapter, subchapter):
        syspath = self.conf.getEnvironmentSysPath("home")
        getconf = Configuration(syspath + '/conf/trac.ini')
        return getconf.get(mainchapter, subchapter)


class MigrateDatabase(object):

    def db_upgrade(self, commands):
        """
        :param commands: List of queries
        :return: False on failure
        """
        with admin_transaction() as cr:
            current_query = None
            try:
                for command in commands:
                    current_query = command
                    cr.execute(command)
            except MySQLdb.IntegrityError:
                log.exception("Exception. Migration failed with query: %s" % str(current_query))
                return False
        return True

    def db_downgrade(self, commands):
        """
        :param commands: List of queries
        :return: False on failure
        """
        with admin_transaction() as cr:
            try:
                for command in commands:
                    cr.execute(command)
            except MySQLdb.IntegrityError:
                log.exception("Exception. Migration downgrade failed with commands '''%s'''." % str(commands))
                return False
        return True

    def db_applied(self, cmd, line, column, result, rows):
        with admin_query() as cr:
            try:
                cr.execute(cmd)

                if column is not None and line is not None:
                    row = cr.fetchall()
                    if len(row) > line and row[line][column] == result:
                        return True
                elif line is not None:
                    row = cr.fetchall()
                    if len(row) > line and row[line] == result:
                        return True
                elif rows is not None:
                    row = cr.fetchall()
                    if len(row) == rows:
                        return True
                elif result is not None:
                    row = cr.fetchone()
                    if row[0] == result:
                        return True
            except:
                params = (str(cmd), str(line), str(column), str(result), str(rows))
                log.exception(
                    "Exception. Failed checking if migration was applied {command:%s, line:%s, column:%s, result:%s, rows: %s}." % params)

        return False


class MigrateMgr(object):

    __instance = None

    def __init__(self):
        if MigrateMgr.__instance:
            raise SingletonExistsException('Singleton Error')

        self.printout = lambda msg, title=None: printer(msg, title)
        self.printerr = lambda msg, title=None: printer(msg, title, 'error')
        self.printwarn = lambda msg, title=None: printer(msg, title, 'warning')
        self.printok = lambda msg, title=None: printer(msg, title, 'success')
        self.__migrations = {}

    @staticmethod
    def instance():
        if MigrateMgr.__instance is None:
            MigrateMgr.__instance = MigrateMgr()
        return MigrateMgr.__instance

    def set_home_config(self, values):
        return MigrateConfigure().set_home_config(values)

    def get_home_config(self, mainchapter, subchapter):
        return MigrateConfigure().get_home_config(mainchapter, subchapter)

    def db_upgrade(self, commands):
        return MigrateDatabase().db_upgrade(commands)

    def db_downgrade(self, commands):
        return MigrateDatabase().db_downgrade(commands)

    def db_applied(self, cmd, line = None, column = None, result = None, rows = None):
        return MigrateDatabase().db_applied(cmd, line, column, result, rows)

    def add(self, client):
        if client.id not in self.__migrations.keys():
            self.__migrations[client.id] = client

    def sort_clients(self):
        items = self.__migrations.items()
        items.sort()
        return items

    def last_installed_migration_id(self):
        """ Get latest migration identifier that is installed
        """
        query = "SELECT migration_name FROM `migration` ORDER BY migration_name DESC LIMIT 0,1"
        migration = None
        with admin_query() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone()
                if row:
                    migration = row[0]
            except:
                log.exception("Exception. Failed finding last installed migration.")

        return migration

    def list_installed(self):
        """ Get list of installed migrations
        """
        query = "SELECT migration_name FROM `migration` ORDER BY migration_name DESC"
        migrations = []
        with admin_query() as cursor:
            try:
                cursor.execute(query)
                migrations = [row[0] for row in cursor]
            except:
                log.exception("Exception. Failed finding last installed migration.")

        return migrations

    def get_ids_between(self, migration_a, migration_b):
        """ Get migration ids (inclusive) between a and b
        """
        # If and end and start equals, don't bother
        if migration_a == migration_b:
            return [migration_a]

        all_migrations = self.__migrations.keys()
        all_migrations.sort()

        if not migration_a:
            migration_a = all_migrations[0]
        if not migration_b:
            migration_b = all_migrations[0]
        end_points = [migration_a, migration_b]

        ids = []
        head_found = False
        # Go through migrations and append between (a & b)
        for id in all_migrations:
            if (not head_found) and (id in end_points):
                head_found = True
                end_points.remove(id)
            if head_found:
                ids.append(id)
            if head_found and (id in end_points):
                break
        return ids

    def migrate_to(self, target_migration):
        """ Downgrades or Upgrades to target migration
        """
        last_migrated = self.last_installed_migration_id()
        if last_migrated not in self.__migrations:
            self.printerr("Migration %s not found!" % last_migrated)
            return

        # Return if no point in migration
        keys = self.__migrations.keys()
        if (target_migration == last_migrated) or (target_migration not in keys):
            return

        # Get migration names between end & start
        needed_ids = self.get_ids_between(last_migrated, target_migration)

        print "OPERATION   MIGRATION"
        print "---------------------------------------------------------------"

        # Select upgrade or downgrade
        if last_migrated < target_migration:
            if last_migrated:
                try:
                    needed_ids.remove(last_migrated)
                except:
                    self.printerr("Migration %s not found!" % last_migrated)
            self.upgrade(needed_ids)
        else:
            needed_ids.reverse()
            needed_ids.remove(target_migration)
            self.downgrade(needed_ids)

    def upgrade(self, migration_ids):
        """ Upgrades all migrations with given ids
        """
        success_ids = []
        for id in migration_ids:
            self.printwarn(id, 'UPGRADING')
            self.__migrations[id].upgrade()

            if self.__migrations[id].applied():
                self.report_upgrade(id)
                success_ids.append(id)
                self.printok('Upgrade completed')
            else:
                self.printerr('Upgrade failed')
                break
        return success_ids

    def downgrade(self, migration_ids):
        """ Downgrades all migrations with given ids
        """
        success_ids = []
        for id in migration_ids:
            self.printwarn(id, 'DOWNGRADING')
            self.__migrations[id].downgrade()

            if not self.__migrations[id].applied():
                self.report_downgrade(id)
                success_ids.append(id)
                self.printok('Downgrade completed')
            else:
                self.printerr('Downgrade failed')
                break
        return success_ids

    def report_upgrade(self, migration):
        """ Writes into database that migration was upgraded
        """
        query = "INSERT INTO `migration` (migration_name, datetime) VALUES('" + migration + "', null)"
        with admin_transaction() as cursor:
            try:
                cursor.execute(query)
            except:
                log.exception("Failed to insert migration to database")
                raise

    def report_downgrade(self, migration):
        """ Writes into database that migration was downgraded
        """
        query = "DELETE FROM `migration` WHERE migration_name = '" + migration + "'"
        with admin_transaction() as cursor:
            try:
                cursor.execute(query)
            except:
                log.exception("Failed to remove migration from database")
                raise

    def update_to(self, target_migration):
        if target_migration not in self.__migrations:
            print "The cherry-picked migration was not found"
        self.migrate_to(target_migration)

    def update_new(self):
        installed = set(self.list_installed())
        migrations = self.__migrations.keys()
        migrations.sort()
        new_migrations = []
        new_noticed = False
        print '\nNEW AND INSTALLED MIGRATIONS'
        print '---------------------------------------------------------------'
        for migration in migrations:
            if migration in installed:
                if new_noticed:
                    self.printwarn(migration, 'INSTALLED')
            else:
                new_noticed = True
                new_migrations.append(migration)
        self.upgrade(new_migrations)

    def cherry_pick(self, target_migration, update=True):
        installed = set(self.list_installed())
        if target_migration not in self.__migrations:
            self.printerr("The cherry-picked migration was not found")
        if update:
            if target_migration in installed:
                self.printerr("Migration already installed, cannot upgrade: %s" % target_migration)
            else:
                self.upgrade([target_migration])
        else:
            if not target_migration in installed:
                self.printerr("Migration not applied, cannot downgrade: %s" % target_migration)
            else:
                self.downgrade([target_migration])

    def show_status(self):
        installed = set(self.list_installed())

        print '\nSTATUS      MIGRATION'
        print '---------------------------------------------------------------'
        migrations = self.__migrations.keys()
        migrations.sort()
        for migration in migrations:
            if migration in installed:
                self.printok(migration, 'INSTALLED')
            else:
                self.printwarn(migration, 'NEW      ')
