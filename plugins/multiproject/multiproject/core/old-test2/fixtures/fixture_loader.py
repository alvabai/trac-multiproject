import csv

from multiproject.core.configuration import Configuration
from multiproject.core.multiproj_exceptions import SingletonExistsException

conf = Configuration.instance()

def to_absolute_path(path):
    """ If. path starts with / nothing happends.
        Ow. path of the __file__ is used as base
    """
    if not path.startswith('/'):
        path = __file__.rsplit('/', 1)[0] + '/' + path
    return path


class Fixture(object):
    """ Hold information of a fixture
        
        This information can be accessed from fixture
        ---------------------------------------------
        file_path - Full path with filename.             example /some/path/auth_cookie.csv
        dir       - Directory part in file_path.         example /some/path
        file_name - Filename part in file_path.          example auth_cookie.csv
        table_name- Table name. Filename without suffix. example auth_cookie
        """

    def __init__(self, file_path):
        file_path = to_absolute_path(file_path)

        # Simple class holding fixture info
        self.file_path = file_path
        self.dir, self.file_name = file_path.rsplit('/', 1)
        self.table_name = self.file_name.split('.')[0]


class FixtureLoader(object):
    """ Class for loading test fixtures into database
    
    Usage.
             - Place all fixtures into folder under this directory (now there is 'basic' set)
             - Fixture file is named as table name with .csv suffix in csv format
             - fixtures.txt holds sequence in which fixtures needs to be loaded (unloaded in reverse order)
             
             # This would load all the fixtures in basic set
             from fixture_loader import FixtureLoader
             fl = FixtureLoader.instance()
             fl.load_all_fixtures('basic')
    """
    __instance = None

    def __init__(self):
        if FixtureLoader.__instance:
            raise SingletonExistsException()

        self.query_cache = {}
        self.db = None

        Configuration.config_file = '/etc/trac/cqde.test.ini'
        conf.refresh()

    @staticmethod
    def instance():
        if FixtureLoader.__instance is None:
            FixtureLoader.__instance = FixtureLoader()
        return FixtureLoader.__instance

    def load_all_fixtures(self, path):
        """ Loads all the fixtures in the path. Test in console.
        """
        path = to_absolute_path(path)
        self.__truncate_test_tables(path)

        for file in self.__read_fixture_list(path):
            self.load_fixture(file)

    def __truncate_test_tables(self, path):
        path = to_absolute_path(path)

        fixture_paths = self.__read_fixture_list(path)
        fixture_paths.reverse()

        for file in fixture_paths:
            fixture = Fixture(file)
            self.__clear_test_table(fixture.table_name)

    def load_fixture(self, file_path):
        """ Loads a single fixture in a path
        """
        fixture = Fixture(file_path)
        self.__clear_test_table(fixture.table_name)
        self.__load_fixture_data(fixture)

    def __load_fixture_data(self, fixture):
        """ Load fixture data into database
        """
        query = self.__build_query(fixture)

        if query:
            self.__run_query(query)

    def __build_query(self, fixture):
        if fixture.file_path in self.query_cache:
            return self.query_cache[fixture.file_path]

        # Reader instance. Quote none to get also quotes on strings automatically
        reader = csv.reader(open(fixture.file_path), delimiter=',', quotechar='"', quoting=csv.QUOTE_NONE)

        field_names = reader.next()

        if not field_names:
            print "Not going to load " + fixture.table_name + ". No fields defined."
            return

        # Build one big insert statement
        query = "INSERT INTO `%(table)s`(%(fields)s) VALUES \n" % {'table': fixture.table_name,
                                                                   'fields': ",".join(field_names)}
        count = 0
        for row in reader:
            count += 1
            query += "(" + ','.join(row) + "),\n"
        query = query[:-2]

        if count > 0:
            self.query_cache[fixture.file_path] = query
            return query
        else:
            return None

    def __run_query(self, query):
        """ Runs query in test db
        """
        db = self.__get_db()
        cursor = db.cursor()

        try:
            cursor.execute(query)
            db.commit()
        except:
            print "Fixture loader: Failed running query:" + query
        finally:
            cursor.close()

    def __clear_test_table(self, table_name):
        """ Clears/Truncates table in test database
        """
        db = self.__get_db()
        cursor = db.cursor()

        try:
            cursor.execute("TRUNCATE `" + table_name + "`")
            db.commit()
        except:
            print "Fixture loader: Failed clearing " + table_name
        finally:
            cursor.close()

    def __read_fixture_list(self, path):
        """ Reads fixtures file and lists all the files
            that have to be loaded
        """
        file = open(path + '/fixtures.txt', "r")

        names = []
        for line in file:
            names.append(path + '/' + line.strip())
        file.close()
        return names

    def __get_db(self):
        if self.db:
            return self.db
        else:
            self.db = conf.getAdminDbConnection()
            return self.db

    def __close_db(self):
        if self.db:
            self.db.close()
