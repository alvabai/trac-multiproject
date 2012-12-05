# -*- coding: utf-8 -*-
"""
Provides REST API handlers for sending and receiving messages:

REST API (MessageRestAPI):
    - Send message: ``<projectenv>/api/message/post?content=message&group_id=3``
    - Send message: ``<projectenv>/api/message/post?content=message&recipients=543,123,432``
    - Delete/hide one message: ``<projectenv>/api/message/delete?message_id=432``
    - Delete/hide all messages in group: ``<projectenv>/api/message/delete?group_id=3``
    - Retrieve all own messages: ``<projectenv>/api/message/list``
    - Retrieve all messages sent to group: ``<projectenv>/api/message/list?group_id=3``
    - Retrieve one message: ``<projectenv>/api/message?message_id=123``
    - Retrieve message groups: ``<projectenv>/api/groups``
    - Retrieve message group: ``<projectenv>/api/group?recipients=543,123,432``
    - Retrieve message group: ``<projectenv>/api/group?group_id=2``
    - Mark message read: ``<projectenv>/api/message/markread?message_id=223``
    - Mark all message read within group: ``<projectenv>/api/message/markread?group_id=2``

Related permissions:
    - MESSAGE_VIEW: For getting messages (checked from environment)
    - MESSAGE_CREATE: For posting messages (checked from environment)

Python API (MessageService):
    Send message using MessageService (access component via environments component manager)::

        msgsrv = self.env[MessageService]
        msgsrv.post('message', sender_id=123, recipient_id=432)

"""
from copy import copy
import os

from trac.core import Component, implements, Interface, ExtensionPoint, TracError
from trac.env import open_environment
from trac.mimeview.api import Context
from trac.perm import PermissionCache
from trac.web.api import IRequestHandler
from trac.web.href import Href
from trac.wiki.formatter import format_to_html

from multiproject.core.restful import send_json
from multiproject.core.users import get_userstore
from multiproject.common.messages.db import Message, MessageGroup
from multiproject.common.projects import HomeProject


class IMessageListener(Interface):
    """
    Interface for interested parties for making actions on message sending and receiving.

    Example usage::

        class MyMessageListener(Component):
            implements(IMessageListener)

            def message_created(self, message):
                self.log.info('Message was created: %s' % message)

    """
    def message_created(message):
        # Message was created: message object provided as a parameter
        pass

    def message_flagged(message, user, flag):
        # User flagged a messages with the specified flag
        pass

    def message_deleted(message):
        # Message is deleted from database
        pass

class IMessageGroupListener(Interface):
    """
    Interface for interested parties for making actions on message group changes

    Example usage::

        class MyMessageGroupListener(Component):
            implements(IMessageGroupListener)

            def group_created(self, group):
                self.log.info('Message group was created: %s' % group)

    """
    def group_created(group):
        # Group was created: message group object provided as a parameter
        pass

    def group_changed(group, old_values):
        """
        Group was changed. For example, recipients were added or removed

        :param MessageGroup group: Updated message group
        :param dict old_values: List of old values in dictionary, field name as a key
        """
        pass


