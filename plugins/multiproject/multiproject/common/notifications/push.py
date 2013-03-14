# -*- coding: utf-8 -*-
"""
Module contains provides a generic solution for sending PUSH notifications.
Solution is built on top the `Juggernaut service <https://github.com/maccman/juggernaut>`_.

- :py:class:`NotificationSystem`: Python API for sending notification
- :py:class:`ChangeNotifier`: Listens Trac changes and notifies the user(s) about them
- :py:class:`NotificationRestAPI`: REST API for getting and reseting notifications

Examples of the usage:

Sending (python):
    NotificationSystem provides the lower level api for sending message::

        ns = self.env[NotificationSystem]
        ns.send_notification(channels=['ch1', 'ch2'], "foobar")

Subscribing (javascript):
    Javascript library in multiproject.js provides ways to subscribe to incoming notifications::

        ns = new multiproject.api.NotificationSystem();
        ns.subscribe(['ch1', 'ch2'], function(notification){
            // Notification is in JSON format
            window.alert("Received notification: " + notification)
        });

Retrieving (python):
    The list of notifications (missed or not) can be retrieved with script::

        ns = self.env[NotificationSystem]
        for notification in ns.get_notifications('ch1', reset=True):
            # Notification is in dict format: {id:123, type:'ticket', action:'create'}
            print notification

REST API:
    Notifications can be retrieved using REST API:

    - ``<projectenv>/api/notification/list?user_id=<uid>``
    - ``<projectenv>/api/notification/list?project_id=<pid>``
    - ``<projectenv>/api/notification/missed?type=message``

    Example output of notifications::

        [
            {"action": "create", "type": "message", "id": "71"},
            {"action": "create", "type": "message", "id": "70"},
            {"action": "create", "type": "ticket", "id": "542"}
        ]


"""
try:
    import cPickle as pickle
except ImportError:
    import pickle

from datetime import datetime
import json
import pkg_resources

from trac.core import Component, implements, TracError
from trac.config import Option, IntOption, BoolOption, ListOption
from trac.ticket.api import ITicketChangeListener
from trac.web.api import IRequestFilter, IRequestHandler
from trac.web.chrome import add_script, ITemplateProvider, INavigationContributor, _, tag

try:
    from redis import Redis, ConnectionError
except ImportError:
    Redis = ConnectionError = None

from multiproject.core.restful import json_encoder, send_json
from multiproject.core.users import User, get_userstore
from multiproject.common.projects.listeners import IProjectChangeListener
from multiproject.common.messages.api import IMessageListener, IMessageGroupListener, Message
from multiproject.common.projects import Project
from multiproject.common.web.resource import IJSONDataPublisherInterface


