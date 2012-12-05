# -*- coding: utf-8 -*-
"""
Database pooling, connection getter and utility class for multiproject

Internally, bound to MySQLdb, offers a singleton class transparently to caller, manages a
sqlalchemy pool as a private variable. Offers some database utilities, like connection
pooling and context managers to get cursor into a specified database.

Also has context managers for conveniently handling a connection specifically defined
databases, like ``trac_admin`` and ``trac_analytical`` database. Both of these database
names are configurable.
"""
from contextlib import contextmanager

from trac.db.api import DatabaseManager
import sqlalchemy.pool as dbpool
import MySQLdb

# Import commonly used into db namespace
from MySQLdb import cursors
from MySQLdb import escape_string

from multiproject.core.decorators import deprecated

# A private, module wide global database pool instance
_pool = None

def _get_pool():
    """
    Private function to get the database pool instance, or create one if it's not available yet.

    :returns: The connection pool instance
    """
    global _pool

    if _pool is None:
        # FIXME: Use pool size and other parameters from config
        _pool = dbpool.manage(MySQLdb, pool_size=1, use_threadlocal=True)

    return _pool

def safe_int(value):
    """
    Helper function to check and retrieve integer

    .. NOTE:: Please use cursor escaping instead where possible
    """
    real = None

    try:
        real = int(value)
    except:
        # Write a warning in log if this looks suspicious
        # NOTE: this import must remain here or circular import will occur
        from multiproject.core.configuration import Configuration
        conf = Configuration.instance()

        if value is not None:
            conf.log.warning("Failed validating '%s' as int" % str(value))

    return real

def safe_string(value):
    """
    Alias to :py:data:`MySQLdb.escape_string` to match with `safe_int`: Escapes the given string to be safe
    to replace in SQL query

    :param str value: SQL string to escape
    :returns: Escaped string
    """
    return escape_string(value)

def get_connection(db_name=''):
    """
    Get a database connection from pool. Raises (and logs) an exception if connection fails.
    Calling program needs to remember to close the connection after it is no longer needed.

    :param db_name: Optional database name to connect into
    :returns: Database connection, remember to call .close() for the connection when done
    """

    # Importing this here, since importing it globally would be a circular dependency
    # This use of configuration is bad, but better than importing the instanced global variable
    # from the module itself.
    from multiproject.core.configuration import Configuration
    conf = Configuration.instance()

    conn = None

    try:
        if not conf.use_alchemy_pool:
            conn = MySQLdb.connect(host=conf.db_host,
                                   user=conf.db_user,
                                   passwd=conf.db_password,
                                   port=int(conf.db_port),
                                   db=db_name,
                                   charset='utf8')
        else:
            conn = _get_pool().connect(host=conf.db_host,
                                       user=conf.db_user,
                                       passwd=conf.db_password,
                                       port=int(conf.db_port),
                                       db=db_name,
                                       charset='utf8')
    except Exception:
        conf.log.exception("Failed to open database connection to db '%s'" % db_name)
        raise

    return conn


def debug_db_execute(fn):
    """
    Simple debugger for database queries: use this function to patch the
    original db cursor.execute::

        def db_query(db_name='', cursor_type=None):
            conn = get_connection(db_name)
            cursor = conn.cursor(cursor_type)
            # PATCH!
            cursor.execute = debug_db_execute(cursor.execute)
            yield cursor

    As outcome, all the queries are logged for further analysis

    .. important::

        Do *not* enable this in production environment!

    """
    import re
    import traceback
    from datetime import datetime
    from multiproject.core.configuration import Configuration

    stack_depth = 5
    conf = Configuration.instance()
    reprex = re.compile('\\n\s*')

    def execute(*args, **kwargs):
        query = [reprex.sub(' ', str(arg)).strip() for arg in args]
        before = datetime.utcnow()

        # Run the actual query
        output = fn(*args, **kwargs)

        # Log output:
        diff = datetime.utcnow() - before
        diffs = str(diff).rsplit(':', 1)[1]

        # Raise exception to get execute information
        try:
            raise Exception('traceback')
        except Exception:
            trace = traceback.extract_stack(limit=stack_depth)
            conf.log.error('SQL: %s, %s (took: %s sec, stack: %s)' % (query, kwargs, diffs, trace[:-1]))

        return output

    return execute


