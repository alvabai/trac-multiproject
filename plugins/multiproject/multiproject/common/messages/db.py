# -*- coding: utf-8 -*-
"""
Module contains the DAO model/python API for MultiProject messages:

- :py:class:`Message`: One message sent by user to specified message group
- :py:class:`MessageGroup`: Groups a set of users in single group. Messages are always sent to group, not a single user.
  Then again, private messages are sent to group of two users.

Notifications are managed in :py:mod:`multiproject.common.notifications.push`

"""
import logging
from datetime import datetime

from multiproject.core.db import admin_query, admin_transaction, cursors, safe_int, safe_string
from multiproject.core.users import get_userstore, User


class Message(object):
    """
    Object for modelling the database entry: message

    >>> msg = Message()
    >>> msg.sender_id = 123
    >>> msg.receivers = [432, 123]
    >>> msg.message_group_id = 2
    >>> msg.content = "Hello there!"
    >>> msg.save()
    >>>
    >>> msg = Message.get(12)
    >>> msg.delete()

    """
    # Mapping: property:dbfield
    FIELDS = {
        'id': 'id',
        'sender_id': 'sender_id',
        'group_id': 'message_group_id',
        'created': 'created',
        'content': 'content',
        'env': 'env',
    }

    FLAG_DELETED = 0
    FLAG_ACCESS = 1
    FLAG_STARRED = 2

    def __init__(self):
        # Private properties
        self._sender = None

        # Properties
        self.id = None
        self.sender_id = None
        self.group_id = None
        self.created = datetime.utcnow()
        self.updated = None
        self.content = None
        self.env = None

    def save(self):
        """
        Saves the changes in properties into database

        >>> msg = Message()
        >>> msg.sender_id = 123
        >>> msg.save()

        """
        # Create new message
        if not self.id:
            sql = '''
            INSERT INTO message
            SET {0}
            '''.format(', '.join(['{0}=%s'.format(field) for field in self.FIELDS.values()]))

            with admin_transaction() as cursor:
                cursor.execute(sql, [getattr(self, pro) for pro in self.FIELDS.keys()])

                # Set id information to Message
                self.id = cursor.lastrowid

        # Update existing message
        else:
            self.updated = datetime.utcnow()

            # Construct SQL update statement using db fields and setting %s placeholder for values
            sql = '''
            UPDATE message
            SET {0}
            WHERE id = %s
            '''.format(', '.join(['{0}=%s'.format(field) for field in self.FIELDS.values()]))

            with admin_transaction() as cursor:
                cursor.execute(sql, ([getattr(self, pro) for pro in self.FIELDS.keys()] + [self.id]))

        logging.info('Saved message {0} into database'.format(self))

    def delete(self):
        """
        Deletes the message from the database
        """
        sql = 'DELETE FROM message WHERE id = %s'
        with admin_transaction() as cursor:
            cursor.execute(sql, self.id)

        logging.info('Deleted message {0} from database'.format(self))

    def set_flags(self, user_ids, flags):
        """
        Sets a flag(s) to message. See FLAG_* variables

        :param tuple user_ids: Tuple or List of user ids. Number of ids must match with flags
        :param tuple flags: Tuple or list of flags. Number of ids must match with user ids

        >>> m = Message()
        >>> m.set_flags([user_ids=(124, 124, 10), flags=(FLAG_STARRTED, FLAG_VISIBLE, FLAG_DELETED))

        """
        # Map ids for multiple insert. Multiple message ids
        data = zip([self.id]*len(user_ids), user_ids, flags)

        sql = '''
        INSERT IGNORE INTO message_flag (message_id, user_id, flag)
        VALUES (%s, %s, %s)
        '''
        with admin_transaction() as cursor:
            cursor.executemany(sql, data)

    def set_flag(self, user_id, flag):
        """
        Set single flag to single user.
        Convenience function to :meth:`Message.set_flags`

        :param user_id: User id
        :param flag: Flag id, see Message.FLAG_* variables
        """
        return self.set_flags(user_ids=(user_id,), flags=(flag,))

    def unset_flag(self, user_id, flag):
        """
        Removes a flag from message. See FLAG_* variables

        :param int user_id: Id of the user who is to be flagged
        :param int flag: Flag value (removes the matching flag)
        """
        sql = '''
        DELETE FROM message_flag
        WHERE id = %s AND user_id = %s AND flag = %s
        '''
        with admin_transaction() as cursor:
            cursor.execute(sql, (self.id, user_id, flag))

    def __json__(self):
        """
        Returns dictionary presentation of the object, suitable for JSON.
        Example output::

            {
            'id': 123,
            'content': 'My message to you',
            'sender: {'id': 532, 'username': 'myaccount'},
            'group: {'id': 4, 'user_ids': [123, 300, 152]}
            }

        """
        return {
            'id': self.id,
            'content': self.content,
            'sender': None if self.sender is None else {'id':self.sender.id, 'username':self.sender.username},
            'recipients': self.recipients,
            'group': {'id': self.group_id},
            'created': self.created,
            'env': self.env,
            'notifications': getattr(self, 'notifications', []) # Support for notifications
        }

    @property
    def sender(self):
        """
        Property for getting message sender

        :returns: User instance of the project author
        """
        if self._sender:
            return self._sender

        userstore = get_userstore()
        self._sender = userstore.getUserWhereId(self.sender_id)

        return self._sender

    @sender.setter
    def sender(self, user):
        """
        Sets/updates the author

        :param User user: User to set for the message
        """
        if not isinstance(user, User):
            raise TypeError('Sender needs to be User instance')

        self._sender = user
        self.sender_id = user.id

    @property
    def recipients(self):
        """
        Property for getting message recipients

        :returns: User instance of the project author
        """
        mg = MessageGroup.get(self.group_id)
        return mg.recipients

    @classmethod
    def get_messages(cls, limit=100, include_flags=None, exclude_flags=None, **filters):
        """
        Returns all messages matching with query.

        Example usage::

            Message.get_messages(group_id=1, limit=20)
            Message.get_messages(user_id=123)
            Message.get_messages(limit=12, exclude_flags={123: Message.FLAG_DELETED})

        Possible values for filters are listed in: Message.FIELDS (keys)
        """
        messages = []

        # Validate input
        limit = safe_int(limit)
        exclude_flags = exclude_flags or {}
        for key, val in exclude_flags.items():
            exclude_flags.update({safe_int(key): safe_int(val)})
        include_flags = include_flags or {}
        for key, val in include_flags.items():
            include_flags.update({safe_int(key): safe_int(val)})

        sql = '''
        SELECT m.*
        FROM message AS m
        LEFT JOIN message_flag AS mf ON mf.message_id = m.id
        {where}
        GROUP BY mf.message_id
        ORDER BY m.created DESC
        LIMIT {limit}
        '''
        # Update SQL query if filters given
        if filters:
            where = 'WHERE ' + ' AND '.join(['m.{0}=%s'.format(cls.FIELDS[fieldname]) for fieldname in filters.keys() if fieldname in cls.FIELDS])

            # Include messages
            if include_flags:
                where += ''' AND ({0}) '''.format(' OR '.join(['(mf.user_id = {0} AND mf.flag = {1})'.format(user_id, flag) for user_id, flag in include_flags.items()]))

            # Exclude messages by user specific flags
            if exclude_flags:
                where += ''' AND m.id NOT IN (
                    SELECT message_id
                    FROM message_flag
                    WHERE {0}
                )'''.format(' OR '.join(['(user_id = {0} AND flag = {1})'.format(user_id, flag) for user_id, flag in exclude_flags.items()]))

            sql = sql.format(where=where, limit=limit)

            with admin_query(cursors.DictCursor) as cursor:
                cursor.execute(sql, filters.values())
                messages = [cls.to_object(row) for row in cursor.fetchall()]

        # Plain query
        else:
            where = ''

            # Include messages
            if include_flags:
                where += ''' AND ({0}) '''.format(' OR '.join(['(mf.user_id = {0} AND mf.flag = {1})'.format(user_id, flag) for user_id, flag in include_flags.items()]))

            # Exclude messages by user specific flags
            if exclude_flags:
                where += ''' AND m.id NOT IN (
                    SELECT message_id
                    FROM message_flag
                    WHERE {0}
                )'''.format(' OR '.join(['(user_id = {0} AND flag = {1})'.format(user_id, flag) for user_id, flag in exclude_flags.items()]))

            sql = sql.format(where=where, limit=limit)

            with admin_query(cursors.DictCursor) as cursor:
                cursor.execute(sql)
                messages = [cls.to_object(row) for row in cursor.fetchall()]

        return messages

    @classmethod
    def get_messages_with_query(cls, user_id, query, limit=30):
        """
        Retrieve messages based on query that is matched with:

        :param int user_id: Id of the user whose messages are wanted to be retrieved
        :param str query:
            Query value matching with fields:

            - username
            - given name
            - last name
            - message content

        :param int limit: Maximum number of messages to fetch
        :returns: List of message objects matching with the query
        """
        messages = []

        # Query: match with username and message
        sql = '''
        SELECT *, CONCAT_WS(' ',
            m.content, m.env, sender.givenName, sender.lastName, sender.username, receiver.username
        ) COLLATE utf8_general_ci AS query
        FROM message AS m
        LEFT JOIN message_group_recipient AS mgr ON m.message_group_id = mgr.message_group_id
        LEFT JOIN user AS sender ON sender.user_id = mgr.user_id
        LEFT JOIN user AS receiver ON receiver.user_id = mgr.user_id
        WHERE mgr.user_id = %s
        HAVING query LIKE '%%{0}%%'
        ORDER BY m.created DESC
        LIMIT %s
        '''.format(safe_string(query))
        with admin_query(cursors.DictCursor) as cursor:
            cursor.execute(sql, (user_id, limit))
            messages = [cls.to_object(row) for row in cursor.fetchall()]

        return messages

    @classmethod
    def get(cls, id):
        """
        Returns single message, based on given id

        >>> Message.get(123)
        <Message>

        """
        message = None

        sql = '''
        SELECT *
        FROM message
        WHERE id = %s
        '''
        with admin_query(cursors.DictCursor) as cursor:
            cursor.execute(sql, id)
            row = cursor.fetchone()
            if row:
                message = cls.to_object(row)

        return message

    @classmethod
    def get_messages_grouped_by(cls, user_id, query=None, limit=30):
        """
        Returns latest messages from each sender, targeted or sent by given receiver
        """
        messages = []

        sql = '''
        SELECT m1.* FROM message AS m1
        LEFT JOIN message AS m2 ON (m1.message_group_id = m2.message_group_id AND m2.created > m1.created)
        WHERE m2.id IS NULL
        HAVING m1.message_group_id IN (SELECT message_group_id FROM message_group_recipient WHERE user_id = %s)
        ORDER BY CREATED DESC
        LIMIT %s
        '''
        with admin_query(cursors.DictCursor) as cursor:
            cursor.execute(sql, (user_id, limit))
            messages = [cls.to_object(row) for row in cursor.fetchall()]

        return messages

    @classmethod
    def to_object(cls, query):
        """
        Maps the SQL query into Message object
        """
        # Construct dict from parameter

        msg = Message()
        for pkey, field in cls.FIELDS.items():
            setattr(msg, pkey, query[field])

        return msg


