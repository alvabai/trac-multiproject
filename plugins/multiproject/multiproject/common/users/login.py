# -*- coding: utf-8 -*-
"""
Module provides the user authentication UI for MultiProject authentication backends.

GlobalLoginModule:
    Handles following URLs:

    - ``/<env>/user``: Show login page
    - ``/<env>/user?action=do_login``: Handle login request
    - ``/<env>/user?action=logout``: Handle logout request
    - ``/<env>/user?action=approve``: Approve service terms

HTTPBasicAuthenticator:
    Checks if request contains ``?auth=basic`` and challenges client
    for basic authentication. Finally redirects to same page as requested

    .. NOTE::

        Some HTTP clients (e.g. curl) do not support/work when redirect is sent after authentication.
        To prevent redirect, clients can set additional ``redirect=false`` in arguments.

        Example::

            http://localhost/myfeed.rss?auth=basic&redirect=false

PasswordRestRequestHandler:
    Provides a link (/<env>/user/pwreset) for requesting a new password

"""
import base64
import urllib
import os
import re, time
from datetime import timedelta, datetime
from pkg_resources import resource_filename

from trac.core import Component, implements, TracError
from trac.env import open_environment
from trac.web.chrome import ITemplateProvider, INavigationContributor, add_warning, add_notice, tag, Markup
from trac.web.api import IAuthenticator, IRequestHandler
from trac.util import hex_entropy
from trac.util.translation import _

from multiproject.core.util import safe_address
from multiproject.core.util.tokens import SaltedToken
from multiproject.core.users import get_userstore
from multiproject.core.auth.auth import Authentication
from multiproject.core.cache.user_cache import UserCache
from multiproject.core.cache.cookie_cache import CookieCache
from multiproject.core.db import admin_transaction, admin_query, safe_string


COOKIE_AUTH = 'trac_auth'
LOGIN_MODULE_REGEXP = re.compile(r'/user(?:action=.+)?$')