@contextmanager
def db_query(db_name='', cursor_type=None):
    """
    Context manager for making a query into a specific database. This context manager
    creates a connection to the specified database and yields a cursor to the database.

    After user is done, the connection is closed automatically (or returned to pool).

    :param db_name: Optional name of the database to get the cursor for reading
    :param cursor_type: Optional cursor type

    .. NOTE::

        This context manager is meant for read-only operations into database. If you want
        automatic commits and rollbacks, use db_transaction(), admin_transaction() or
        analytical_transaction().

    Example::

        def some_function():
            row = []
            with db_query('trac_admin') as cursor:
                query = "SELECT * FROM users WHERE username LIKE %s"
                cursor.execute(query, 'mika%')
                row = cursor.fetchall()

            # Do something

    """
    from multiproject.core.configuration import Configuration
    conf = Configuration.instance()

    conn = None
    cursor = None

    try:
        conn = get_connection(db_name)
    except Exception:
        conf.log.error('Failed to get db connection for queries to %s' % db_name)
        raise

    try:
        cursor = conn.cursor(cursor_type)
        # Uncomment for debugging
        #cursor.execute = debug_db_execute(cursor.execute)
        yield cursor
    except Exception:
        conf.log.exception('Exception in db_query(%s)' % db_name)
        raise
    finally:
        cursor.close()
        conn.close()


@contextmanager
def db_transaction(db_name=''):
    """
    Context manager for doing an update, insert, delete or some other transaction
    into a database. This will take care of providing cursor and taking a connection for
    the database for the calling code. After everything is done, the cursor and connection
    are disposed. If no exception is returned, all changes to database are committed. If
    an exception is raised, changes are rolled back.

    :param db_name: Name of the database to get the cursor for modifying

    Example::

        def some_function():
            data = (1, 2, 3)
            with admin_transaction() as cursor:
                try:
                    cursor.execute("DELETE ...", data)
                except Exception:
                    conf.log.exception("Failed to delete...")
                    raise
                return
     """
    from multiproject.core.configuration import Configuration
    conf = Configuration.instance()

    conn = None
    cursor = None

    try:
        conn = get_connection(db_name)
    except Exception:
        conf.log.error('Failed to get database connection for transactions to db %s' % db_name)
        raise

    # Simple fallbacking from commit to rollback
    try:
        cursor = conn.cursor()
        # Uncomment for debugging
        #cursor.execute = debug_db_execute(cursor.execute)
        yield cursor
        conn.commit()
    except Exception:
        conf.log.error('Exception in db_transaction(%s), running rollback' % db_name)
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


@contextmanager
def admin_query(cursor_type=None):
    """
    Context manager implementation for getting a configured ``trac_admin`` database cursor
    for executing a query into database. This handles exceptions for users and in the end
    closes the connection.

    :param cursor_type: Optional MySQLdb cursor type

    For more example on how to use this, see db_query()
    """
    from multiproject.core.configuration import Configuration
    conf = Configuration.instance()

    with db_query(conf.db_admin_schema_name, cursor_type) as cursor:
        try:
            yield cursor
        except Exception:
            conf.log.exception('Exception in admin_query()')
            raise


@contextmanager
def admin_transaction():
    """
    Context manager for doign an update, insert, delete or some other transaction
    into ``trac_admin`` database. This will take care of providing cursor and taking
    a connection for the database for the calling code. After everything is done, the
    cursor and connection are disposed.

    For example of use and more details, see db_transaction()
    """
    from multiproject.core.configuration import Configuration
    conf = Configuration.instance()

    with db_transaction(conf.db_admin_schema_name) as cursor:
        try:
            yield cursor
        except Exception:
            conf.log.exception('Exception in admin_transaction()')
            raise


@contextmanager
def analytical_query(cursor_type=None):
    """
    Context manager implementation for getting a configured ``trac_analytical`` database cursor
    for executing a query into database. This handles exceptions for users and in the end
    closes the connection.

    :param cursor_type: Optional MySQLdb cursor type

    For more example on how to use this, see db_query()
    """
    from multiproject.core.configuration import Configuration
    conf = Configuration.instance()

    with db_query(conf.db_analytical_schema_name, cursor_type) as cursor:
        try:
            yield cursor
        except Exception:
            conf.log.error('Exception in analytics_query()')
            raise


@contextmanager
def analytical_transaction():
    """
    Context manager for doign an update, insert, delete or some other transaction
    into ``trac_analytical`` database. This will take care of providing cursor and taking
    a connection for the database for the calling code. After everything is done, the
    cursor and connection are disposed.

    For example of use and more details, see db_transaction()
    """
    from multiproject.core.configuration import Configuration
    conf = Configuration.instance()

    with db_transaction(conf.db_analytical_schema_name) as cursor:
        try:
            yield cursor
        except Exception:
            conf.log.error('Exception in analytics_transaction()')
            raise


@contextmanager
def trac_db_query(env):
    """
    Context manager to handle database connection and cursor from trac environment's
    read only connection. This does not attempt to roll back or commit, the connection
    is meant only for accessing the data. For examples on use, see db_query().

    Internally, this uses Trac's connection pool via the Trac DatabaseManager class

    :param Environment env: The Trac environment
    """
    conn = None
    cursor = None

    try:
        dm = DatabaseManager(env)
        conn = dm.get_connection()
    except Exception:
        env.log.exception("Failed to get database connection from trac database manager")
        raise

    try:
        # NOTE: Trac's connection does not support alternative cursor types!
        cursor = conn.cursor()
        yield cursor
    except Exception:
        env.log.error("Failed to query database")
        raise
    finally:
        cursor.close()
        conn.close()


