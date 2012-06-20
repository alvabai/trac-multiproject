# -*- coding: utf-8 -*-
import MySQLdb, datetime, urllib

from multiproject.core.configuration import conf
from multiproject.core.permissions import CQDEAuthenticationStore
from multiproject.core.db import analytical_query, analytical_transaction, admin_query, safe_string, safe_int
from multiproject.core.users import get_userstore


def now_str():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


class UserDimension(object):
    """ Model class for user dimension
    """
    authentications = {}
    sk_cache = {}

    def __init__(self):
        self._init_active_user_sks()
        self._init_known_authentications()

    def _init_active_user_sks(self):
        """ Returns a list of users that are
            active {username => user_sk}
        """
        query = "SELECT username, user_sk FROM user_dim WHERE VALID_TO IS NULL"
        with analytical_query() as cursor:
            try:
                cursor.execute(query)
                for row in cursor:
                    self.sk_cache[row[0]] = row[1]
            except:
                conf.log.exception("Failed reading user surrogate keys with query '%s'" % query)

    def _init_known_authentications(self):
        """ Lazy load authentications and store them
            locally to reduce sql
        """
        auth_store = CQDEAuthenticationStore.instance()
        auths = auth_store.get_authentications()

        for auth in auths:
            self.authentications[auth.id] = auth.name
        self.authentications[None] = '<No authentication>'

    def user_sk(self, username):
        if username in self.sk_cache:
            return self.sk_cache[username]

        return self.new(username)

    def new(self, username):
        """ Create new dimension record from user
        """
        user = self.from_operational(username)
        if not user:
            return None

        # Current time for user
        user['now'] = now_str()

        user_insert = """
        INSERT INTO user_dim(user_sk,
                     username,
                     mail,
                     mobile,
                     givenName,
                     lastName,
                     authentication,
                     status,
                     user_key,
                     VALID_FROM)
        VALUES(null,
           '%(username)s',
           '%(mail)s',
           '%(mobile)s',
           '%(givenName)s',
           '%(lastName)s',
           '%(authentication)s',
           '%(status)s',
           %(user_key)d,
           '%(now)s')""" % user

        invalidate_old = """
        UPDATE user_dim SET VALID_TO = '%(now)s'
        WHERE username = '%(username)s' AND VALID_TO IS NULL""" % user

        with analytical_transaction() as cursor:
            try:
                cursor.execute(invalidate_old)
                cursor.execute(user_insert)
            except:
                conf.log.exception("Failed creating a new user record to dimension. %s" % str(user))
                raise

        return self.get_active_user_sk(username)

    def get_active_user_sk(self, username):
        query = """
        SELECT user_sk
        FROM user_dim
        WHERE username = '%s' AND VALID_TO IS NULL""" % username

        row = []
        with analytical_query() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone()
            except:
                conf.log.exception("Failed reading users surrogate key. %s" % username)

        if not row:
            return None

        self.sk_cache[username] = row[0]
        return row[0]

    def from_operational(self, username):
        """ Return user from operational database
        """
        userstore = get_userstore()
        user = userstore.getUser(username)
        if not user:
            return None

        authentication = self.authentications[user.authentication_key]
        denormalized_user = {
            'username': user.username,
            'mail': user.mail,
            'mobile': user.mobile,
            'givenName': user.givenName,
            'lastName': user.lastName,
            'authentication': authentication,
            'status': userstore.USER_STATUS_LABELS[user.status],
            'user_key': user.id
        }
        return denormalized_user

    def from_analytical(self, username):
        """ Return user from analytical database
        """
        query = """
        SELECT username, mail, mobile, givenName,
               lastName, authentication, status, user_key
        FROM user_dim
        WHERE username = %s AND VALID_TO IS NULL
        """

        row = []
        with analytical_query() as cursor:
            try:
                cursor.execute(query, username)
                row = cursor.fetchone()
            except:
                conf.log.exception("Failed reading user from operational database. username : %s" % username)

        if not row:
            return None

        user = {
            'username': row[0],
            'mail': row[1],
            'mobile': row[2],
            'givenName': row[3],
            'lastName': row[4],
            'authentication': row[5],
            'status': row[6],
            'user_key': row[7]
        }
        return user

    def sync_all(self):
        for username in self.sk_cache.keys():
            self.sync(username)

    def sync(self, username):
        """ SCD2 : Create new record if user has changed
            in operational database
        """
        if not self.is_in_sync(username):
            self.new(username)

    def is_in_sync(self, username):
        """ Test if user in analytical db match
        """
        A = self.from_analytical(username)
        B = self.from_operational(username)
        if None in [B, A]:
            return False

        return A == B