class MessageService(Component):
    """
    Message sending service, to provide a python API
    Use compontent via ComponentMgr available in Environment::

        msgsrv = self.env[MessageService]
        msgsrv.get_messages()

    Component also uses the IMessageListener, notifying the interest parties
    about posted messages.
    """
    implements(IMessageListener)
    message_listeners = ExtensionPoint(IMessageListener)
    message_group_listeners = ExtensionPoint(IMessageGroupListener)

    def post(self, content, sender, group):
        """
        Posts a new message to specified channels

        :param str content: Message body
        :param User sender: User object
        :param MessageGroup group: MessageGroup object. Message is posted on message group object receivers

        """

        # Store in database
        msg = Message()
        msg.sender_id = sender.id
        msg.group_id = group.id
        msg.content = content
        msg.env = self.env.project_identifier
        msg.save()

        # Notify listeners about created messages
        for mlistener in self.message_listeners:
            mlistener.message_created(msg)

    def get_messages(self, user_id, group_id, limit=20):
        """
        Get multiple message based on given parameters
        """
        messages = Message.get_messages(
            limit=limit,
            include_flags={user_id: Message.FLAG_ACCESS},
            exclude_flags={user_id: Message.FLAG_DELETED},
            group_id=group_id
        )

        # Append notification data to messages if enabled
        if self.env.is_component_enabled('multiproject.common.notifications.push.NotificationSystem'):
            from multiproject.common.notifications.push import NotificationSystem

            ns = self.env[NotificationSystem]
            try:
                chname = ns.generate_channel_name(user_id=user_id)
                for message in messages:
                    message.notifications = ns.get_notifications(chname, ['message-%s' % message.id])
            except Exception, e:
                self.log.error('Failed to retrieve notifications')

        return messages

    def get_messages_with_query(self, user_id, query, limit=30):
        """
        Retrieve messages based on query
        """
        return Message.get_messages_with_query(user_id, query, limit)

    def get_messages_grouped_by(self, user_id, query=None, limit=30):
        """
        Returns list of latest messages, grouped by the the sender.

        :returns: List of messages, one from each sender
        :rtype: list
        """
        return Message.get_messages_grouped_by(user_id, limit=limit)

    def get_message_groups(self, user_id=None, limit=30):
        """
        Returns message groups
        """
        if user_id is not None:
            return MessageGroup.get_groups(user_id=user_id, limit=limit)
        return MessageGroup.get_groups(limit=limit)

    def get_latest_message_groups(self, user_id, limit=30):
        return MessageGroup.get_latest_message_groups(user_id, limit=limit)

    def get_message(self, user_id, message_id):
        """
        Get single message. Used for example with notifications (where notification contains only id and type)
        and actual message needs to be retrieved
        """
        message = Message.get(message_id)

        # Append notification data to messages if enabled
        # Reset message notification if enabled

        if self.env.is_component_enabled('multiproject.common.notifications.push.NotificationSystem'):
            from multiproject.common.notifications.push import NotificationSystem

            ns = self.env[NotificationSystem]
            try:
                chname = ns.generate_channel_name(user_id=user_id)
                ns.reset_notification(chname, {'type': 'message', 'id': message.id})

            except Exception, e:
                self.log.error('Failed to retrieve notifications')

        return message

    def delete_message(self, message_id, user_id=None, only_hide=True):
        """
        Delete hide
        """
        return self.delete_messages([message_id], user_id, only_hide)

    def delete_messages(self, message_ids, user_id=None, only_hide=True):
        """
        Delete one or multiple messages

        :param message_ids: List of message ids
        :param user_id: Id of the user. Only needed if only_hide = False (for flagging
        :param only_hide: Boolean flag to indicate if message is only to be hidden from user
        """
        user = None

        # User info only needed if flaggin required
        if only_hide:
            userstore = get_userstore()
            user = userstore.getUserWhereId(user_id)
            if not user:
                raise Exception('User cannot be found')

        # Iterate all messages
        for message_id in message_ids:
            message = Message.get(message_id)

            # NOTE: Hiding instead of deleting
            if only_hide:
                flag = Message.FLAG_DELETED
                message.set_flag(user.id, flag=flag)

                # Notify listeners about flagged messages
                for mlistener in self.message_listeners:
                    mlistener.message_flagged(message, user, flag)

            # Delete from database completely
            else:
                message.delete()
                self.log.info('Deleted message %d from database' % message.id)

                # Notify listeners about deleted messages
                for mlistener in self.message_listeners:
                    mlistener.message_deleted(message)

    def create_message_group(self, user_id, title=None, recipients=None):
        """
        Create message group
        """
        mg = MessageGroup()
        mg.creator_id = user_id
        mg.title = title or None
        mg.recipients = recipients or []
        mg.save()

        # Notify listeners
        for mlistener in self.message_group_listeners:
            mlistener.group_created(mg)

        return mg

    def get_message_group(self, group_id):
        """
        Returns the message group specified by the group id

        :returns: Message group if found
        """
        return MessageGroup.get(group_id)

    def update_message_group(self, group_id, user_id, new_values):
        """
        Update message group with given data

        :param long group_id: Id of the message group to update
        :param dict new_values: Dictionary of the new values
        :returns: MessageGroup
        """
        msgsrv = MessageService(self.env)
        userstore = get_userstore()
        user = userstore.getUserWhereId(user_id)
        user_display = user.getDisplayName().strip()
        mg = MessageGroup.get(group_id)

        # Read existing values
        old_values = {
            'recipients': copy(mg.recipients),
            'creator_id': mg.creator.id,
            'title': mg.title
        }

        # Update new values to DB
        mg.recipients = new_values.get('recipients', old_values['recipients'])
        mg.title = new_values.get('title', old_values['title'])
        mg.save()

        # Get display name
        def format_user(user_or_id):
            if type(user_or_id) in (long, int):
                user_or_id = userstore.getUserWhereId(user_or_id)
            return user_or_id.getDisplayName().strip()

        # NOTE; Temporarily set different recipient set on message group object (but not save)

        # Post removed recipients as messages
        recipients_removed = [removed_uid for removed_uid in set(old_values['recipients']).difference(mg.recipients)]
        if recipients_removed:
            recipients_org = copy(mg.recipients)
            mg.recipients = recipients_removed
            msgsrv.post('%s removed %s from topic' % (user_display, ','.join([format_user(rid) for rid in recipients_removed])), user, mg)
            mg.recipients = recipients_org

        # Post new recipients as messages
        recipients_added = [added_uid for added_uid in set(mg.recipients).difference(old_values['recipients'])]
        if recipients_added:
            recipients_org = copy(mg.recipients)
            mg.recipients = recipients_added
            msgsrv.post('%s added %s to topic' % (user_display, ','.join([format_user(aid) for aid in recipients_added])), user, mg)
            mg.recipients = recipients_org

        # Post change as message
        if old_values['title'] != mg.title:
            msgsrv.post('%s renamed topic from "%s" to "%s"' % (
                user_display,
                old_values.get('title') or 'Topic %d' % mg.id,
                mg.title or 'Topic %d' % mg.id),
                user, mg)

        # Notify listeners (after the data is stored in DB!)
        for mlistener in self.message_group_listeners:
            mlistener.group_changed(mg, old_values)

        return mg

    # IMessageListener methods

    def message_created(self, message):
        """
        Extension listener. Invoked when message is created: run post actions

        :param message: Message
        """
        # Set visibility flag for each recipient
        userstore = get_userstore()
        recipients = message.recipients
        flag = Message.FLAG_ACCESS
        message.set_flags(recipients, [flag]*len(recipients))

        # Notify listeners about created messages
        for mlistener in self.message_listeners:
            for recipient_id in recipients:
                user = userstore.getUserWhereId(recipient_id)
                mlistener.message_flagged(message, user, flag)

    def message_flagged(self, message, user, flag):
        """
        Extension listener: message was set with the flag
        """
        pass

    def message_deleted(self, message):
        """
        Extension listener: message was set with the flag
        """
        pass


