# -*- coding: utf-8 -*-
import os
import re, time
from datetime import timedelta, datetime
from pkg_resources import resource_filename

from trac.core import Component, implements, TracError
from trac.env import open_environment
from trac.web.href import Href
from trac.web.chrome import ITemplateProvider, INavigationContributor, add_warning, add_notice, tag, Markup
from trac.web.api import IAuthenticator, IRequestHandler
from trac.util import hex_entropy
from trac.util.translation import _

from multiproject.common.notifications.email import EmailNotifier
from multiproject.core.util import safe_address
from multiproject.core.util.tokens import SaltedToken
from multiproject.core.users import get_userstore
from multiproject.core.auth.auth import Authentication
from multiproject.core.cache.user_cache import UserCache
from multiproject.core.cache.cookie_cache import CookieCache
from multiproject.core.db import admin_transaction, admin_query, safe_string


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

    def get_active_navigation_item(self, req):
        """ Item that will be active when this page is loaded
        """
        return 'login'

    def get_navigation_items(self, req):
        """ Introduce some new items into metanav for log(in/out) purposes
        """
        store = get_userstore()
        user = store.getUser(req.authname)
        home_env = get_home(self.env)

        if user and req.authname != 'anonymous':
            yield ('metanav', 'login', 'logged in as %s' % user.getDisplayName())
            yield ('metanav', 'logout',
                tag.a('Logout', href = req.href('user', action = 'logout')))
        else:
            login_href = Href(get_homeurl(home_env))
            current_uri = req.base_url + req.path_info
            yield ('metanav', 'login',
                tag.a('Login', href = login_href('user' , action = 'login', goto = current_uri)))

    def match_request(self, req):
        """ Log(in/out) requests are handled on /user path
        """
        # valid urls are "/home/user" and "/home/user?action=xxxxx"
        # "/home/user/xxxxx" is handled by home/frontpage/myprojects.py (public user page)
        return re.match(r'/user?(?:action=.+)?$', req.path_info)

    def process_request(self, req):
        """
        Process log(in/out) requests
        """
        act = req.args.get('action')
        home_env = get_home(self.env)
        home_url = get_homeurl(home_env)

        if not act:
            referer = safe_address(self.env, req.get_header('Referer'))
            if referer:
                self.set_goto(req, referer)
            else:
                self.set_goto(req, req.args.get('goto'))
        else:
            self.set_goto(req, req.args.get('goto'))

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
            req.redirect(home_url)

        return self._show_login(req)

    def set_goto(self, req, goto):
        """ Sets goto parameter into session
        """
        safegoto = safe_address(self.env, goto)

        if safegoto:
            req.session['goto'] = safegoto
            req.session.save()

    def get_goto(self, req):
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

    def authenticate(self, req):
        """ Checks if user authenticated or not
            Returns username on success ow. None
        """
        authname = None

        # If user have authenticated with digest
        if req.remote_user:
            authname = req.remote_user

        # If user have authenticated with cookie
        if req.incookie.has_key('trac_auth'):
            authname = self._get_name_for_cookie(req, req.incookie['trac_auth'])

        # If user have not authenticated
        if not authname:
            return None

        return authname

    def _do_logout(self, req):
        """ Log the user out.
        """
        home_env = get_home(self.env)
        self._delete_db_cookies(req)
        self._expire_cookie(req)
        req.redirect(home_env.project_url)

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
                self.set_goto(req, self.env.config.get('multiproject', 'initial_login_page'))
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

        home_env = get_home(self.env)
        home_url = get_homeurl(home_env)
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
            return req.redirect(home_url)

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
        req.redirect(self.get_goto(req))

    def _init_session(self, req, remote_user):
        # Some modules uses name and email data from session, so lets put them there
        userstore = get_userstore()
        user = userstore.getUser(remote_user)
        req.session['name'] = user.getDisplayName()
        req.session['email'] = user.mail
        req.session['displayname'] = user.getDisplayName()
        req.session.save()

    def _outcookie(self, req, cookie, expires = None):
        # Cookie version0. In the future change this for version1 and replace field expires with max-age.
        # Currently IE does not support cookie v2.
        req.outcookie['trac_auth'] = cookie
        req.outcookie['trac_auth']['path'] = self.env.config.get('multiproject', 'url_projects_path', '/')
        if expires:
            req.outcookie['trac_auth']['expires'] = expires
        if self.env.secure_cookies:
            req.outcookie['trac_auth']['secure'] = True
        if hasattr(self.env, 'httponly_cookies'):
            if self.env.httponly_cookies:
                req.outcookie['trac_auth']['httponly'] = True
        else:
            if not GlobalLoginModule.patch_warned:
                self.log.warning('Trac environment object does not have httponly_cookies option - missing a patch?')
                GlobalLoginModule.patch_warned = True

    def _expires(self):
        cookie_lifetime = self.env.config.getint('multiproject', 'cookie_lifetime')
        if cookie_lifetime > 0:
            expires = datetime.utcnow() + timedelta(minutes = cookie_lifetime)
            return expires.strftime('%a, %d %b %Y %H:%M:%S')
        else:
            return None

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
        self._outcookie(req, cookie, self._expires())

        # Create cached cookie
        self.cookie.add(cookie)

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
        if req.incookie.has_key('trac_auth'):
            cache = UserCache.instance()
            sql_safe_cookie_value = safe_string(req.incookie['trac_auth'].value)
            cache.clearUserCookieName(sql_safe_cookie_value)

            # Remove cached cookie
            self.cookie.remove(sql_safe_cookie_value)

            # Create cookie
            self._outcookie(req, '', -10000)

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
                    self._outcookie(req, sql_safe_cookie_value, self._expires())
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
                self._outcookie(req, sql_safe_cookie_value, self._expires())
            self.cookie.add(sql_safe_cookie_value)

        cache.setUserCookieName(sql_safe_cookie_value, row[0])
        return row[0]

    def get_templates_dirs(self):
        return [resource_filename('multiproject.common.users', 'templates')]

    def get_htdocs_dirs(self):
        return []


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
        # Open home environment
        home_env = get_home(self.env)
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
            add_warning(req, _('Unknown username'))
            return req.redirect(back_url)

        # Check token
        if token != get_token(self.env, user):
            add_warning(req, _('Invalid request'))
            return req.redirect(back_url)

        # Construct and send email
        manage_url = home_env.abs_href(
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
    Load home environment with current environment
    """
    return open_environment(os.path.join(
        project_env.config.get('multiproject', 'sys_projects_root'),
        project_env.config.get('multiproject', 'sys_home_project_name')),
        use_cache=True
    )

def get_homeurl(home_env, absolute=False):
    """
    Returns the URL to home project
    """
    if absolute:
        return home_env.abs_href(home_env.config.get('multiproject', 'sys_home_project_name'))
    return home_env.href(home_env.config.get('multiproject', 'sys_home_project_name'))