class ProjectDimension(object):
    sk_cache = {}

    def __init__(self):
        self._read_project_surrogate_keys()

    def _read_project_surrogate_keys(self):
        query = "SELECT identifier, project_sk FROM project_dim WHERE VALID_TO IS NULL"

        with analytical_query() as cursor:
            try:
                cursor.execute(query)
                for row in cursor:
                    self.sk_cache[row[0]] = row[1]
            except:
                conf.log.exception("Failed reading project surrogate keys")

    def project_sk(self, identifier):
        if identifier in self.sk_cache:
            return self.sk_cache[identifier]

        return self.new(identifier)

    def new(self, identifier):
        """ Create new dimension record from project
        """
        project = self.from_operational(identifier)
        if not project:
            return None

        # Current time for project
        project['now'] = now_str()

        project_insert = """
        INSERT INTO project_dim(project_sk,
                     identifier,
                     project_name,
                     author,
                     created,
                     updated,
                     published,
                     project_key,
                     VALID_FROM)
        VALUES(null,
           '%(identifier)s',
           '%(project_name)s',
           '%(author)s',
           '%(created)s',
           '%(updated)s',
           '%(published)s',
           '%(project_key)s',
           '%(now)s')""" % project

        invalidate_old = """
        UPDATE project_dim SET VALID_TO = '%(now)s'
        WHERE identifier = '%(identifier)s' AND VALID_TO IS NULL""" % project

        with analytical_transaction() as cursor:
            try:
                cursor.execute(invalidate_old)
                cursor.execute(project_insert)
            except Exception:
                conf.log.exception("Failed creating a new project record to dimension. insert: %s\nupdate:%s" %
                                        (project_insert, invalidate_old))
                raise

        return self.get_active_project_sk(identifier)

    def get_active_project_sk(self, identifier):
        query = """
        SELECT project_sk
        FROM project_dim
        WHERE identifier = '%s' AND VALID_TO IS NULL""" % identifier

        row = []
        with analytical_query() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone()
            except:
                conf.log.exception("Getting project sk failed. project identifier : %s" % identifier)

        if not row:
            return None

        self.sk_cache[identifier] = row[0]
        return row[0]

    def from_operational(self, identifier):
        """ Read a project from operational database
        """
        query = """
        SELECT  p.environment_name AS identifier,
                p.project_name,
                u.username AS author,
                p.created,
                p.updated,
                p.published,
                p.project_id
        FROM projects AS p
        INNER JOIN user AS u ON u.user_id = p.author
        WHERE p.environment_name = '%s'""" % identifier

        row = []
        with admin_query() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone()
            except:
                conf.log.exception("Getting project from operational db failed. %s" % identifier)

        if not row:
            return None

        project = {'identifier': row[0],
                   'project_name': MySQLdb.escape_string(row[1]),
                   'author': MySQLdb.escape_string(row[2]),
                   'created': row[3],
                   'updated': row[4],
                   'published': row[5],
                   'project_key': row[6]}

        return project

    def from_analytical(self, identifier):
        """ Return project from analytical database
        """
        query = """
        SELECT identifier, project_name, author, created,
               updated, published, project_key
        FROM project_dim
        WHERE identifier = '%s' AND VALID_TO IS NULL""" % identifier

        row = []
        with analytical_query() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone()
            except:
                conf.log.exception("Getting project from analytical db failed. project identifier : %s" %
                                        identifier)

        if not row:
            return None

        project = {'identifier': MySQLdb.escape_string(row[0]),
                   'project_name': MySQLdb.escape_string(row[1]),
                   'author': MySQLdb.escape_string(row[2]),
                   'created': row[3],
                   'updated': row[4],
                   'published': row[5],
                   'project_key': row[6]}
        return project

    def sync_all(self):
        for identifier in self.sk_cache.keys():
            self.sync(identifier)

    def sync(self, identifier):
        """ SCD2 : Create new record if user has changed
            in operational database
        """
        if not self.is_in_sync(identifier):
            self.new(identifier)

    def is_in_sync(self, identifier):
        """ Test if user in analytical db match
        """
        A = self.from_analytical(identifier)
        B = self.from_operational(identifier)
        if None in [B, A]:
            return False

        return A == B


