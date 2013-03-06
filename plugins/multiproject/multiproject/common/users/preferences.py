# -*- coding: utf-8 -*-
"""
Module contains custom user preferences panels
"""
from trac.config import Option
from trac.core import Component, implements, TracError
from trac.prefs.api import IPreferencePanelProvider
from trac.web.api import ITemplateStreamFilter, IRequestFilter
from trac.web.chrome import add_warning, add_notice, _, add_stylesheet, add_script
from genshi.filters.transform import Transformer

from multiproject.core.configuration import conf
from multiproject.core.users import get_userstore
from multiproject.core.auth.auth import Authentication
from multiproject.core.ssh_keys import CQDESshKeyStore, SshKey
from multiproject.common.web.resource import IJSONDataPublisherInterface


class SharedSyntaxHighlight(Component):
    """
    Hides the internal Syntax Highlight user preference section by and forces
    the single style instead throughout the projects. The style name is defined in configuration::

        [multiproject]
        ; Name of the pygments' style: trac, monokai, autumn, ..
        pygments_theme_name = trac

    To list available styles, run::

        >>> from pygments.styles import STYLE_MAP
        >>> STYLE_MAP.keys()
        ['monokai', 'manni', 'perldoc', 'borland', 'colorful', 'default', 'murphy', 'vs', 'trac',
        'tango', 'fruity', 'autumn', 'bw', 'emacs', 'vim', 'pastie', 'friendly', 'native']

    """
    implements(ITemplateStreamFilter, IRequestFilter)

    pygments_theme_name = Option('multiproject', 'pygments_theme_name', 'trac', 'Pygments style to use in all views')

    # ITemplateStreamFilter methods

    def filter_stream(self, req, method, filename, stream, data):
        """
        Removes Syntax Highlight tab from user preferences view
        """
        # Filter only user preference view
        if not req.path_info.startswith('/prefs'):
            return stream

        # Remove Syntax Highlight tab from user preferences
        trans = Transformer('.//li[@id="tab_pygments"]').remove()
        return stream | trans

    # IRequestFilter methods

    def pre_process_request(self, req, handler):
        """
        Process request to add some data in request
        """
        return handler

    def post_process_request(self, req, template, data, content_type):
        """
        Add pygments colorscheme stylesheet into request
        """
        add_stylesheet(req, '/pygments/{0}.css'.format(self.pygments_theme_name))

        return template, data, content_type


class HideGeneralPreferences(Component):
    """
    Hides the Trac's General preferences tab in user settings
    """
    implements(ITemplateStreamFilter)

    # ITemplateStreamFilter methods

    def filter_stream(self, req, method, filename, stream, data):
        """
        Removes Syntax Highlight tab from user preferences view
        """
        # Redirect to basic tab
        if req.path_info == '/prefs':
            return req.redirect(req.href('/prefs/basic'))

        # Remove General (first) tab from user preferences
        if req.path_info.startswith('/prefs'):
            trans = Transformer('.//ul[@id="tabs"]/li[1]').remove()
            return stream | trans

        return stream


class UserImagePreferencePanel(Component):
    """ Preference panel for changing user image
    """
    implements(IPreferencePanelProvider, ITemplateStreamFilter, IJSONDataPublisherInterface)

    def get_preference_panels(self, req):
        """ Give name of the panel
        """
        user = get_userstore().getUser(req.authname)
        has_external_avatar = Authentication().has_external_profile(user)
        if req.authname != 'anonymous' and not has_external_avatar:
            yield ('image', 'Face image')

    def render_preference_panel(self, req, panel):
        """ Renders preference panel and handles image change on POST
        """

        if req.authname == 'anonymous':
            raise TracError("User is not authenticated", "No access")

        userstore = get_userstore()
        user = userstore.getUser(req.authname)

        if req.method == 'POST':
            if 'removeicon' in req.args:
                user.icon = None
                userstore.updateUser(user)
            elif 'icon' in req.args:
                user.createIcon(req.args['icon'])

                if user.icon:
                    userstore.updateUser(user)

        data = {'user':user, 'base_path':req.base_path}
        if 'limitexceeded' in req.args:
            add_warning(req, 'Picture you tried to upload was too big. Try a smaller one.')

        return 'multiproject_user_prefs_image.html', data

    def filter_stream(self, req, method, filename, stream, formdata):
        """ Makes /prefs/image use correct enctype
        """
        if filename == 'multiproject_user_prefs_image.html' and req.path_info.endswith('/prefs/image'):
            return stream | Transformer('//form[@id="userprefs"]').attr('enctype', 'multipart/form-data')
        return stream

    # IJSONDataPublisherInterface methods

    def publish_json_data(self, req):
        return {
            'conf': {
                'dateformat': 'mm/dd/y',
        }}