@contextmanager
def trac_db_transaction(env):
    """
    Context manager to handle database connection and cursor from trac environment's
    read / write connection. This handles automatic commits, rollbacks and connection
    closing.

    Internally, this uses Trac's connection pool via the Trac DatabaseManager class.
    This is because it would appear that to multiproject uses, Trac's with_transaction()
    is not sufficient.

    For examples of use, see db_transaction()

    :param Environment env: The Trac Environment in use.
    """
    conn = None
    cursor = None

    try:
        dm = DatabaseManager(env)
        conn = dm.get_connection()
    except Exception:
        env.log.exception("Failed to get database connection from trac database manager")
        raise

    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception:
        env.log.error("Failed to perform transaction to database")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


# Deprecated API
@deprecated
def operational_conn():
    """
    Get a connection to ``trac_admin`` database.

    .. NOTE::

        DEPRECATED: Use either get_connection() or context managers admin_query()
        or admin_transaction()
    """
    from multiproject.core.configuration import Configuration
    return get_connection(Configuration.instance().db_admin_schema_name)


@deprecated
def analytical_conn():
    """
    Get a connection to ``trac_admin`` database.

    .. NOTE::

        DEPRECATED: Use either get_connection() or context managers analytical_query()
        or analytical_transaction()
    """
    from multiproject.core.configuration import Configuration
    return get_connection(Configuration.instance().db_analytical_schema_name)


@deprecated
def single_analytical_db_result(query, params = None):
    try:
        with analytical_query() as cursor:
            return _single_db_result(cursor, query, params)
    except:
        pass

    return None


@deprecated
def single_operational_db_result(query, params = None):
    try:
        with admin_query() as cursor:
            return _single_db_result(cursor, query, params)
    except:
        pass

    return None


@deprecated
def multi_analytical_db_result(query, params = None):
    try:
        with analytical_query() as cursor:
            return _multi_db_result(cursor, query, params)
    except:
        pass

    return None


@deprecated
def multi_operational_db_result(query, params = None):
    try:
        with admin_query() as cursor:
            return _multi_db_result(cursor, query, params)
    except:
        pass

    return None


@deprecated
def commit_to_analytical(query, params = None):
    try:
        with admin_transaction() as cursor:
            return _commit_change(cursor, query, params)
    except:
        pass

    return False


@deprecated
def commit_to_operational(query, params = None):
    try:
        with admin_transaction() as cursor:
            return _commit_change(cursor, query, params)
    except:
        pass

    return False


@deprecated
def operational_db_procedure(procedure, params = None):
    try:
        with admin_transaction() as cursor:
            return _procedure_call(cursor, procedure, params)
    except:
        pass

    return False


@deprecated
def analytical_db_procedure(procedure, params = None):
    try:
        with analytical_transaction() as cursor:
            return _procedure_call(cursor, procedure, params)
    except:
        pass

    return False


@deprecated
def multi_operational_result_procedure(procedure, params = None):
    try:
        with admin_query() as cursor:
            return _result_procedure_call(cursor, procedure, params)
    except:
        pass

    return None


@deprecated
def multi_analytical_result_procedure(procedure, params = None):
    try:
        with analytical_query() as cursor:
            return _result_procedure_call(cursor, procedure, params)
    except:
        pass

    return None


# Private
def _single_db_result(cursor, query, params = None):
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
    except:
        from multiproject.core.configuration import conf
        conf.log.exception("Query failed: %s" % query)
        raise

    return cursor.fetchone()


def _multi_db_result(cursor, query, params = None):
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
    except:
        from multiproject.core.configuration import conf
        conf.log.exception("Query failed: %s" % query)
        raise

    return cursor.fetchall()


def _commit_change(cursor, query, params = None):
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
    except:
        from multiproject.core.configuration import conf
        conf.log.exception("Query failed: %s" % query)
        raise

    return True


def _procedure_call(cursor, procedure, params = None):
    try:
        if params:
            cursor.callproc(procedure, params)
        else:
            cursor.callproc(procedure)
    except:
        from multiproject.core.configuration import conf
        conf.log.exception("Procedure call failed: %s" % procedure)
        return False

    return True


def _result_procedure_call(cursor, procedure, params = None):
    try:
        if params:
            cursor.callproc(procedure, params)
        else:
            cursor.callproc(procedure)
    except:
        from multiproject.core.configuration import conf
        conf.log.exception("Procedure call failed: %s" % procedure)
        raise

    return cursor.fetchall()