class DiscussionDimension(object):
    sk_cache = {}

    def __init__(self):
        row = self._inapplicable_sk_row()
        if row:
            self.inapplicable_sk = row[0]
        else:
            conf.log.warning("Didn't find <Inapplicable> sk row")
            self.inapplicable_sk = []
        self._read_discussion_surrogate_keys()

    def cache_key(self, project_identifier, forum_id):
        return "%s.%d" % (project_identifier, forum_id)

    def _read_discussion_surrogate_keys(self):
        query = "SELECT project_identifier, forum_key, project_key FROM discussion_dim WHERE VALID_TO IS NULL"
        with analytical_query() as cursor:
            try:
                cursor.execute(query)
                for row in cursor:
                    cache_key = self.cache_key(row[0], row[1])
                    self.sk_cache[cache_key] = row[2]
            except:
                conf.log.exception("Failed reading discussion surrogate keys")

    def discussion_sk(self, project_identifier, forum_id):
        # Try from memory
        cache_key = self.cache_key(project_identifier, forum_id)
        if cache_key in self.sk_cache:
            return self.sk_cache[cache_key]

        # Not in memory, try from analytics db
        sk = self.get_active_discussion_sk(project_identifier, forum_id)
        if sk:
            return sk

        # Not in analytics db, try building a new from operational
        sk = self.new(project_identifier, forum_id)
        return sk

    def new(self, project_identifier, forum_id):
        dibo = self.from_operational(project_identifier, forum_id)

        if not dibo:
            return None

        dibo['now'] = now_str()

        dibo_insert = """
        INSERT INTO discussion_dim(discussion_sk,
                     discussion_name,
                     author,
                     moderators,
                     subscribers,
                     subject,
                     description,
                     forum_key,
                     project_key,
                     project_name,
                     project_identifier,
                     VALID_FROM)
        VALUES(null,
           '%(discussion_name)s',
           '%(author)s',
           '%(moderators)s',
           '%(subscribers)s',
           '%(subject)s',
           '%(description)s',
            %(forum_key)d,
            %(project_key)d,
           '%(project_name)s',
           '%(project_identifier)s',
           '%(now)s')""" % dibo

        invalidate_old = """
        UPDATE discussion_dim SET VALID_TO = '%(now)s'
        WHERE project_key = %(project_key)d AND forum_key = %(forum_key)d
        AND VALID_TO IS NULL""" % dibo

        with analytical_transaction() as cursor:
            try:
                cursor.execute(invalidate_old)
                cursor.execute(dibo_insert)
            except:
                conf.log.exception("Failed creating a new record to discussion dimension. %s" % str(dibo))
                raise

        return self.get_active_discussion_sk(project_identifier, forum_id)

    def get_active_discussion_sk(self, project_identifier, forum_id):
        query = """
        SELECT discussion_sk
        FROM discussion_dim
        WHERE project_identifier = '%s' AND forum_key = %d
        AND VALID_TO IS NULL""" % (project_identifier, forum_id)

        row = []
        with analytical_query() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone()
            except:
                conf.log.exception("Getting discussion surrogate key failed. {project: %s, forum: %d}" %
                                        (project_identifier, forum_id))

        if not row:
            return None

        cache_key = "%s.%d" % (project_identifier, forum_id)
        self.sk_cache[cache_key] = row[0]
        return row[0]

    def from_operational(self, project_identifier, forum_id):
        # Alternative way to do this would be to open the connection straight into the project database...
        query = """
        SELECT id, name, author, moderators, subscribers, subject, description
        FROM %(project_identifier)s.forum WHERE id = %(forum_id)s
        """ % {'project_identifier': safe_string(project_identifier), 'forum_id': safe_int(forum_id)}

        dibo = None
        with admin_query() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone()
                if not row:
                    return None
                dibo = {'forum_key':row[0],
                        'discussion_name':row[1],
                        'author':row[2],
                        'moderators':row[3],
                        'subscribers':row[4],
                        'subject':row[5],
                        'description':row[6]
                }
            except:
                conf.log.exception("Failed reading a record from discussion dimension. %s" % str(dibo))

        pd = ProjectDimension()
        project = pd.from_operational(project_identifier)
        dibo['project_key'] = project['project_key']
        dibo['project_identifier'] = project['identifier']
        dibo['project_name'] = project['project_name']
        return dibo

    def from_analytical(self, project_identifier, forum_id):
        """ Return user from analytical database
        """
        query = """
        SELECT forum_key, discussion_name, author, moderators, subscribers,
               subject, description, project_key, project_identifier, project_name
        FROM discussion_dim
        WHERE project_identifier = '%s' AND forum_key = %d
        AND VALID_TO IS NULL""" % (safe_string(project_identifier), safe_int(forum_id))

        row = []
        with analytical_query() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone()
            except:
                conf.log.exception(
                    "Failed reading discussion forum from analytical db. {project: %s, forum: %d}" %
                    (project_identifier, forum_id))

        if not row:
            return None

        project = {'forum_key': row[0],
                   'discussion_name': MySQLdb.escape_string(row[1]),
                   'author': MySQLdb.escape_string(row[2]),
                   'moderators': MySQLdb.escape_string(row[3]),
                   'subscribers': MySQLdb.escape_string(row[4]),
                   'subject': MySQLdb.escape_string(row[5]),
                   'description': MySQLdb.escape_string(row[6]),
                   'project_key': row[7],
                   'project_identifier': MySQLdb.escape_string(row[8]),
                   'project_name': MySQLdb.escape_string(row[9])
        }
        return project

    def sync_all(self):
        """ Use SCD 2 for discussion sync
        """
        for cache_key in self.sk_cache.keys():
            project_identifier, forum_id = cache_key.split('.')
            self.sync(project_identifier, int(forum_id))

    def sync(self, project_identifier, forum_id):
        """ SCD2 : Create new record if user has changed
            in operational database
        """
        if not self.is_in_sync(project_identifier, forum_id):
            self.new(project_identifier, forum_id)

    def is_in_sync(self, project_identifier, forum_id):
        """ Test if user in analytical db match
        """
        A = self.from_analytical(project_identifier, forum_id)
        B = self.from_operational(project_identifier, forum_id)
        if None in [B, A]:
            return False

        return A == B

    def _inapplicable_sk_row(self):
        query = """
            SELECT discussion_sk FROM discussion_dim
            WHERE project_identifier = '<Inapplicable>'
              AND discussion_name = '<Inapplicable>'"""
        row = []
        with analytical_query() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone()
            except:
                conf.log.exception("Getting inapplicable discussion sk failed")

        return row