class MessageGroup(object):
    """
    Simple DAO class for accessing message_group metadata, stored in ``message_group`` database table.

    >>> mg = MessageGroup()
    >>> mg.recipients = [123, 145, 512]
    >>> mg.save()
    >>> mg.id
    2
    >>> mg.recipients = [123, 512]
    >>> mg.save()
    >>> mg.id
    5
    >>>
    >>> # Retrieve
    >>> MessageGroup.get_groups(id=2)
    [<MessageGroup>, <MessageGroup>, ...]
    >>>
    >>> mg = MessageGroup()
    >>> mg.id = 96
    >>> mg.get_messages()
    [<Message>, <Message>, ...]

    """
    # Mapping: property=db_field
    FIELDS = {
        'id': 'id',
        'creator_id': 'creator_id',
        'title': 'title',
        'created': 'created'
    }

    def __init__(self):
        self.id = None
        self.title = None
        self.creator_id = None
        self.created = datetime.utcnow()
        self._recipients = None

    def __json__(self):
        """
        Returns dictionary presentation of the object, suitable for JSON.
        Example output::

            {
                'id': 123,
                'title': 'My group',
                'recipients: [142, 126, 132]
            }

        """
        return {
            'id': self.id,
            'title': self.title,
            'created': self.created,
            'recipients': self.recipients
        }

    @classmethod
    def to_object(cls, query):
        """
        Maps the SQL query into object
        """
        # Construct dict from parameter
        mgi = MessageGroup()
        for pkey, field in cls.FIELDS.items():
            setattr(mgi, pkey, query[field])

        return mgi

    @classmethod
    def get(cls, message_group_id):
        """
        Returns groups based on given filter
        """
        group_info = None

        sql = '''
        SELECT mg.*
        FROM message_group AS mg
        WHERE mg.id = %s
        '''
        with admin_query(cursors.DictCursor) as cursor:
            cursor.execute(sql, message_group_id)

            row = cursor.fetchone()
            if row:
                group_info = cls.to_object(row)

        return group_info

    @property
    def creator(self):
        """
        Returns the creator user if set
        :return: User
        """
        if not self.creator_id:
            raise Exception('MessageGroup has no creator')

        return get_userstore().getUserWhereId(self.creator_id)

    @property
    def recipients(self):
        """
        Property for getting list of recipients ids
        """
        if not self.id:
            raise ValueError('Save the message group before reading the recipients')

        if self._recipients is not None:
            return self._recipients

        self._recipients = []

        sql = '''
        SELECT user_id
        FROM message_group_recipient
        WHERE message_group_id = %s
        '''
        with admin_query(cursors.DictCursor) as cursor:
            cursor.execute(sql, self.id)
            self._recipients = [row['user_id'] for row in cursor.fetchall()]

        return self._recipients

    @recipients.setter
    def recipients(self, recipients):
        """
        Property for setting the recipients

        .. NOTE::

            Recipients are saved in the db at ``MessageGroup.save``

        """
        if not isinstance(recipients, list):
            raise TypeError('Receiver needs to be a list of receiver ids')

        # Ensure the sender is included in the recipients, there are no duplicates
        # It is fine to create groups without any other recipients
        self._recipients = list(set([safe_int(uid) for uid in recipients]))

    @property
    def info(self):
        """
        Returns group info in dictionary format.
        This is convenience function. Following are equivalent:

        >>> mg = MessageGroup.get(12)
        >>> mg.info['title']
        'foo'
        >>> mg.info = {'title': 'bar'}
        >>> mgi = MessageGroupInfo.get(mg.id)
        >>> mgi.title
        'bar'
        >>> mgi.title = 'baz'
        >>> mgi.save()


        :return: Group info
        :rtype: dict
        """
        data = {'id': self.id, 'created': None, 'title': None, 'creator': None}

        data.update({
            'creator_id': self.creator_id,
            'creator': self.creator,
            'created': self.created,
            'title': self.title
        })

        return data

    @info.setter
    def info(self, data):
        """
        Set/update info for the group
        :param data: Dictionary containing the data

        >>> mg = MessageGroup.get(23)
        >>> mg.info
        {'id': 23, 'title': None, 'creator':<User>}
        >>> mg.info = {'title': 'foo'}
        >>> mg.info
        {'id': 23, 'title': 'foo', 'creator':<User>}

        """
        mgi = MessageGroup.get(self.id)
        for key, val in data.items():
            setattr(mgi, key, val)

        mgi.save()

    @classmethod
    def get_groups(cls, limit=20, **filters):
        """
        Returns groups based on given filter
        """
        groups = []
        limit = safe_int(limit)

        sql = '''
        SELECT mgr.*
        FROM message_group_recipient AS mgr
        LEFT JOIN message AS m ON m.message_group_id = mgr.id
        {where}
        GROUP BY mgr.message_group_id
        ORDER BY m.created DESC
        LIMIT {limit}
        '''

        sql = '''
        SELECT mg.*, mgr.*
        FROM message_group AS mg
        LEFT JOIN message_group_recipient AS mgr ON mgr.message_group_id = mg.id
        {where}
        GROUP BY mg.id
        ORDER BY mg.created DESC
        LIMIT {limit}
        '''

        # Update SQL query if filters given
        if filters:
            where = 'WHERE ' + ' AND '.join(['mg.{0}=%s'.format(cls.FIELDS[fieldname]) for fieldname in filters.keys() if fieldname in cls.FIELDS])
            sql = sql.format(where=where, limit=limit)

            with admin_query(cursors.DictCursor) as cursor:
                cursor.execute(sql, filters.values())
                groups = [cls.to_object(row) for row in cursor.fetchall()]

        # Plain query
        else:
            sql = sql.format(where='', limit=limit)

            with admin_query(cursors.DictCursor) as cursor:
                cursor.execute(sql)
                groups = [cls.to_object(row) for row in cursor.fetchall()]

        return groups

    @classmethod
    def get_latest_message_groups(cls, user_id, limit=30):
        """
        Returns the message groups the user has some messages in it (that are not deleted)
        :param cls: MessageGroup class
        :param user_id: User id based on who the groups are listed
        :param limit: Maximum number of results
        :return: List of MessageGroups
        :rtype: list
        """
        mgroups = []

        sql = '''
        SELECT
            m.message_group_id,
            mf1.flag AS flag_del,
            mf2.flag AS flag_acl,
            (COUNT(mf2.flag) - COUNT(mf1.flag)) AS count_visible
        FROM message AS m
        LEFT JOIN
            message_flag AS mf1 ON
            mf1.flag = %s AND
            mf1.message_id = m.id AND
            mf1.user_id = %s
        LEFT JOIN
            message_flag AS mf2 ON
            mf2.flag = %s AND
            mf2.message_id = m.id AND
            mf2.user_id = %s
        GROUP BY m.message_group_id
        HAVING
            count_visible > 0
        LIMIT %s
        '''

        with admin_query(cursors.DictCursor) as cursor:
            cursor.execute(sql, (Message.FLAG_DELETED, user_id, Message.FLAG_ACCESS, user_id, limit))
            mgroups = [MessageGroup.get(row['message_group_id']) for row in cursor.fetchall()]

        return mgroups

    def save(self):
        """
        Save the object into database
        :return: Updated message group info
        :rtype: MessageGroupInfo
        """
        set_values = ', '.join(['{0}=%s'.format(field) for field in self.FIELDS.values()])
        values = [getattr(self, pro) for pro in self.FIELDS.keys()]

        # New entry
        if not self.id:
            sql = '''
            INSERT INTO message_group
            SET {set_values}
            '''.format(set_values=set_values)

            with admin_transaction() as cursor:
                cursor.execute(sql, values)
                self.id = cursor.lastrowid

        # Update entry
        else:
            # Create new entry or update existing
            sql = '''
            UPDATE message_group
            SET {set_values}
            WHERE id = %s
            '''.format(set_values=set_values)

            with admin_transaction() as cursor:
                cursor.execute(sql, values + [self.id])

        # Save the recipients info in db
        mgr = MessageGroupRecipient.get(self.id)
        mgr.recipients = self._recipients
        mgr.save()

        return self

    def get_messages(self):
        """
        Returns the messages from current message group
        """
        return Message.get_messages(limit=5000, group_id=self.id)

    def get_recipient_users(self):
        """
        Convenience function for getting the recipients users

        :returns: List of users
        """
        users = []
        userstore = get_userstore()
        for rid in self.recipients:
            users.append(userstore.getUserWhereId(rid))

        return users