class NotificationSystem(Component):
    """
    API for sending and getting notifications.

    Notifications are stored in Redis database as follows::

        # Structure
        uid-<id> : [{<type>-<id>:<notification>}, {<type>-<id>:<notification>}, ...]

        # Example
        uid-2903 : [{message-123: {id:123, content:123, created:...}}, {message-2: {...}}]

    Where notifications are serialized JSON data - they are automatically de-serialized on load.

    """
    hkey = '%(type)s-%(id)s'

    def send_notification(self, channels, data, store=True):
        """
        Sends notification to selected channels and stores them with additional key, where they
        can be retrieved afterwards if user missed the notification::

            ns = self.env[NotificationSystem]
            ns.send_notification(['mychannel'], {'foo': 'bar'})
            ns.get_notifications('mychannel')

        :param list channels: List of channels where to send
        :param data:
            Data to send to channel. The actual message is wrapped in JSON format::

                {channels:['ch1', 'ch2'], data:'data'}

        :param bool store:
            Store notification also with separate key, where they can be retrieved in a case user misses
            the notification.

        """
        # Store notification with permanent key:
        # - set: List of notification keys stored with key: <channelname>
        # - hash: Notification data stored with key: <type>-<id>
        redis = self._get_redis()

        if store:
            for ch in channels:
                hkey = self.hkey % data
                # Pickle data because of nested dict
                redis.hmset(ch, {hkey: pickle.dumps(data)})

        # Publish message in specified channels
        msg = {
          "channels": channels,
          "data": data
        }
        return redis.publish("juggernaut", json.dumps(msg, default=json_encoder))

    def get_notifications(self, chname, keys=None, reset=False):
        """
        Returns list of notifications stored in Redis DB

        :param str chname: Channel name where to retrieve notifications
        :param bool reset: Reset notifications after returning
        :param dict keys: Optional list of fields to fetch
        :returns:

        >>> ns = self.env[NotificationSystem]
        >>> ns.get_notifications('uid-123')
        [{message-123:{notification}, message-4:{notification}}]
        >>> ns.get_notifications('uid-123', fields=['message-4'])
        [{message-4:{notification}}]

        """
        notifications = []
        redis = self._get_redis()

        # Iterate through keys and retrieve the hashes with them
        if keys:
            notifications = [pickle.loads(notification) for notification in list(redis.hmget(chname, keys)) if notification]
            if reset:
                redis.hdel(chname, *keys)

        else:
            notifications = [pickle.loads(notification) for key, notification in redis.hgetall(chname).items()]
            if reset:
                redis.delete(chname)

        return notifications

    def reset_notifications(self, chname=None, keys=None):
        """
        Removes notifications from permanent store

        :param str chname: Name of the channel. If none, all the channels are iterated
        :param list keys: Optional list of keys only to reset. Defaults to all notifications within a channel
        """
        redis = self._get_redis()
        chnames = [chname] or redis.keys()

        # All notifications matching with the keys: ['<type>-<id>', '<type>-<id>', ...]
        for chname in chnames:
            if keys:
                redis.hdel(chname, *keys)

            # All notifications based on channel
            else:
                redis.delete(chname)

    def reset_notification(self, chname, notification):
        """
        Removes the notification from Redis DB, defined by notification data

        :param str chname: Name of the channel
        :param dict notification: Notification ``{'id': 123, 'type': 'message'}``
        """
        # Check notification validity
        if not(isinstance(notification, dict) and 'id' in notification and 'type' in notification):
            raise Exception('Invalid notification')

        # Remove notification
        redis = self._get_redis()
        hkey = self.hkey % notification

        return redis.hdel(chname, hkey)

    def generate_channel_name(self, obj=None, user_id=None, project_id=None):
        """
        Generates the channel names based on given parameters::

            >>> ns = self.env[NotificationSystem]
            >>> ns.generate_channel_name(user_id=123)
            'uid-123'
            >>> ns.generate_channel_name(project_id=323)
            'pid-323'

        In javascript library, there is a similar method::

            var ns = new multiproject.api.NotificationSystem();
            // Returns uid-123
            ns.generateChannelName({recipient_id: 123});

        """
        if isinstance(obj, User):
            return 'uid-{0}'.format(obj.id)

        if isinstance(obj, Project):
            return 'pid-{0}'.format(obj.id)

        if user_id:
            return 'uid-{0}'.format(user_id)

        if project_id:
            return 'pid-{0}'.format(user_id)

        return 'global'

    def _get_redis(self):
        # NOTE: Redis client automatically acquires and release connection from pool
        redis_host = self.config.get('multiproject-messages', 'redis_host')
        redis_port = self.config.getint('multiproject-messages', 'redis_port')

        try:
            redis = Redis(host=redis_host, port=redis_port)
            redis.ping()

            return redis
        except ConnectionError, e:
            raise TracError('Failed connect connect notification service: %s' % e)