class GlobalLoginModule(Component):
    """ This module is similar as trac.web.auth.LoginModule
        Only this module authenticates for all trac environments at once
        (cookie data is held on global db instead of trac instance db)
    """
    implements(IAuthenticator, ITemplateProvider, IRequestHandler, INavigationContributor)
    patch_warned = False

    def __init__(self):
        # override trac's Preferences link, which does not check that user is logged in
        def get_navigation_items_check_login(self, req):
            if req.authname != 'anonymous':
                yield ('metanav', 'prefs', tag.a(_('Preferences'), href = req.href.prefs()))
        from trac.prefs.web_ui import PreferencesModule
        PreferencesModule.get_navigation_items = get_navigation_items_check_login

        self.cookie = CookieCache.instance()

    # ITemplateProvider methods

    def get_templates_dirs(self):
        return [resource_filename('multiproject.common.users', 'templates')]

    def get_htdocs_dirs(self):
        return []

    # INavigationContributor methods

    def get_active_navigation_item(self, req):
        """ Item that will be active when this page is loaded
        """
        return 'login'

    def get_navigation_items(self, req):
        """ Introduce some new items into metanav for log(in/out) purposes
        """
        store = get_userstore()
        user = store.getUser(req.authname)

        if user and req.authname != 'anonymous':
            yield ('metanav', 'login', 'logged in as %s' % user.getDisplayName())
            yield ('metanav', 'logout',
                tag.a('Logout', href = req.href('user', action = 'logout')))
        else:
            current_uri = req.base_url + req.path_info
            yield ('metanav', 'login',
                tag.a('Login', href = self.env.home_href.user(action = 'login', goto = current_uri)))

    # IRequestHandler methods

    def match_request(self, req):
        """ Log(in/out) requests are handled on /user path
        """
        # valid urls are "/home/user" and "/home/user?action=xxxxx"
        # "/home/user/xxxxx" is handled by home/frontpage/myprojects.py (public user page)
        # TODO: Move the request handler part into home (it should be disabled in projects)
        return bool(LOGIN_MODULE_REGEXP.match(req.path_info))

    def process_request(self, req):
        """
        Process log(in/out) requests
        """
        act = req.args.get('action')

        if not act:
            referer = safe_address(self.env, req.get_header('Referer'))
            if referer:
                self._set_goto(req, referer)
            else:
                self._set_goto(req, req.args.get('goto'))
        else:
            self._set_goto(req, req.args.get('goto'))

        actions = {
            'login':self._show_login,
            'do_login':self._do_login,
            'logout':self._do_logout,
            'approve':self._do_approve
        }

        if actions.has_key(act):
            return actions[act](req)

        # Already logged in
        if req.authname != 'anonymous':
            req.redirect(self.env.home_href())

        return self._show_login(req)

    # IAuthenticator methods

    def authenticate(self, req):
        """ Checks if user authenticated or not
            Returns username on success ow. None
        """
        authname = None

        # If user have authenticated with digest
        if req.remote_user:
            authname = req.remote_user

        # If user have authenticated with cookie
        if req.incookie.has_key(COOKIE_AUTH):
            authname = self._get_name_for_cookie(req, req.incookie[COOKIE_AUTH])

        # If user have not authenticated
        if not authname:
            return None

        return authname

    # Internal methods

    def _set_goto(self, req, goto):
        """ Sets goto parameter into session
        """
        safegoto = safe_address(self.env, goto)

        if safegoto:
            req.session['goto'] = safegoto
            req.session.save()

    def _get_goto(self, req):
        """ Goto parameter should be read only once.
            Side-effect of deleting goto param from session
        """
        if req.session.has_key('goto'):
            goto = req.session['goto']
            del req.session['goto']
            return goto
        else:
            return req.base_path

    def _show_login(self, req, optdata=None):
        """
        Show login page
        """
        data = {'login_page':True}

        if optdata and isinstance(optdata, dict):
            data.update(optdata)
        return 'multiproject_login.html', data, None

    def _do_logout(self, req):
        """ Log the user out.
        """
        self._delete_db_cookies(req)
        self._expire_cookie(req)
        req.redirect(self.env.project_url)

    def _request_legal_approval(self, req, remote_user):
        data = {'username': remote_user}
        return "multiproject_legal.html", data, None

    def _do_approve(self, req):
        if req.method != 'POST':
            return self._show_login(req)
        username = req.args.get('username')

        if not username:
            message = "Login error. No user found!"
            return 'multiproject_login.html', {'error':message, 'login_page':True}, None

        users = get_userstore()
        user = users.getUser(username)
        if not user:
            add_warning(req, "Legal approval process failed. User not found.")
        elif req.args.has_key('approve'):
            if req.args.get('approve') == 'on':
                user.activate()
                self._set_goto(req, self.env.config.get('multiproject', 'initial_login_page'))
                add_notice(req, _("Your account is now activated. You can now log in."))
                return self._show_login(req)

        add_warning(req, "You need to approve legal text before you can login")
        return self._request_legal_approval(req, username)

    def _do_login(self, req):
        """
        Logs user in
        Works so that first it is checked that user have inserted correct
        password. If yes, then create cookie

        Cookie contains random hex entropy that is also stored into database
        When user next time requests page data in cookie and db should match
        """
        if req.method != 'POST':
            return self._show_login(req)

        remote_user = req.args.get('username')
        password = req.args.get('password')

        # If not params
        if not remote_user or not password:
            return self._show_login(req)

        # Try authentication
        auth = Authentication()
        auth_username = auth.authenticate(remote_user, password)

        # User is already logged in
        if req.authname == auth_username:
            add_notice(req, _('User is already logged in as %s.' % req.authname))
            return req.redirect(self.env.home_href())

        # Authentication failed
        if not auth_username:
            # Load user for salt
            userstore = get_userstore()
            user = userstore.getUser(remote_user)
            if not user:
                add_notice(req, _('Incorrect username or password - please try again'))
                return self._show_login(req)

            # Provide password reset link for local users that have an author
            if userstore.is_local(user) and userstore.get_user_author(user):
                token = get_token(self.env, user)
                reset_link = tag.a('request new password', href=req.href('/user/pwreset', username=remote_user, token=token))
                add_notice(req, Markup("Incorrect username or password - please try again or %s" % reset_link))
            else:
                add_notice(req, _("Incorrect username or password - please try again"))

            return self._show_login(req)

        return self._select_login_action(req, auth_username)

    def _select_login_action(self, req, remote_user):
        """
        Select login action based on user status.

        - If user is expired, error msg is shown
        - If user is active, user will be logged in
        - If user is inactive, legal process is started
        - Otherwise user has no way of logging in (is banned or disabled)

        """
        user_store = get_userstore()
        user = user_store.getUser(remote_user)
        if not user:
            # This may happen if authentication method is case-insensitive
            add_notice(req, _("Incorrect username or password - please try again"))
            return self._show_login(req)

        # Check if expired
        if user.expires and user.expires <= datetime.utcnow():
            author = user_store.get_user_author(user)
            if author:
                add_warning(req, _('Account expired. Contact {0} for extension'.format(author.getDisplayName())))
            else:
                add_warning(req, _('Account expired. Contact service support for extension'))
            return self._show_login(req)

        # User is authentic but can not log in before knowing he is not banned or disabled or activation required
        if user.status == user.STATUS_INACTIVE and self.env.config.getbool('multiproject', 'login_requires_agreed_terms'):
            return self._request_legal_approval(req, remote_user)

        if user.status in (user.STATUS_ACTIVE, user.STATUS_INACTIVE):
            return self._login_success(req, remote_user)

        add_warning(req, _("User status is '%s'. Can not log in." % user_store.USER_STATUS_LABELS[user.status]))
        return self._show_login(req)

    def _login_success(self, req, remote_user):
        self._create_auth_cookie(req, remote_user)
        self._init_session(req, remote_user)
        req.authname = remote_user
        req.redirect(self._get_goto(req))

    def _init_session(self, req, remote_user):
        # Some modules uses name and email data from session, so lets put them there
        userstore = get_userstore()
        user = userstore.getUser(remote_user)
        req.session['name'] = user.getDisplayName()
        req.session['email'] = user.mail
        req.session['displayname'] = user.getDisplayName()
        req.session.save()

    def _set_outcookie(self, req, cookie, expires=None):
        """
        Set out cookies for request

        .. NOTE::

            Cookie version0. In the future change this for version1 and replace field expires with max-age.
            Currently IE does not support cookie v2.

        :param req: Trac request
        :param str cookie: Cookie value. Can be empty.
        :param datetime expires: Optional cookie expiration time. Defaults to None (do not expire)
        """
        cookie_lifetime = self.env.config.getint('multiproject', 'cookie_lifetime')
        req.outcookie[COOKIE_AUTH] = cookie
        req.outcookie[COOKIE_AUTH]['path'] = self.env.config.get('multiproject', 'url_projects_path', '/')

        # Set optional expiration time to cookie
        if expires or cookie_lifetime > 0:
            if not expires:
                expires = datetime.utcnow() + timedelta(minutes = cookie_lifetime)
            req.outcookie[COOKIE_AUTH]['expires'] = expires.strftime('%a, %d %b %Y %H:%M:%S')

        if self.env.secure_cookies:
            req.outcookie[COOKIE_AUTH]['secure'] = True

        if hasattr(self.env, 'httponly_cookies'):
            if self.env.httponly_cookies:
                req.outcookie[COOKIE_AUTH]['httponly'] = True
        else:
            if not GlobalLoginModule.patch_warned:
                self.log.warning('Trac environment object does not have httponly_cookies option - missing a patch?')
                GlobalLoginModule.patch_warned = True

    def _create_auth_cookie(self, req, remote_user):
        cookie = hex_entropy()

        sql = """
        INSERT IGNORE INTO auth_cookie (cookie, name, ipnr, time)
        VALUES (%s, %s, %s, %s)
        """
        with admin_transaction() as cursor:
            try:
                cursor.execute(sql, (cookie, remote_user, req.remote_addr, int(time.time())))
            except Exception:
                self.log.exception("Failed to store auth cookie into database")
                raise

        # Make new cookie
        self._set_outcookie(req, cookie)

        # Create cached cookie
        self.cookie.add(cookie)
        return cookie

    def _delete_db_cookies(self, req):
      """ Delete cookie from auth_cookie table and
      wipe also older than 10 days old cookies.
      """
      query = "DELETE FROM auth_cookie WHERE name = %s OR time < %s"
      with admin_transaction() as cursor:
          try:
              cursor.execute(query, (req.authname, int(time.time()) - 86400 * 10))
          except Exception:
              self.log.exception("Failed to delete cookie for: %s" % req.authname)

    def _expire_cookie(self, req):
        """ Instruct the user agent to drop the auth cookie by setting the
            "expires" property to a date in the past.
        """
        if req.incookie.has_key(COOKIE_AUTH):
            cache = UserCache.instance()
            sql_safe_cookie_value = safe_string(req.incookie[COOKIE_AUTH].value)
            cache.clearUserCookieName(sql_safe_cookie_value)

            # Remove cached cookie
            self.cookie.remove(sql_safe_cookie_value)

            # Create cookie by setting expiration to past
            self._set_outcookie(req, cookie='', expires=(datetime.utcnow() - timedelta(10000)))

    def _get_name_for_cookie(self, req, cookie, send_cookie = True):
        """ Fetch cookie->username from database based on cookie value
        """
        cache = UserCache.instance()
        sql_safe_cookie_value = safe_string(cookie.value)

        active = self.cookie.get(sql_safe_cookie_value)

        name = cache.getUserCookieName(sql_safe_cookie_value)
        if name:
            if not active:
                if send_cookie:
                    self._set_outcookie(req, sql_safe_cookie_value)
                self.cookie.add(sql_safe_cookie_value)
            return name

        row = None
        with admin_query() as cursor:
            try:
                cursor.execute("SELECT name FROM auth_cookie WHERE cookie=%s", (sql_safe_cookie_value,))
                row = cursor.fetchone()
            except Exception:
                self.log.exception("Failed to get the name for the cookie")

        if not row:
            # The cookie is invalid (or has been purged from the database), so
            # tell the user agent to drop it as it is invalid
            if send_cookie:
                self._expire_cookie(req)
            return None

        if not active:
            if send_cookie:
                self._set_outcookie(req, sql_safe_cookie_value)
            self.cookie.add(sql_safe_cookie_value)

        cache.setUserCookieName(sql_safe_cookie_value, row[0])
        return row[0]