class MessageRestAPI(Component):
    """
    Component implements simple REST API for messages
    """
    implements(IRequestHandler)

    # REST API URL mapping: /api/message/<path> = <method>
    handlers = {
        'post': '_post_message',
        'list': '_list_messages',
        'delete': '_delete_message',
        'groups': '_list_message_groups',
        'group': '_get_message_group',
        'markread': '_mark_read'
    }

    # IRequestHandler methods

    def match_request(self, req):
        return req.path_info.startswith('/api/message')

    def process_request(self, req):

        if req.authname == 'anonymous':
            raise TracError('Authentication required')

        # Select handler based on last part of the request path
        action = req.path_info.rsplit('/', 1)[1]
        if action in self.handlers.keys():
            return getattr(self, self.handlers[action])(req)

        # Single message
        if 'message_id' in req.args:
            return self._get_message(req)

        return send_json(req, {'result': 'Missing action'}, status=404)

    # Internal methods

    def _list_messages(self, req):
        """
        Returns multiple message in JSON format, based on given request arguments.

        :param Request req:
            Trac request, with following arguments:

            - limit: Maximum number of responses
            - query: String matching with the fields:

              - username
              - given name
              - last name
              - message content

            - format: Render to HTML or return as raw text. Possible values: html / raw

        :returns: Message in JSON format

        """
        userstore = get_userstore()
        user = userstore.getUser(req.authname)
        msgsrv = MessageService(self.env)
        this_env = self.env.project_identifier
        messages = []

        group_id = req.args.get('group_id')
        query = req.args.get('q', '')
        limit = req.args.get('limit', 5)

        # Convert types
        try:
            limit = int(limit)
        except ValueError:
            return send_json(req, {'result': 'Invalid request'}, status=403)

        if query:
            # Get messages from all groups
            messages = msgsrv.get_messages_with_query(user.id, query, limit)
        elif group_id:
            # Get messages from specified
            messages = msgsrv.get_messages(user.id, group_id, limit)
        else:
            return send_json(req, {'result': 'Invalid request'}, status=403)

        # Render to HTML unless opted out
        if req.args.get('format', 'html') != 'raw':
            context = Context.from_request(req)

            # Iterate message to render them
            for msg in messages:
                env = self.env
                msg_env = msg.env

                # If message is sent from different env, load it for correct links
                if msg_env and msg_env != this_env:
                    env = open_environment(os.path.join(
                        self.config.get('multiproject', 'sys_projects_root'),
                        msg_env),
                        use_cache=True
                    )

                # Override the URL because the env does not have abs_href set
                context.href = Href('/%s' % env.path.rsplit('/', 1)[1])
                msg.content = format_to_html(env, context, msg.content)

        return send_json(req, messages)

    def _delete_message(self, req):
        """
        Deletes one or multiple messages from the user by hiding them
        (others can still see them)

        Following Request parameters are expected:

        - message_id: Id of the message to delete
        - group_id: Id of the message group

        .. note::

            Either ``message_id`` or ``group_id`` is required

        """
        userstore = get_userstore()
        msgsrv = MessageService(self.env)

        user = userstore.getUser(req.authname)
        message_id = req.args.get('message_id')
        group_id = req.args.get('group_id')
        only_hide = True

        try:
            # Delete one message
            if message_id:
                message = Message.get(message_id)

                # Everyone can hide message, even the non-recipient
                msgsrv.delete_message(message.id, user.id, only_hide)

            # Delete all group messages
            elif group_id:
                # Everyone can hide message, even the non-recipient
                mg = MessageGroup.get(group_id)
                # NOTE: Should delete_messages take objects intead of ids?
                msgsrv.delete_messages([msg.id for msg in mg.get_messages()], user.id, only_hide)

        except Exception, e:
            self.log.warning('Deleting the message failed with id: {0}'.format(message_id))
            return send_json(req, {'result': 'Failed to delete the message: {0}'.format(e)}, status=404)

        return send_json(req, {'result': 'OK'})

    def _get_message(self, req):
        """
        Returns contents of the message, if user has permission to see it:

        - If user is marked as sender or receiver
        - If message is project wide, and user has MESSAGE_VIEW permission in the project

        :param Request req:
            Trac request, with following arguments:

            - message_id: Id of the message to load. Required.
            - format: Render to HTML or return as raw text. Possible values: html / raw

        :returns: Message in JSON format

        """
        # Check permission from home env
        home_env = HomeProject().get_env()
        home_perm = PermissionCache(home_env, req.authname)

        # Get current user
        userstore = get_userstore()
        user = userstore.getUser(req.authname)
        this_env = self.env.project_identifier

        # Convert types
        message_id = req.args.get('message_id')
        try:
            message_id = int(message_id)
        except ValueError:
            return send_json(req, {'result': 'Invalid request'}, status=403)

        # Get message
        msgsrv = self.env[MessageService]
        message = msgsrv.get_message(user.id, message_id)

        # Run through wiki processor
        if req.args.get('format', 'html') != 'raw':
            env = self.env
            msg_env = message.env
            context = Context.from_request(req)

            # If message is sent from different env, load it for correct links
            if msg_env and msg_env != this_env:
                env = open_environment(os.path.join(
                    self.config.get('multiproject', 'sys_projects_root'),
                    msg_env),
                    use_cache=True
                )

            # Render to HTML using wiki formatter. Set href to context in order to get correct links
            context.href = Href('/%s' % env.path.rsplit('/', 1)[1])
            message.content = format_to_html(self.env, context, message.content)

        if not message:
            return send_json(req, {'result': 'Message cannot be not found'}, status=404)

        # Permission check: if user is in recipients
        if user.id in message.recipients and 'MESSAGE_VIEW' in home_perm:
            return send_json(req, message)

        self.log.warning('Permission denied for %s to see message: (sender: %s, receivers: %s)' % (req.authname, message.sender_id, message.recipients))

        return send_json(req, {'result': 'Permission denied'}, status=403)


    def _post_message(self, req):
        """
        Handles the message post request

        :param Request req:
            Trac POST request, with following arguments:

            - content: Message content. Can contain wiki markup
            - group_id: Send message to specific user

        """
        group_id = req.args.get('group_id')
        msgsrv = self.env[MessageService]
        mg = msgsrv.get_message_group(group_id)

        userstore = get_userstore()
        user = userstore.getUser(req.authname)
        content = req.args.get('content')

        # Ensure content and receiver is set
        if not content or not any((mg.recipients, group_id)):
            self.log.warning('Invalid rest request')
            return send_json(req, {'result': 'Invalid rest request'}, status=400)

        # Check permission from home env
        home_env = HomeProject().get_env()
        perm = PermissionCache(home_env, req.authname)

        # Check permission
        if 'MESSAGE_CREATE' not in perm or user.id not in mg.recipients:
            return send_json(req, {'result': 'Permission denied'}, status=403)

        # Send message using MessageService
        msgsrv.post(
            content,
            sender=user,
            group=mg,
        )

        self.log.info('Handled REST API request (%s) successfully' % req.path_info)

        # Return JSON presentation of the created message
        return send_json(req, 'OK')


    def _list_message_groups(self, req):
        """
        Returns list of message groups: messages grouped by the sender
        """
        # Check permission from home env
        home_env = HomeProject().get_env()
        perm = PermissionCache(home_env, req.authname)
        query = req.args.get('q') or None # If empty, return latest
        limit = req.args.get('limit', 5)

        # Convert types
        try:
            limit = int(limit)
        except ValueError:
            return send_json(req, {'result': 'Invalid request'}, status=403)

        # Check permission
        if 'MESSAGE_VIEW' not in perm:
            return send_json(req, {'result': 'Permission denied'}, status=403)

        msgsrv = self.env[MessageService]
        userstore = get_userstore()
        user = userstore.getUser(req.authname)

        # TODO: Permission checks?
        return send_json(req, msgsrv.get_messages_grouped_by(user.id, query=query, limit=limit))

    def _get_message_group(self, req):
        """
        Returns the group information based on receivers/group information provided in request::

            /api/message/group?recipients=123,345,235&action=create
            => {id: 2, recipients: [123, 345, 235]}

            /api/message/group?group_id=2&action=view
            => {id: 2, recipients: [123, 345, 235]}

            /api/message/group?recipients=123,345&group_id=2&action=update
            => {id: 2, recipients: [123]}

            /api/message/group?group_id=2
            => {id: 2, recipients: [123, 345]}

            /api/message/group?recipients=123,345,235&action=create
            => {id: 3, recipients: [123, 345, 235]}

        """
        msgsrv = self.env[MessageService]

        # Check permission from home env
        home_env = HomeProject().get_env()
        perm = PermissionCache(home_env, req.authname)

        # Check permission
        if 'MESSAGE_VIEW' not in perm:
            return send_json(req, {'result': 'Permission denied'}, status=403)

        userstore = get_userstore()
        user = userstore.getUser(req.authname)
        recipients = []
        action = 'view'
        group_id = None
        group_title = None
        mg = None

        # Read parameters
        try:
            recipients_raw = req.args.get('recipients')
            group_title = req.args.get('title', group_title)
            if recipients_raw:
                recipients += [long(repid) for repid in recipients_raw.split(',')]
            action = req.args.get('action', action)
            group_id = req.args.get('group_id', group_id)

        except ValueError:
            return send_json(req, {'result': 'Invalid request'}, status=500)

        try:
            # Create new group
            if action == 'create':
                mg = msgsrv.create_message_group(user.id, group_title, recipients)

                self.log.info('User %s created a message group: %s' % (user, mg.id))

            # Fetch info from existing group
            elif action == 'view':
                if not group_id:
                    raise Exception('Group id missing in request')

                mg = msgsrv.get_message_group(group_id)

            # Update exiting group
            elif action == 'update':
                if not group_id:
                    raise Exception('Group id missing in request')

                # Only existing recipients (if any) can add/remove recipients
                mg = msgsrv.get_message_group(group_id)
                if mg.recipients and user.id not in mg.recipients:
                    self.log.warning('User %s tried adding/removing recipients without being one of them' % user)
                    return send_json(req, {'result': 'Permission denied'}, status=403)

                # Update the recipients
                mg = msgsrv.update_message_group(group_id, user.id, {'recipients': recipients, 'title': group_title})
                self.log.info('User %s updated the message group: %s' % (user, mg.id))

            # No action, no valid request
            else:
                raise Exception('Action missing in request')

        except Exception, ex:
            self.log.exception('Error in message group request')
            return send_json(req, {'result': 'Failed to retrieve group information: {0}'.format(ex)}, status=500)

        return send_json(req, mg)

    def _mark_read(self, req):
        """
        Marks message / messages within a group read

        :param Request req:
            Trac requst with following arguments:

            - message_id: Message id
            - group_id: Message group id

            .. NOTE::

               Either ``message_id`` or ``group_id`` needs to be provided

        :return: JSON response with result: 'OK' or error
        """
        # NOTE: Depends on NotificationSystem. Moving method in NotificationRestAPI does not make sense either
        # because Notification system is generic and does not know about the MessageGroups

        if not self.env.is_component_enabled('multiproject.common.notifications.push.NotificationSystem'):
            return send_json(req, {'result': 'NotificationSystem is not enabled/available'}, status=500)

        group_id = req.args.get('group_id', None)
        message_id = req.args.get('message_id', None)

        # Load NotificationSystem
        from multiproject.common.notifications.push import NotificationSystem
        ns = self.env[NotificationSystem]

        # Load user (anon check already done at this point)
        user = get_userstore().getUser(req.authname)
        chname = ns.generate_channel_name(user_id=user.id)

        # Load specified message group
        if message_id:
            msg = Message.get(message_id)
            if not msg:
                return send_json(req, {'result': 'Message was not found'}, status=404)
            ns.reset_notification(chname, {'id': msg.id, 'type': 'message'})

        # Reset all messages within a group
        elif group_id:
            mg = MessageGroup.get(group_id)
            if not mg:
                return send_json(req, {'result': 'Message group or user was not found'}, status=404)

            # Generate notification keys based on group messages
            notification_keys = ['message-%d' % msg.id for msg in mg.get_messages()]
            ns.reset_notifications(chname, keys=notification_keys)

        # Missing required arguments
        else:
            return send_json(req, {'result': 'Invalid request'}, status=400)

        return send_json(req, {'result': 'OK'})