class ChangeNotifier(Component):
    """
    Sends push notifications from the listened changes using Juggernaut service
    """
    implements(
        IMessageListener,
        IMessageGroupListener,
        ITemplateProvider,
        IRequestFilter,
        IProjectChangeListener,
        ITicketChangeListener,
        INavigationContributor
    )

    # IMessageListener methods

    def message_created(self, message):
        initiator = message.sender.username

        for recipient_id in message.recipients:
            self.notify_user(
                {'type': 'message', 'id': message.id, 'action': 'create', 'initiator': initiator},
                recipient_id,
                store=recipient_id != message.sender.id
            )

    def message_flagged(self, message, user, flag):
        """
        Message was flagged
        """
        # Reset the notification flag if the message is hidden
        if flag == Message.FLAG_DELETED:
            ns = self.env[NotificationSystem]
            ns.reset_notification(ns.generate_channel_name(user_id=user.id), {'type': 'message', 'id': message.id})

    def message_deleted(self, message):
        """
        Message was removed from the database
        """
        # Reset all notifications related to the ticket

        # NOTE: Unfortunately we need to iterate all users and check
        ns = self.env[NotificationSystem]
        ns.reset_notifications(chname=None, keys=['message-%d' % message.id])

    # IMessageGroupListener methods
    def group_created(self, group):
        pass

    def group_changed(self, group, old_values):
        initiator = ''
        initiator_id = 0
        creator = group.creator

        if creator:
            initiator = creator.username
            initiator_id = creator.id

        # Form union from the sets
        all_recipients = set(old_values.get('recipients', [])) | set(group.recipients)

        # Notify both old and new group recipients
        # Old users won't get any messages but they can handle the notifications otherwise
        for recipient_id in all_recipients:
            self.notify_user(
                {'type': 'messagegroup', 'id': group.id, 'action': 'change', 'initiator': initiator},
                recipient_id,
                store = recipient_id != initiator_id
            )

    # ITemplateProvider methods

    def get_templates_dirs(self):
        return [pkg_resources.resource_filename('multiproject.common.notifications', 'templates')]

    def get_htdocs_dirs(self):
        return [('multiproject', pkg_resources.resource_filename(__name__, 'htdocs'))]

    # INavigationContributor methods

    def get_active_navigation_item(self, req):
        return 'notifications'

    def get_navigation_items(self, req):
        if req.authname and req.authname != 'anonymous':
            yield ('metanav', 'notifications', tag.a(_('Notifications'), **{'class': 'notifications', 'href': '#'}))

    # IRequestFilter methods

    def pre_process_request(self, req, handler):
        """
        Process request to add some data in request
        """
        return handler

    def post_process_request(self, req, template, data, content_type):
        """
        Add global javascript data on post-processing phase
        """
        # When processing template, add global javascript json into scripts
        if template:
            add_script(req, 'multiproject/js/jquery-ui.js')
            add_script(req, 'multiproject/js/jquery.cookie.js')
            add_script(req, 'multiproject/js/transparency.js')
            add_script(req, 'multiproject/js/multiproject.js')
            add_script(req, 'multiproject/js/jquery.json.js')
            add_script(req, 'multiproject/js/jstorage.js')
            add_script(req, 'multiproject/js/push.js')

        return template, data, content_type

    # IProjectChangeListener methods

    def project_created(self, project):
        pass

    def project_set_public(self, project):
        pass

    def project_set_private(self, project):
        pass

    def project_archived(self, project):
        pass

    def project_deleted(self, project):
        pass

    def project_watched(self, project):
        pass

    # ITicketChangeListener methods

    def ticket_created(self, ticket):
        # NOTE: Reporter is not available as property
        initiator = ticket['reporter']
        self.notify_project({'type': 'ticket', 'id': ticket.id, 'action':'create', 'initiator': initiator})

    def ticket_changed(self, ticket, comment, author, old_values):
        if comment:
            self.notify_project({'type': 'ticket', 'id': ticket.id, 'action':'comment', 'inititor': author})
        else:
            self.notify_project({'type': 'ticket', 'id': ticket.id, 'action':'change', 'initiator': author})

    def ticket_deleted(self, ticket):
        # TODO: ticket.author or reporter?
        self.notify_project({'type': 'ticket', 'id': ticket.id, 'action':'delete', 'initiator': ticket['author']})

    # Public methods

    def notify_user(self, data, user_id, store=True):
        # Add timestamp if not already set
        if 'created' not in data:
            data.update({'created': datetime.utcnow().isoformat()})

        # Load notification system and used it for sending - unless disabled
        ns = self.env[NotificationSystem]
        if not ns:
            return

        try:
            count = ns.send_notification([ns.generate_channel_name(user_id=user_id)], data, store)
            self.log.info('Sent private notification to user (%s) about: %s and %s received it' % (user_id, data, count))
        except TracError, err:
            self.log.warning('Failed to send notification to user (%s): %s' % (user_id, err))

    def notify_project(self, data, project_id=None, store=True):
        # Add timestamp if not already set
        if 'created' not in data:
            data.update({'created': datetime.utcnow().isoformat()})

        if not project_id:
            project_id = Project.get(self.env).id

        # Load notification system and used it for sending - unless disabled
        ns = self.env[NotificationSystem]
        if not ns:
            return

        try:
            count = ns.send_notification([ns.generate_channel_name(project_id=project_id)], data, store)
            self.log.info('Sent project wide notification to project (%s) about: %s and %s received it' % (project_id, data, count))
        except TracError, err:
            self.log.warning('Failed to send notification to project (%s): %s' % (project_id, err))