class UserBasicInfo(Component):
    """ Preference panel for changing user basic information
    """
    implements(IPreferencePanelProvider)

    def get_preference_panels(self, req):
        """ Give name of the panel
        """
        if req.authname != 'anonymous':
            yield ('basic', 'Basic information')

    def render_preference_panel(self, req, panel):
        """ Renders preference panel and handles information change on POST
        """
        add_script(req, 'multiproject/js/jquery-ui.js')
        add_script(req, 'multiproject/js/preference.js')
        add_stylesheet(req, 'multiproject/css/jquery-ui.css')

        if req.authname == 'anonymous':
            raise TracError("User is not authenticated", "No access")

        userstore = get_userstore()
        user = userstore.getUser(req.authname)
        is_local = userstore.is_local(user)

        if req.method == 'POST':
            user = self._do_save(req, user)

        data = {'user':user,
                'has_agreed_terms':user.status != user.STATUS_INACTIVE,
                'is_local': is_local
                }
        return 'multiproject_user_prefs_basic.html', data

    def _do_save(self, req, user):
        """ Update user information into database
        """
        userstore = get_userstore()

        if not req.args.get('mail'):
            add_warning(req, _('User should have an e-mail address'))
            return user

        user.mail = req.args.get('mail')

        if not req.args.get('lastName'):
            add_warning(req, _('Last name required'))
            return user

        # NOTE: Values are escaped in userstore update
        user.lastName = req.args.get('lastName')
        user.givenName = req.args.get('givenName')
        user.mobile = req.args.get('mobile')

        if userstore.updateUser(user):
            user = userstore.getUser(user.username)
            add_notice(req, _('Updated user settings'))

            if req.args.get('approve') == 'on' and user.status == user.STATUS_INACTIVE:
                user.activate()
                add_notice(req, _("Your account is now activated."))

            return user

        add_warning(req, _('Failed to update user'))
        return user


class UserPasswordPreferencePanel(Component):
    """ Preference panel for changing password
    """
    implements(IPreferencePanelProvider)

    def get_preference_panels(self, req):
        userstore = get_userstore()
        user = userstore.getUser(req.authname)

        if req.authname != 'anonymous' and userstore.is_local(user):
            yield ('changepw', 'Change password')

    def render_preference_panel(self, req, panel):
        userstore = get_userstore()
        user = userstore.getUser(req.authname)

        if req.authname == 'anonymous' or not userstore.is_local(user):
            raise TracError("User is not authenticated or preferences are maintained separate service", "No preferences")

        if req.method == 'POST':
            self.changePassword(req)

        return 'multiproject_user_prefs_password.html', {}

    def changePassword(self, req):
        userstore = get_userstore()
        user = userstore.getUser(req.authname)

        oldpw = req.args.get('oldpassword')
        newpw = req.args.get('newpassword')

        if not oldpw or not userstore.userExists(req.authname, oldpw):
            add_warning(req, _('Old password is invalid'))
            return user

        if not newpw or len(newpw) < 7:
            add_warning(req, _('New password should be at least 7 characters long'))
            return user

        if newpw != req.args.get('confirmpw'):
            add_warning(req, _('Passwords do not match'))
            return user

        if not userstore.updatePassword(user, newpw):
            add_warning(req, _('Failed to change the password'))
            return user

        add_notice(req, _('Password changed'))
        return user


class UserSshKeys(Component):
    """ Preference panel for managing ssh keys
    """
    implements(IPreferencePanelProvider)

    def get_preference_panels(self, req):
        """ Give name of the panel
        """
        if req.authname != 'anonymous' and self.config.getbool('multiproject', 'gitosis_enable'):
            yield ('ssh_keys', 'SSH keys')

    def render_preference_panel(self, req, panel):
        """ Renders preference panel and handles information change on POST
        """
        if req.authname == 'anonymous':
            raise TracError("User is not authenticated", "No access")

        data = {}
        key_store = CQDESshKeyStore.instance()
        user = get_userstore().getUser(req.authname)

        if req.method == 'POST':
            ssh_key = req.args.get('ssh_key')
            delete_key = req.args.get('deletelist')

            if ssh_key:
                user = self._do_save(req, user)
            elif delete_key:
                user = self._do_deletes(req, user)
            else:
                add_warning(req, _('Please provide data'))

        keys = key_store.get_ssh_keys_by_user_id(user.id)
        data['keys'] = keys if keys else None

        # This is to prevent adding of more than one ssh password.
        # Remove this if we support more in the future.
        if keys:
            data['hide_add_dialog'] = True

        data['domain'] = conf.domain_name
        data['user'] = user

        return 'multiproject_user_prefs_ssh_keys.html', data

    def _do_save(self, req, user):
        """
        Save ssh key into database
        """
        if not req.args.get('ssh_key'):
            add_warning(req, _('Failed to add SSH key: Key is required'))
            return user

        ssh_key = req.args.get('ssh_key')
        ssh_key = SshKey.remove_comment_from_key_string(ssh_key)

        if not SshKey.validate_key_string(ssh_key):
            add_warning(req, _('Failed to add SSH key: invalid SSH key'))
            return user

        description = req.args.get('description')
        if len(description) > 200:
            add_warning(req, _('Failed to add SSH key: Too long description'))
            return user

        key_store = CQDESshKeyStore.instance()
        user_id = user.id

        if key_store.add_ssh_key(user_id, ssh_key, description):
            add_notice(req, _('New SSH key added (validation takes about 1 minute)'))
            return user

        add_warning(req, _('Failed to add SSH key: Server error'))
        return user

    def _do_deletes(self, req, user):
        """ Delete ssh key from database
        """
        key_store = CQDESshKeyStore.instance()
        user_id = user.id

        key_ids = req.args.get('deletelist')
        key_ids = isinstance(key_ids, list) and key_ids or [key_ids]

        for key_id in key_ids:
            if key_id:
                if key_store.remove_ssh_key(user_id, key_id):
                    add_notice(req, _('SSH key deleted'))
                else:
                    add_warning(req, _('Failed to delete SSH key: Server error.'))

        return user

