# -*- coding: utf-8 -*-
"""
Module provides the UI elements/views, related to the messaging.

- :py:class:`MessagesGroupBox`

"""
import pkg_resources

from trac.config import Option
from trac.core import Component, implements, TracError
from trac.perm import PermissionCache
from trac.web.api import IRequestHandler, IRequestFilter
from trac.web.chrome import INavigationContributor, ITemplateProvider, tag, _, add_script, add_stylesheet, Chrome
from trac.wiki import wiki_to_html
from trac.wiki.api import IWikiMacroProvider, parse_args

from multiproject.core.users import get_userstore, DATEFORMATS
from multiproject.common.users.api import IUserProfileActions
from multiproject.common.projects import HomeProject
from multiproject.common.messages.api import MessageService


class MessagesGroupBox(Component):
    """
    Component injects required javascript resource to request, to provide message sending/receiving
    dialog  in every view.
    """
    implements(INavigationContributor, IRequestFilter, IRequestHandler)

    # INavigationContributor methods

    def get_active_navigation_item(self, req):
        return 'messages'

    def get_navigation_items(self, req):
        if 'MESSAGE_VIEW' in req.perm:
            yield ('metanav', 'messages', tag.a(_('Messages'), **{'class': 'messages', 'href': '#'}))

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
            # NOTE: Expecting other dependencies to be imported already
            add_script(req, 'multiproject/js/messages_group_box.js')

        return template, data, content_type

    # IRequestHandler methods

    def match_request(self, req):
        return req.path_info.startswith('/message/list')

    def process_request(self, req):
        req.perm.assert_permission('MESSAGE_VIEW')

        msgsrv = self.env[MessageService]
        userstore = get_userstore()
        user = userstore.getUser(req.authname)

        message_groups = msgsrv.get_latest_message_groups(user.id, limit=15)

        # Fetch and set notifications if component is enabled
        # TODO: Move into MessageService?
        if self.env.is_component_enabled('multiproject.common.notifications.push.NotificationSystem'):
            from multiproject.common.notifications.push import NotificationSystem

            ns = self.env[NotificationSystem]
            chname = ns.generate_channel_name(user)

            try:
                # Update message objects to have notification count
                for message_group in message_groups:
                    message_keys = ['message-%s' % message.id for message in message_group.get_messages()]
                    message_group.notifications = ns.get_notifications(chname, message_keys)

            except TracError, e:
                self.log.error('Failed to retrieve notifications')

        data = {
            'message_groups': message_groups,
            'date_format': DATEFORMATS['py']
        }
        return 'multiproject_messages_group_box.html', data, None


class MessagesDialog(Component):
    """
    Component injects required javascript resource to request, to provide message sending/receiving
    dialog  in every view.
    """
    implements(IRequestFilter, IRequestHandler, ITemplateProvider, IUserProfileActions)

    placeholder_default = """
=== Messages ===
This is your chat-like messaging window where you can communicate with one or multiple recipients at once.
Messages are shown immediately and the missed ones are shown as notifications.

- Only recipients can see and post messages
- Only recipients can add/remove recipients
- Users can only see the messages that are sent while there are/were marked as recipients
- Users can still see the old messages after being removed from the recipients
- Deleting a message will only hide it from you. Rest of the receivers will still see it

Actions:
- '''Send''': Sends message. Alternatively you can use shortcut: `Ctrl+Enter`
- '''Mark all read''': Reset notifications for all the missed messages
- '''Delete and leave''': Deletes/hides all messages and removes from recipients.
  Topic will no longer be shown in listing.
- '''Close''': Close the dialog by pressing 'X' in top-right or pressing `Esc`

"""

    placeholder_text = Option('multiproject-messages', 'placeholder', default=placeholder_default, doc='Default text to show when there are no messages in messagebox')

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
            add_script(req, 'multiproject/js/jstorage.js')
            add_script(req, 'multiproject/js/transparency.js')
            add_script(req, 'multiproject/js/multiproject.js')
            add_script(req, 'multiproject/js/messages_dialog.js')
            add_stylesheet(req, 'multiproject/css/multiproject.css')
            add_stylesheet(req, 'multiproject/css/jquery-ui.css')

        return template, data, content_type

    # IRequestHandler methods

    def match_request(self, req):
        return req.path_info.startswith('/message/dialog')

    def process_request(self, req):
        req.perm.assert_permission('MESSAGE_VIEW')

        data = {
            'placeholder': wiki_to_html(self.placeholder_text, self.env, req=req)
        }
        return 'multiproject_messages_dialog.html', data, None

    # ITemplateProvider methods

    def get_templates_dirs(self):
        return [pkg_resources.resource_filename('multiproject.common.messages', 'templates')]

    def get_htdocs_dirs(self):
        return [('multiproject', pkg_resources.resource_filename(__name__, 'htdocs'))]

    # IUserProfileActions methods

    def get_profile_actions(self, req, account):
        """
        Returns
        """
        actions = []

        # Check if user has MESSAGE_CREATE in home env
        home_env = HomeProject().get_env()
        home_perm = PermissionCache(home_env, req.authname)

        if 'MESSAGE_CREATE' not in home_perm:
            return []

        # Own account
        if req.authname == account.username:
            actions.append((200, tag.a(
                _('Send message to...'),
                **{'class': 'messages-dialog', 'href': '#'}
            )))
        else:
            actions.append((200, tag.a(
                _('Send message to %s' % account.username),
                **{'class': 'messages-dialog', 'href': '#user_id=%d' % account.id}
            )))

        return actions


class MessagesMacros(Component):
    implements(IWikiMacroProvider)

    # Macros
    macros = {
        'MessageGroups': '''
Provides a block for listing message groups

Example usage:
{{{
[[MessageGroups]]
}}}
''',
    }

    # IWikiMacroProvider methods

    def get_macros(self):
        for macro in self.macros:
            yield macro

    def get_macro_description(self, name):
        return self.macros.get(name)

    def expand_macro(self, formatter, name, content, args=None):
        """
        Returns the outcome from macro.
        """
        req = formatter.req
        userstore = get_userstore()
        user = userstore.getUser(req.authname)
        msgsrv = self.env[MessageService]

        # Parse optional arguments
        if args is None:
            args = parse_args(content)
            if len(args) > 1:
                args = args[1]

        data = {
            'groups': msgsrv.get_messages_grouped_by(user.id)
        }

        # FIXME: Temporary fix for IE8 + jQuery 1.4.4 + Transparency combination
        agent = req.get_header('user-agent')
        if agent and 'MSIE 8.0' not in agent:
            add_script(req, 'multiproject/js/transparency.js')

        add_script(req, 'multiproject/js/multiproject.js')
        add_script(req, 'multiproject/js/messages_group_macro.js')

        chrome = Chrome(self.env)
        return chrome.render_template(req, 'multiproject_messages_group_macro.html', data, fragment=True)