class NotificationRestAPI(Component):
    """
    Component implements simple REST API for messages
    """
    implements(IJSONDataPublisherInterface, IRequestHandler)

    juggernaut_host = Option('multiproject-messages', 'juggernaut_host', None, 'Juggernaut server host name or ip (or proxy on front them). Defaults to current domain')
    juggernaut_port = IntOption('multiproject-messages', 'juggernaut_port', None, 'Juggernaut server port. Defaults to current port')
    juggernaut_secure = BoolOption('multiproject-messages', 'juggernaut_secure', False, 'Secure connection or not')
    juggernaut_transports = ListOption('multiproject-messages', 'juggernaut_transports', [],
        'Set/limit the used tranportation methods. Defaults to automatic selection. '
        'Valid values: websocket, flashsocket, htmlfile, xhr-polling, jsonp-polling')
    redis_host = Option('multiproject-messages', 'redis_host', 'localhost', 'Redis server host name or ip')
    redis_port = IntOption('multiproject-messages', 'redis_port', 6379, 'Redis server port')

    handlers = {
        'list':'_list_notifications',
    }

    # IJSONDataPublisherInterface

    def publish_json_data(self, req):
        return {'conf': {
            'juggernaut_host': self.juggernaut_host,
            'juggernaut_port': self.juggernaut_port,
            'juggernaut_secure': self.juggernaut_secure,
            # FIXME: Using self.juggernaut_transports directly returns all items in a string
            'juggernaut_transports': self.config.getlist('multiproject-messages', 'juggernaut_transports', []),
            'redis_port': self.redis_port,
            'redis_host': self.redis_host,
        }}

    # IRequestHandler

    def match_request(self, req):
        return req.path_info.startswith('/api/notification')

    def process_request(self, req):

        # Select handler based on last part of the request path
        action = req.path_info.rsplit('/', 1)[1]
        if action in self.handlers.keys():
            return getattr(self, self.handlers[action])(req)

        # Single notification
        if 'id' in req.args:
            return self._get_notification(req)

        return send_json(req, {'result': 'Missing action'}, status=404)

    def _list_notifications(self, req):
        """
        Returns the list of missed notification and optionally reset them
        """
        chname = None
        initiator = req.args.get('initiator', '')
        reset = req.args.get('reset', 'false').lower() in ('yes', 'true', 'on', '1')
        ntype = req.args.get('type', '')

        # Check permissions
        if req.authname == 'anonymous':
            return send_json(req, {'result': 'Permission denied'}, status=403)

        userstore = get_userstore()
        user = userstore.getUser(req.authname)
        ns = self.env[NotificationSystem]
        if not ns:
            return send_json(req, [])

        # Fetch notifications sent to user
        chname = ns.generate_channel_name(user_id=user.id)

        # Get notifications
        try:
            notifications = ns.get_notifications(chname)
        except TracError, e:
            self.log.error('Failed to retrieve notifications')
            return send_json(req, {'result': e.message}, status=500)

        # Internal filtering and notification reset function
        def filter_and_reset(notification):
            if initiator and notification.get('initiator', '') != initiator:
                return False

            if ntype and notification.get('type', '') != ntype:
                return False

            if reset:
                ns.reset_notification(chname, notification)

            return True

        # Filter by sender if set
        notifications = filter(filter_and_reset, notifications)

        # If user want's to reset status, send empty notification so the listening clients can update their state
        if reset:
            ns.send_notification([chname], {'type': ntype}, store=False)

        return send_json(req, notifications)

    def _get_notification(self, req):
        """
        Get and especially reset the specified notification
        """
        reset = req.args.get('reset', 'false').lower() in ('yes', 'true', 'on', '1')
        ntype = req.args.get('type')
        nid = req.args.get('id')

        if not all((ntype, nid)):
            return send_json(req, {'result': 'Either or both type and id missing'}, status=400)

        userstore = get_userstore()
        user = userstore.getUser(req.authname)
        ns = self.env[NotificationSystem]
        chname = ns.generate_channel_name(user_id=user.id)

        notification = {'id': nid, 'type': ntype}
        if reset:
            ns.reset_notification(chname, notification)

        return send_json(req, notification)