class HTTPBasicAuthenticator(Component):
    """
    Component checks for ``?auth=basic`` argument in request,
    challenging for basic auth if needed

    Example::

        http://localhost/myfeed.rss?auth=basic

    """
    implements(IAuthenticator)

    # IAuthenticator methods

    def authenticate(self, req):
        """
        Does basic authentication for the HTTP client if ``auth=basic`` is set
        :param Request req: Trac request
        :return: Username if authentication succeeds, or None (also if this component does not authenticate)
        """
        # Return None: Not to be handled by this component
        if req.args.get('auth') != 'basic':
            return None

        # Check for existing session
        if req.remote_user:
            return req.remote_user

        # Parse username and password from basic authentication request
        # NOTE: user may or may not be logged in at this point
        username, password = self._parse_username_password(req)

        # Challenge for basic auth
        if username == 'anonymous':
            req.send_header('WWW-Authenticate', 'Basic realm="Authenticate"')
            req.send('Authentication required', content_type='text', status=401)
            return None

        # Try authentication
        auth = Authentication()
        be_username = auth.authenticate(username, password)

        # Authentication failed
        if not be_username:
            req.send_header('WWW-Authenticate', 'Basic realm="Authenticate"')
            req.send('Authentication failure', status=401)
            return None

        self.log.debug('Authenticated user %s with basic auth: %s' % (be_username, username))
        return be_username

    # Internal methods

    def _parse_username_password(self, req):
        """
        Parse request for authorization info and parses the username / password
        from it, if found.

        :param Request req: Trac request
        :returns: Username, password tuple. Defaults to: 'anonymous', ''
        """
        username = 'anonymous'
        password = ''

        auth_header = req.get_header('authorization')

        if auth_header:
            # Authorization: Basic <base64 username and pw>
            authz_hdr = base64.b64decode(auth_header.split(' ')[1])
            user_data, pw_data = authz_hdr.split(':', 1)
            username = urllib.unquote(user_data)
            encoded_password = urllib.unquote(pw_data)

            try:
                password = encoded_password.decode('UTF-8')
            except UnicodeDecodeError as e:
                try:
                    password = encoded_password.decode('ISO-8859-1')
                except UnicodeDecodeError as e:
                    # Should not happen, since for ISO-8859-1, every string
                    # is a valid string
                    raise Exception('Password conversion from ISO-8859-1 FAILED')

        return username, password