class DateDimension(object):
    date_cache = {}

    def date_sk(self, sql_date_string):
        """ From python date to date_sk
        """
        query = """
        SELECT date_sk FROM date_dim
        WHERE date = '%s'
        """ % sql_date_string[:10]

        row = []
        with analytical_query() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone()
            except:
                conf.log.exception("Getting date surrogate key failed. %s" % sql_date_string)

        if not row:
            return None

        return row[0]

    def datetime_to_sql(self, date):
        """ Return a string from date that can be used
            in sql query
        """
        return date.strftime("%Y-%m-%d")

    def date_sk_utcnow(self):
        sql_date = self.datetime_to_sql(datetime.datetime.utcnow())
        return self.date_sk(sql_date)


class EventDimension(object):
    """ Class for querying and managing event
        dimension data
    """
    key_cache = {}

    def event_sk(self, action):
        """ From event/action name to
            event surrogate key
        """
        if action in self.key_cache:
            return self.key_cache[action]

        query = "SELECT event_sk FROM event_dim WHERE action_name = '%s' AND VALID_TO IS NULL" % action
        row = []
        with analytical_query() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone()
            except:
                conf.log.exception("Getting event surrogate key failed. %s" % action)

        if not row:
            return None

        event_sk = row[0]
        self.key_cache[action] = event_sk

        return event_sk


