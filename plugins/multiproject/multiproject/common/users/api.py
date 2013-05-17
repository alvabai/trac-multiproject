# -*- coding: utf-8 -*-
"""
Module contains the :py:class:`UserRestAPI` that provides the user listing based on search term in JSON format.
The functionality is being used in user autocomplete fields.

Get user::

    /<projectid>/api/user?id=234
    /<projectid>/api/user?username=accountname

Get list of users::

    /<projectid>/api/user/list?q=foo
    /<projectid>/api/user/list?q=foo&auth=localdb
    /<projectid>/api/user/list?q=foo&auth=localdb&field=username,lastname
    /<projectid>/api/user/list?q=foo&auth=localdb&field=username,lastname&status=expired
    /<projectid>/api/user/list?q=foo&auth=localdb&field=username,lastname&status=expired,banned,inactive
    /<projectid>/api/user/list?q=foo&auth=localdb&field=username,lastname&status=expired&perm=USER_MODIFY
    /<projectid>/api/user/list?q=foo&auth=localdb&field=username,lastname&status=expired&perm=USER_MODIFY&limit=5

.. note:: Backward compatibility

    Request also works with ``userautocomplete``::

        /<projectid>/userautocomplete?q=foo


Example response (depends on requested field):

.. code-block:: json

    [{'username':'Foo', 'lastname':'Bar'}, {'username':'Baz', 'lastname':'Huz'}]

.. NOTE::

    - Query: String that matches with the field values. The non-string fields (id, expires) are not included in search
      but only in results
    - Valid ``auth`` values are the organization keys, like: localdb, ldap..
    - Valid ``field`` values (separated with comma): id, username, firstname, lastname, email, mobile, expires
    - Valid ``status`` values (separated with comma): expired, banned, inactive, active, disabled
    - Valid ``perm`` value: Trac permission name, like ``USER_MODIFY``
    - Values are incasesensitive

"""
from trac.core import Component, implements
from trac.perm import PermissionCache
from trac.web import IRequestHandler
from trac.core import Interface

from multiproject.core.db import admin_query, safe_string, cursors, safe_int
from multiproject.core.users import get_userstore
from multiproject.core.restful import send_json
from multiproject.common.projects import HomeProject