# TODO: Move this into home, should be disabled for projects
class PasswordResetRequestHandler(Component):
    """
    Component implements the HTTP request handler that
    sends the password reset request to author.
    """
    implements(IRequestHandler)

    # IRequestHandler methods

    def match_request(self, req):
        return req.path_info.startswith('/user/pwreset')


    def process_request(self, req):
        """
        Takes the provided arguments and posts an email to author

        - username: User account whose password needs to be changed
        - token: Validation token generated by system

        """
        back_url = req.href()
        username = req.args.get('username', '')
        token = req.args.get('token', '')

        # Check if required parameters are set
        if not username or not token:
            add_warning(req, _('Invalid request'))
            return req.redirect(back_url)

        # Check if user really exists
        userstore = get_userstore()
        user = userstore.getUser(username)
        if not user:
            add_warning(req, _('Invalid request'))
            return req.redirect(back_url)

        # Check token
        if token != get_token(self.env, user):
            add_warning(req, _('Invalid request'))
            return req.redirect(back_url)

        # Construct and send email
        manage_url = self.env.abs_home_href(
            'admin/users/manage',
            username=user.username
        )
        data = {
            'user':user,
            'domain_name':self.env.config.get('multiproject', 'domain_name'),
            'manage_url':manage_url
        }

        # Get author email address
        author = userstore.get_user_author(user)
        if not author or not author.mail:
            add_warning(req, _('Author email not found - please contact service support instead'))
            return req.redirect(back_url)

        try:
            # Import module here so that multiproject.common.users can be imported easily/without circular dependencies
            from multiproject.common.notifications.email import EmailNotifier

            # Open home environment
            home_env = get_home(self.env)
            enotify = EmailNotifier(home_env, 'Password reset requested', data)
            enotify.template_name = 'multiproject_reset_password.txt'
            enotify.notify(author.mail)
            add_notice(req, _('Password reset requested - you will be informed about the new password once changed'))
        # Email sending failed
        except TracError:
            add_warning(req, _('Email sending failed - please try again later'))

        # Return back to homepage
        return req.redirect(back_url)

def get_token(env, user):
    """
    Returns SaltedToken based on given user
    :returns: Token
    :rtype: SaltedToken
    """
    return SaltedToken(env.config.get('multiproject', 'salt'), user.username, user.id, user.mail)

def get_home(project_env):
    """
    Load home environment with current environment. Returns project_env, if that is the home env.
    """
    sys_home_project_name = project_env.config.get('multiproject', 'sys_home_project_name')
    try:
        if project_env.project_identifier == sys_home_project_name:
            return project_env
    except AttributeError:
        if project_env.path.split('/')[-1] == sys_home_project_name:
            return project_env

    return open_environment(os.path.join(
        project_env.config.get('multiproject', 'sys_projects_root'),
        sys_home_project_name),
        use_cache=True
    )

def get_homeurl(home_env, absolute=False):
    """
    Returns the URL to home project
    """
    if absolute:
        return home_env.abs_href(home_env.config.get('multiproject', 'sys_home_project_name'))
    return home_env.href(home_env.config.get('multiproject', 'sys_home_project_name'))