class MessageGroupRecipient(object):
    """
    Simple DAO class for accessing message_group_recipient data.
    """
    # Mapping: property:dbfield
    FIELDS = {
        'id': 'message_group_id',
        'user_id': 'user_id',
    }

    def __init__(self):
        self.id = None
        self.recipients = []

    @classmethod
    def get(cls, id):
        """
        Fetches message group recipient information from the database

        :param cls:
        :param id: Id of the message group
        :return: MessageGroup
        """
        group_info = None
        recipients = []

        sql = '''
        SELECT mgr.user_id
        FROM message_group_recipient AS mgr
        WHERE mgr.message_group_id = %s
        '''
        with admin_query(cursors.DictCursor) as cursor:
            cursor.execute(sql, id)

            for row in cursor.fetchall():
                recipients.append(row['user_id'])

        mgr = MessageGroupRecipient()
        mgr.id = id
        mgr.recipients = recipients

        return mgr

    @classmethod
    def to_object(cls, query):
        """
        Maps the SQL query into Message object
        """
        # Construct dict from parameter
        msg = MessageGroupRecipient()
        for pkey, field in cls.FIELDS.items():
            setattr(msg, pkey, query[field])

        return msg

    def save(self):
        """
        Saves the changes in properties into database

        >>> mg = MessageGroup()
        >>> mg.save()
        >>> mgr = MessageGroupRecipient()
        >>> mgr.recipients = [123, 423, 123]
        >>> mgr.id = mg.id
        >>> mgr.save()

        """
        # If either of the properties is None
        if None in (self.recipients, self.id):
            raise ValueError('Both recipients and id needs to be set first')

        recipients_str = [str(receiver_id) for receiver_id in self.recipients]

        # Update existing group: remove existing members and insert new
        remove_sql = 'DELETE FROM message_group_recipient WHERE message_group_id = %s'
        update_sql = 'INSERT INTO message_group_recipient (message_group_id, user_id) VALUES (%s, %s)'
        update_values = zip([self.id]*len(self.recipients), self.recipients)

        with admin_transaction() as cursor:
            cursor.execute(remove_sql, self.id)
            cursor.executemany(update_sql, update_values)

        logging.info('Updated message group {0} into database'.format(self))

        return self