class ContextDimension(object):
    """ Class for querying and managing event
        dimension data
    """
    home_exact_cache = {}
    project_exact_cache = {}

    home_prefix_cache = {}
    project_prefix_cache = {}

    def __init__(self):
        self._init_sk_cache()

    def _init_sk_cache(self):
        """ Reads all the surrogate keys from the database
        """
        with analytical_query() as cursor:
            try:
                query = """SELECT context_sk, context, environment_type, path_info FROM context_dim"""
                cursor.execute(query)
                for row in cursor:
                    is_home = row[2] == 'home'
                    is_prefix = row[3].endswith('.*')
                    sk = row[0]

                    if is_home and is_prefix:
                        self.home_prefix_cache[row[3][:-2]] = sk
                        continue
                    if is_home and not is_prefix:
                        self.home_exact_cache[row[3]] = sk
                        continue

                    if not is_home and is_prefix:
                        self.project_prefix_cache[row[3][:-2]] = sk
                        continue
                    if not is_home and not is_prefix:
                        self.project_exact_cache[row[3]] = sk
                        continue
            except:
                conf.log.exception("Failed reading context sk")

    def context_sk(self, project_identifier, path_info):
        """ From event/action name to
            event surrogate key
        """
        path_info = urllib.quote(path_info)

        # To simplify things, we allow only first part of the path for now
        environment_type = self._environment_type(project_identifier)

        if not path_info.startswith('/'):
            return None

        # Try exact match
        sk = self._try_exact_sk(environment_type, path_info)

        # Try prefix match
        if not sk:
            sk = self._try_prefix_sk(environment_type, path_info)

        # build a new one (Will be built with the best guess)
        if not sk:
            sk = self.new(environment_type, path_info)

        return sk

    def _try_exact_sk(self, environment_type, path_info):
        cache = self._get_exact_cache(environment_type)
        # Try from cache
        if path_info in cache:
            return cache[path_info]
        return None

    def _get_exact_cache(self, environment_type):
        if environment_type == 'home':
            return self.home_exact_cache
        else:
            return self.project_exact_cache

    def _get_prefix_cache(self, environment_type):
        if environment_type == 'home':
            return self.home_prefix_cache
        else:
            return self.project_prefix_cache

    def _environment_type(self, project_identifier):
        is_home = project_identifier == 'home'
        if is_home:
            return 'home'
        else:
            return 'project'

    def _try_prefix_sk(self, environment_type, path_info):
        cache = self._get_prefix_cache(environment_type)

        # Find the best match
        match = ''
        for key in cache.keys():
            if path_info.startswith(key) and len(key) > len(match):
                match = key

        if not match:
            return None

        # Return match
        return cache[match]

    def new(self, environment_type, path_info):
        conf.log.warning("New context created, Check your db! '%s', '%s'" % (environment_type, path_info))
        insert_new = "INSERT INTO context_dim VALUES(null, %s, %s, %s, %s, null)"

        new_id = None
        with analytical_transaction() as cursor:
            try:
                now = now_str()

                # We don't know the context name so lets just use first part of the path info
                path_info = '/'.join(path_info.split('/')[:2])
                context = path_info
                path_info += '.*'
                cursor.execute(insert_new, (context, environment_type, path_info, now))
                cursor.execute("SELECT last_insert_id() FROM context_dim LIMIT 1")
                row = cursor.fetchone()
                if row and len(row) > 0:
                    new_id = row[0]

                    is_home = environment_type == 'home'
                    cache = {True: self.home_prefix_cache, False: self.project_prefix_cache}[is_home]
                    cache[context] = row[0]
            except:
                conf.log.exception("Failed creating a new record to context dimension. %s" % str(path_info))
                raise

        return new_id