class UserRestAPI(Component):
    """
    """
    implements(IRequestHandler)
    # Fields available for search
    # field name : db column name
    db_fields = {
        'id':'user_id',
        'username':'username',
        'firstname':'givenName',
        'lastname':'lastName',
        'email':'mail',
        'mobile':'mobile',
        'expires':'expires',
    }

    # Fields that are only shown for users with USER_ADMIN in home env
    sens_fields = (
        'mobile',
        'email',
        'expires',
    )

    # Fields that are in other type than varchar: cannot be collated
    nonchar_fields = (
        'id',
        'expires'
    )

    def match_request(self, req):
        """
        Path for listing users starting with "foo": ``/<projectid>/api/user/list?q=foo``
        Path for listing only local users: ``/<projectid>/api/user/list?q=foo&auth=localdb``
        Path for validating username or email before local user create: ``/<projectid>/api/validate/user?q=mail|q=username``
        """
        return req.path_info.startswith('/userautocomplete') or req.path_info.startswith('/api/user')

    def process_request(self, req):
        """
        Handles the incoming requests
        """

        if req.path_info.startswith('/api/username_or_email_exists'):
           return self._user_name_or_mail_exists(req)

        # Show single user
        if req.path_info.endswith('/api/user'):
            return self._show_user(req)

        return self._list_users(req)

    def _user_name_or_mail_exists(self, req):
        """
           Returns JSON representation for requested username or mail
        """

        query = req.args.get('q', '')[:100]

        if not query:
            self.log.exception("query string not given. %s" % query)
            return req.send('', status=404)

        userstore = get_userstore()
        recordExists = userstore.userNameOrMailExists(query)
        
        return send_json(req, recordExists)

    def _show_user(self, req):
        """
        Returns JSON presentation from the requested user
        """
        # NOTE: Limiting down the username
        user_id = req.args.get('id', '')[:100]
        username = req.args.get('username', '')[:100]

        if not any((user_id, username)):
            return req.send('', status=404)

        userstore = get_userstore()
        user = userstore.getUserWhereId(user_id) if user_id else userstore.getUser(username)
        if not user:
            return send_json(req, '', status=404)

        return send_json(req, user)

    def _list_users(self, req):
        """
        Process the ajax request for fetching users from database. Require at least
        two characters in the name string before allowing any values. Disallow % character
        and allow _ only as a normal character, that is part of the username.
        """
        name = req.args.get('q', '')
        auth = safe_string(req.args.get('auth', '').lower())
        perm = safe_string(req.args.get('perm', '').upper())
        limit = safe_int(req.args.get('limit', '30'))
        status = safe_string(req.args.get('status', '').lower())
        raw_fields = safe_string(req.args.get('field', 'username').lower())
        fields = [field for field in raw_fields.split(',') if field.strip() in self.db_fields.keys()]

        # If no fields or % in query => not allowed
        if not fields or '%' in name:
            return send_json(req, '', status=403)

        # Allow underscore in names/query
        name = safe_string(name).replace('_', '\_')
        states = [stat.lower() for stat in status.split(',') if stat]

        # Do the query
        rows = self._query_users(req, query=name, fields=fields, states=states, auth=auth, perm=perm, limit=limit)

        # Construct response in JSON list format
        # Serialize datetime objects into iso format: 2012-05-15T09:43:14
        return send_json(req, rows)

    def _query_users(self, req, query, fields, states=None, auth=None, perm=None, limit=None):
        """
        Implements the full search based on given parameters.
        Maximum number of results is 30

        :param str query: Search query matching into fields
        :param list fields:
            Name of fields where to search.

            .. NOTE:: Fields are combined for search, in provided order

        :param list states: Optional list of state names to include in search
        :param str auth: Optional name of authentication backend/organization to limit down the results
        :returns: List of results (each result presented as dictionary
        """
        rows = []

        home_perm = PermissionCache(HomeProject().get_env(), username=req.authname)
        default_limit = 30
        limit = int(limit or default_limit)

        # Search terms shorter than 2 - except for the persons with USER_AUTHOR perms
        if len(query) < 2 and 'USER_AUTHOR' not in home_perm:
            return []

        # Validate limit
        if limit > default_limit and 'USER_AUTHOR' not in home_perm:
            limit = default_limit

        # NOTE1: Fields are validated and escaped when reading from the request
        # Construct where: join fields so that we can search from all of them
        # NOTE2: Fields type other that varchar cannot be collated
        char_fields = [self.db_fields[field] for field in fields if field not in self.nonchar_fields]

        where = ["WHERE CONCAT_WS(' ', {0}) COLLATE utf8_general_ci LIKE '%{1}%'"
                 .format(','.join(char_fields), query.lower())]

        # Do not list special users
        where.append('u.username NOT IN ("anonymous", "authenticated")')

        # Limit down the results based on authentication method
        if auth:
            where.append("LOWER(auth.method) = '{0}'".format(auth))

        # Limit down the results based on status key
        if states:
            # Handle special status: expired
            if 'expired' in states:
                where.append("(u.expires IS NOT NULL AND u.expires <= NOW())")
                states.remove('expired')

            # If also other type of states defined
            if states:
                where.append("LOWER(us.status_label) IN ({0})".format(','.join(["'%s'" % safe_string(state) for state in states])))

        # Limit down per permissions
        # NOTE: This does not really check the Trac resource permission (it would be far too slow), just check the author_id
        # FIXME: Do proper check and cache permissions results do proper check?
        if perm and perm != 'USER_VIEW':
            # Limit results down everybody else but user admins
            if 'USER_ADMIN' not in home_perm:
                userstore = get_userstore()
                user = userstore.getUser(req.authname)
                where.append('(u.author_id = {0} OR u.user_id = {0})'.format(safe_int(user.id)))


        # Check if user is not home admin and remove private fields from query
        if 'USER_ADMIN' not in home_perm:
            for pfield in [pfield for pfield in self.sens_fields if pfield in fields]:
                fields.remove(pfield)

        # Construct SQL queries
        select_fields = ['{0} AS {1}'.format(self.db_fields[field], field) for field in fields]
        select_sql = ','.join(select_fields)
        where_sql = ' AND '.join(where)


        # SQL query for fetching username - in-casesentive
        sql = """
        SELECT {0}
        FROM user AS u
        LEFT JOIN authentication AS auth ON auth.id = u.authentication_key
        LEFT JOIN user_status AS us ON us.user_status_id = u.user_status_key
        {1}
        ORDER BY u.givenName, u.lastname, u.username
        LIMIT {2}
        """.format(select_sql, where_sql, limit)

        with admin_query(cursors.DictCursor) as cursor:
            try:
                cursor.execute(sql)
                rows = cursor.fetchall()
            except Exception:
                self.log.exception("Failed to get users with query %s" % sql)

        return rows


class IUserProfileActions(Interface):
    """
    Extension point registering user profile actions, based on given
    request and user.

    >>> from trac.core import Component, implements
    >>> from multiproject.common.users.api import IUserProfileActions
    >>>
    >>> class MyActionProvider(Component):
    >>>     implements(IUserProfileActions)
    >>>
    >>>     def get_profile_actions(self):
    >>>         return [
    >>>             tag.p('Can contain anything'),                          # Fragments are put in ul-li -list
    >>>             (0, tag.a('http://www.google.com'))                     # Default prioriority
    >>>             (-20, tag.a('http://www.google.com', id="important"))   # Higher in the action list
    >>>         ]

    """
    def get_profile_actions(req, user):
        """
        Function is expected to return actions to be shown
        for profile (:see:`multiproject.common.users.profile`)

        :param Request req: Trac request. Can be used for checking permissions for certain actions
        :param User user: User in question
        :returns:
            List of HTML fragments or optionally tuples (priority number, HTML fragment). If element
            is only a HTML fragment, it is considered a tuple with 0 priority (default)

        """
        return []
