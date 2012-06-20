# -*- coding: utf-8 -*-
import os
import sys
from ConfigParser import ConfigParser, NoOptionError

from trac.log import logger_factory
from trac.env import open_environment

from genshi.builder import Fragment

from multiproject.core.db import get_connection
from multiproject.core.exceptions import SingletonExistsException
from multiproject.core.stubs.memcache_stub import MemcacheStub
from multiproject.core.util import safe_int
from multiproject.core.util.organizations import OrganizationUpdater
from multiproject.core.decorators import deprecated


# TODO: This is EViL practice but seems to be needed
# Project summary page with japanese announcements breaks down without this
# - Marko K / 2011

try:
    reload(sys)
    sys.setdefaultencoding("utf-8")
except:
    pass


class Configuration(object):
    """
    .. WARNING:: Avoid using!

       This is something we want to get rid of, always use Trac environment to
       read configuration when it's possible! For logging you should also use Trac
       environment's log method instead of conf.log. All classes deriving Component
       can do both of these very easily.
    """

    __instance = None
    __memcached = None

    _organizations_updated = False
    default_groups = []
    activity_factors = {}
    config_file = '/etc/trac/project.ini'

    def __init__(self):
        # Make sure that configuration is created only once
        if Configuration.__instance:
            raise SingletonExistsException("Singleton violation")

        self.config_parser = None

        # Specify, where trac configuration file is.
        self.defaults()
        self.refresh()

        # DEPRECATED: Use env.abs_href instead
        # Your server's url: 'http://some.server.com'
        self.url_service = self.default_http_scheme + '://' + self.domain_name

        # DEPRECATED: Use ref.href instead
        # Path to home page  '/trac/home'
        self.url_home_path = self.url_projects_path + "/" + self.sys_home_project_name
        # For projects: self.url_projects_path (configurable)
        # For DAV     : self.url_dav_path      (configurable)

        # Your server's url with project path: 'http://some.server.com/trac'
        # DEPRECATED: Use req.abs_href instead
        self.url_projects = self.url_service + self.url_projects_path

        # Full home project url 'http://some.server.com/trac/home'
        # DEPRECATED: Use env.href instead
        self.url_home = self.url_service + self.url_home_path

        # Statistics url
        # DEPRECATED: Use env.abs_href instead
        self.url_statistics = self.statistics_scheme + '://' + self.domain_name + '/' + self.sys_home_project_name + '/stats'

        self.start_log()

    @staticmethod
    def instance():
        if Configuration.__instance is None:
            Configuration.__instance = Configuration()
        return Configuration.__instance

    def defaults(self):
        # First initialize the ones with None default value
        self.ldap_bind_user = None
        self.ldap_bind_password = None
        self.insider_organization = None
        self.organizations = {}

        # Create a dict with the rest of the default settings
        defaults_dict = {
            'default_http_scheme': 'https',
            'domain_name': 'cqde.test.site.com',
            'url_projects_path': '/trac',
            'url_dav_path': '/dav',
            'sys_home_project_name': 'home',
            'sys_root': '/storage/trac',
            'sys_dav_root': '/storage/trac/webdav',
            'sys_projects_root': '/storage/trac/projects',
            'sys_vcs_root': '/storage/trac/repositories',
            'db_host': 'localhost',
            'db_user': 'tracuser',
            'db_password': 'password',
            'db_admin_schema_name': 'trac_admin',
            'db_analytical_schema_name': 'trac_analytical',
            'db_port': '3306',
            'visibility_db_batch_size': '5000',
            'repo_type': 'svn',
            # FIXME: This is actually theme root, not default theme path
            'default_theme_path': '/storage/trac/themes',
            'theme_name': '',

            # LDAP configuration. Maybe could be in it's on [LDAP] section or something
            'ldap_connect_path': 'ldap://localhost',
            'host_match': '',
            'ldap_uid': 'uid',
            'ldap_user_rdn': 'ou=People',
            'ldap_base_dn': 'dc=ldaphost',
            'ldap_object_classes': 'inetOrgPerson',
            'ldap_use_tsl': 'False',
            'ldap_use_sasl': 'False',
            'ldap_groups_enabled': 'False',
            'ldap_groups_attribute_name': 'memberOf',
            'ldap_users_attribute_name': 'uniqueMember',
            'ldap_groups_dn': 'ou=groups,o=company',
            'ldap_groups_cn': 'cn',
            'salt': 'TODO: Make this long and unique!',
            'organizations_enabled': 'false',
            'allow_ldap_user_administration': 'False',
            'memcached_host': '127.0.0.1',
            'memcached_port': '11211',
            'memcached_enabled': 'true',
            'global_conf_path': '/etc/trac/project.ini',
            'archive_path': '/storage/trac/archive',
            'authentication_order': 'local',
            'authentication_providers': 'multiproject.core.auth.local_auth.LocalAuthentication',
            'show_debug_page': 'false',
            'use_alchemy_pool': 'false',
            'default_groups': 'Administrators:TRAC_ADMIN|Owners:TRAC_ADMIN|Developers:VIEW,TICKET_CREATE',
            'public_auth_group': 'Public contributors:DELETE,VERSION_CONTROL,WEBDAV,XML_RPC',
            'private_auth_group': '',
            'public_anon_group': 'Public viewers:VIEW,VERSION_CONTROL_VIEW',
            'anon_forbidden_actions': '',
            'initial_login_page': '/home',
            'expose_user_identity': 'false',
            'display_name': 'username',
            'create_public_as_default': 'false',
            'default_user_status': 'active',
            'project_requires_agreed_terms': 'True',
            'login_requires_agreed_terms': 'False',
            'max_items_shown': '200',
            'storage_warning_limit': '800000000',
            'storage_locking_limit': '1000000000',
            'generated_content_dir': '/storage/trac/results',
            'storage_usage': 'storageusage.csv',
            'trac_htdocs_location': '/htdocs/trac',
            'theme_htdocs_location': '/htdocs/theme',
            'notifications_file': 'notifications.csv',

            # TODO: Rename this to ext_profile_url
            # This parameter can be used for external user profiles.
            # Link is generated so that username is added right after this url, used in My Projects badge
            'user_profile_url': '',

            # If user avatar is in external location this configuration variable can be used. username will be added to the end.
            'external_avatar_url': '',

            'user_editable_contexts': 'Custom',
            'default_icon_id': '1',
            'anonymous_desc_string': 'Anonymous users are casual visitors that either do not have a login or have decided not to login. Anonymous users will have rights to browser, but not of any interaction.'
            ,
            'authenticated_desc_string': 'Authenticated users are those that have logged in with their credentials. By default authenticated users are allowed to contribute to a project by joining the discussion boards and opening tickets. Unless changed by the project administrators authenticated users that are not members of a project will not be allowed to perform many actions such as committing updates to the server or editing Wiki pages.'
            ,
            'hidden_contexts': 'Custom',
            'combined_contexts': 'Custom',
            'non_browsable_contexts': 'Natural language,License',
            'activity_factors': 'ticket:2|wiki:2|scm:5|attachment:1|discussion:1',
            'allow_public_projects': 'True',
            'dav_help_url': '',
            'supported_scm_systems': 'svn,git,hg',
            'gitosis_enable': 'false',
            'gitosis_repo_path': '/storage/trac/repositories/gitosis-admin.git',
            'gitosis_clone_path': '/storage/trac/gitosis_clone_tmp/',
            'cookie_lifetime': '45',
            'cookie_refresh_rate': '300',
            'service_statistics': 'False',
            'analytics_log_file_path': '/storage/trac/analytics/',
            'version_control_hooks_dir': '/storage/trac/dist/current/scripts/',
            'multirepo_separator': '.',
            # Public userprofile is disabled when having empty / no value
            'public_user_page_url': '',
            'news_forum_name': 'NEWS',
            'news_forum_subject': 'Project News',
            'news_forum_description': 'Project News',
            'show_news_forum': 'false',
            'activity_calculation_daterange': '60',
            'site_title_text': '',
            'site_name': 'Welcome',
            'use_protocol_check': 'False',
            # Set this if global timeline needs active refreshing
            'refresh_global_timeline': 'True',
            # FIXME: Remove these when home permission improvements done
            'allow_anonymous_frontpage': 'False',
            # Will be shown in the My projects page always
            'default_projects': '',
            'use_project_filtering': 'False',
            # Http proxy for outgoing connections. Used for example for reading external RSS feed.
            'http_proxy': '',
            'punch_line': '',
            # Statistics
            'statistic_scheme': 'http'
        }

        self.handle_multiproject_conf(defaults_dict.items())

    def handle_multiproject_conf(self, options):
        """ Process the configuration options for the multiproject section.
            Most of the values are simply set, but some require some processing.
        """

        # List of the simple value assignment cases
        assignment_values = [
            'sys_home_project_name', # Main (home) project name
            'sys_root', # WebDav root directory ?
            'sys_dav_root', # WebDav root directory
            'sys_projects_root', # Place where trac instances will be created
            'sys_vcs_root', # Place where repositories are created
            'url_dav_path',
            'repo_type',
            'salt',
            'db_host',
            'db_user',
            'db_password',
            'db_admin_schema_name',
            'db_analytical_schema_name',
            'db_port',
            'default_theme_path', # Path to theme. Trac default is used when None
            'ldap_connect_path', # Ldap connection path (protocol://host:port)
            'ldap_bind_user',
            'ldap_bind_password',
            'ldap_uid',
            'ldap_user_rdn', # Relative dn of users (Can be only in the simple form as below)
            'ldap_base_dn', # Ldap Base domain
            'ldap_groups_attribute_name',
            'ldap_users_attribute_name',
            'ldap_groups_dn',
            'ldap_groups_cn',
            'external_avatar_url',
            'memcached_port',
            'log_file',
            'global_conf_path',
            'domain_name',
            'archive_path',
            'initial_login_page',
            'default_user_status',
            'max_items_shown',
            'storage_warning_limit',
            'storage_locking_limit',
            'generated_content_dir',
            'storage_usage',
            'trac_htdocs_location',
            'theme_htdocs_location',
            'notifications_file',
            'user_profile_url',
            'default_icon_id',
            'anonymous_desc_string',
            'authenticated_desc_string',
            'insider_organization',
            'gitosis_repo_path',
            'gitosis_clone_path',
            'dav_help_url',
            'analytics_log_file_path',
            'version_control_hooks_dir',
            'multirepo_separator',
            'public_user_page_url',
            'default_http_scheme',
            'news_forum_name',
            'news_forum_subject',
            'news_forum_description',
            'theme_name',
            'activity_calculation_daterange',
            'site_title_text',
            'site_name',
            'punch_line']

        # Cases that have some things to do before setting the value
        # have their own functions to do so.
        calls = {'host_match': self.f_host_match,
                 'ldap_object_classes': self.f_ldap_object_classes,
                 'ldap_use_tsl': self.f_ldap_use_tsl,
                 'ldap_use_sasl': self.f_ldap_use_sasl,
                 'organizations_enabled': self.f_organizations_enabled,
                 'allow_ldap_user_administration': self.f_allow_ldap_user_administration,
                 'ldap_groups_enabled': self.f_ldap_groups_enabled,
                 'memcached_host': self.f_memcached_host,
                 'memcached_enabled': self.f_memcached_enabled,
                 'default_groups': self.f_default_groups,
                 'user_editable_contexts': self.f_user_editable_contexts,
                 'hidden_contexts': self.f_hidden_contexts,
                 'combined_contexts': self.f_combined_contexts,
                 'non_browsable_contexts': self.f_non_browsable_contexts,
                 'activity_factors': self.f_activity_factors,
                 'public_auth_group': self.f_public_auth_group,
                 'private_auth_group': self.f_private_auth_group,
                 'public_anon_group': self.f_public_anon_group,
                 'anon_forbidden_actions': self.f_anon_forbidden_actions,
                 'authentication_order': self.f_authentication_order,
                 'authentication_providers': self.f_authentication_providers,
                 'show_debug_page': self.f_show_debug_page,
                 'use_alchemy_pool': self.f_use_alchemy_pool,
                 'expose_user_identity': self.f_expose_user_identity,
                 'display_name': self.f_display_name,
                 'create_public_as_default': self.f_create_public_as_default,
                 'project_requires_agreed_terms': self.f_project_requires_agreed_terms,
                 'login_requires_agreed_terms': self.f_login_requires_agreed_terms,
                 'allow_public_projects': self.f_allow_public_projects,
                 'supported_scm_systems': self.f_supported_scm_systems,
                 'gitosis_enable': self.f_gitosis_enable,
                 'cookie_lifetime': self.f_cookie_lifetime,
                 'cookie_refresh_rate': self.f_cookie_refresh_rate,
                 'service_statistics': self.f_service_statistics,
                 'show_news_forum': self.f_show_news_forum,
                 'use_protocol_check': self.f_use_protocol_check,
                 'allow_anonymous_frontpage': self.f_allow_anonymous_frontpage,
                 'default_projects': self.f_default_projects,
                 'refresh_global_timeline': self.f_refresh_global_timeline,
                 'url_projects_path': self.f_url_projects_path,
                 'visibility_db_batch_size': self.f_visibility_db_batch_size,
                 'url_dav_path': self.f_url_dav_path,
                 'use_project_filtering': self.f_use_project_filtering,
                 'statistic_scheme': self.f_statistics_scheme,
                 'http_proxy': self.f_http_proxy}

        for opt in options:
            # First check if it's a value we just need to set
            if opt[0] in assignment_values:
                setattr(self, opt[0], opt[1].strip('"\''))
            # Otherwise check if it's something we need to handle more
            elif calls.has_key(opt[0]):
                calls[opt[0]](opt[1].strip('"\''))


    @property
    def home_env(self):
        """
        Loads and returns the Trac environment from special home project
        """
        return open_environment(env_path=os.path.join(conf.sys_projects_root, conf.sys_home_project_name), use_cache=True)

    def handle_organizations(self, organizations):
        for opt in organizations:
            organization_type, position = opt[0].split('.')
            authentication, organization = opt[1].split(',')
            self.organizations[authentication] = [position, organization_type, organization]

    def refresh(self):
        self.config_parser = ConfigParser()
        files = self.config_parser.read(Configuration.config_file)

        # If the configuration file was successfully read, we will process the configured values.
        if len(files) > 0:
            options = self.config_parser.items('multiproject')
            self.handle_multiproject_conf(options)
            try:
                organizations = self.config_parser.items('organizations')
                self.handle_organizations(organizations)
            except:
                pass
        else:
            raise Exception("Configuration file %s not found!" % Configuration.config_file)

    def start_log(self):
        """
        TO BE DEPRECATED - hopefully

        Initializes legacy api `conf.log` with trac configuration.

        In every Component context you should aways use `self.log` to log messages.
        """
        level = self.config_parser.get('logging', 'log_level')
        logtype = self.config_parser.get('logging', 'log_type')
        logfile = self.config_parser.get('logging', 'log_file')
        format = None
        try:
            format = self.config_parser.get('logging', 'log_format')
        except NoOptionError:
            pass

        # if required, verify that we have patch present
        if logtype.startswith('factory:'):
            try:
                from trac.log import FACTORY_SUPPORTED
            except ImportError:
                raise Exception('Custom Trac\'s log factory not supported - missing a patch?')

        # Note: log format cannot be supported properly since trac does these replacements
        # in Environment.setup_log
        # One more reson to avoid conf.log !

        if format is not None:
            format = format.replace('$(', '%(')\
            .replace('%(path)s', 'N/A')\
            .replace('%(basename)s', 'N/A')\
            .replace('%(project)s', 'N/A')

        self.log = logger_factory(logtype, logfile, level, 'multiproject', format)

    def f_host_match(self, value):
        # Frendly hostnames
        self.host_match = self._list(value)

    def f_default_projects(self, value):
        self.default_projects = self._list(value)

    def f_refresh_global_timeline(self, value):
        self.refresh_global_timeline = self._bool(value)

    def f_ldap_object_classes(self, value):
        # Users will be stored to be on this class (Don't change)
        self.ldap_object_classes = self._list(value)

    def f_ldap_use_tsl(self, value):
        self.ldap_use_tsl = self._bool(value)

    def f_ldap_use_sasl(self, value):
        self.ldap_use_sasl = self._bool(value)

    def f_organizations_enabled(self, value):
        self.organizations_enabled = self._bool(value)

    def f_allow_ldap_user_administration(self, value):
        self.allow_ldap_user_administration = self._bool(value)

    def f_ldap_groups_enabled(self, value):
        self.ldap_groups_enabled = self._bool(value)

    def f_memcached_host(self, value):
        self.memcached_host = self._list(value)

    def f_memcached_enabled(self, value):
        self.memcached_enabled = self._bool(value)

    def f_default_groups(self, value):
        # input is 'Administrators:TRAC_ADMIN,DISCUSSIONFORUM|Owners:TRAC_ADMIN|Developers:VIEW,TICKET_CREATE'

        del self.default_groups[:]

        groups = value.split('|')
        # -> ['Administrators:TRAC_ADMIN,DISCUSSIONFORUM','Owners:TRAC_ADMIN','Developers:VIEW,TICKET_CREATE']

        for group in groups:
            # 'Administrators:TRAC_ADMIN,DISCUSSIONFORUM'
            grpname, rights = group.split(':')
            rightslist = rights.split(',')
            self.default_groups.append((grpname, rightslist))

    def f_user_editable_contexts(self, value):
        self.user_editable_contexts = self._list(value)

    def f_hidden_contexts(self, value):
        self.hidden_contexts = self._list(value)

    def f_combined_contexts(self, value):
        self.combined_contexts = self._list(value)

    def f_non_browsable_contexts(self, value):
        self.non_browsable_contexts = self._list(value)

    def f_supported_scm_systems(self, value):
        self.supported_scm_systems = self._list(value)

    def f_activity_factors(self, value):
        # input is 'ticket=2:wiki=2:scm=5:attachment=1:discussion=1'

        self.activity_factors.clear()

        groups = value.split('|')
        # -> ['ticket:2','wiki:2','scm:5','attachment:1','discussion:1']

        for group in groups:
            # 'ticket:2'
            eventtype, factor = group.split(':')
            self.activity_factors[eventtype] = factor

    def f_public_auth_group(self, value):
        self.public_auth_group = None
        if value:
            grpname, rights = value.split(':')
            rightslist = rights.split(',')
            self.public_auth_group = (grpname, rightslist)

    def f_private_auth_group(self, value):
        self.private_auth_group = None
        if value:
            grpname, rights = value.split(':')
            rightslist = rights.split(',')
            self.private_auth_group = (grpname, rightslist)

    def f_public_anon_group(self, value):
        grpname, rights = value.split(':')
        rightslist = rights.split(',')
        self.public_anon_group = (grpname, rightslist)

    def f_anon_forbidden_actions(self, value):
        # Actions forbidden for anonymous user
        self.anon_forbidden_actions = self._list(value)

    def f_authentication_order(self, value):
        # List of used authentication methods, in preferred order
        self.authentication_order = self._list(value)

    def f_authentication_providers(self, value):
        # List of available authentication provider classes
        self.authentication_providers = self._list(value)

    def f_show_debug_page(self, value):
        self.show_debug_page = self._bool(value)

    def f_use_alchemy_pool(self, value):
        self.use_alchemy_pool = self._bool(value)

    def f_expose_user_identity(self, value):
        self.expose_user_identity = self._bool(value)

    def f_display_name(self, value):
        self.display_name = self._list(value)

    def f_create_public_as_default(self, value):
        self.create_public_as_default = self._bool(value)

    def f_project_requires_agreed_terms(self, value):
        self.project_requires_agreed_terms = self._bool(value)

    def f_login_requires_agreed_terms(self, value):
        self.login_requires_agreed_terms = self._bool(value)

    def f_allow_public_projects(self, value):
        self.allow_public_projects = self._bool(value)

    def f_gitosis_enable(self, value):
        self.gitosis_enable = self._bool(value)

    def f_service_statistics(self, value):
        self.service_statistics = self._bool(value)

    def f_use_protocol_check(self, value):
        self.use_protocol_check = self._bool(value)

    def f_allow_anonymous_frontpage(self, value):
        self.allow_anonymous_frontpage = self._bool(value)

    # Cookies
    def f_cookie_lifetime(self, value):
        #  0 forever or >1 minutes of lifetime
        self.cookie_lifetime = safe_int(value) or 0

    def f_cookie_refresh_rate(self, value):
        # >1 seconds of lifetime (default 5 min)
        self.cookie_refresh_rate = safe_int(value) or 300
        if self.cookie_refresh_rate == 0:
            self.cookie_refresh_rate = 300

    def get_activity_factor(self, eventtype):
        if self.activity_factors.has_key(eventtype):
            return self.activity_factors[eventtype]
        else:
            return 0

    def f_show_news_forum(self, value):
        self.show_news_forum = self._bool(value)

    def f_url_projects_path(self, value):
        self.url_projects_path = value.strip(" ").rstrip("/")

    def f_url_dav_path(self, value):
        self.url_dav_path = value.strip(" ").rstrip("/")

    def f_visibility_db_batch_size(self, value):
        self.visibility_db_batch_size = safe_int(value) or 5000
        if self.visibility_db_batch_size == 0:
            self.visibility_db_batch_size = 5000

    def f_use_project_filtering(self, value):
        self.use_project_filtering = self._bool(value)

    def f_http_proxy(self, value):
        self.http_proxy = value

    def f_statistics_scheme(self, value):
        self.statistics_scheme = value

    def _bool(self, value):
        if not value:
            return False
        return value.lower() != "false"

    def _list(self, value):
        return value.split(',')

    #
    # Helper functions
    #
    # FIXME: Move all helper functions away from configuration
    #

    def update_organizations(self):
        """
        Private function to update organizations from configuration file into database. This
        is allowed to be run only once on configuration object's life time and only when
        we actually have organizations in configuration file
        """
        if self._organizations_updated:
            return
        if not self.organizations_enabled:
            return
        if not self.organizations:
            return

        self._organizations_updated = OrganizationUpdater.update_to_db(self)

    def getThemePath(self):
        if len(self.theme_name) > 0:
            return self.theme_name + "/"
        else:
            return ''

    def getUserStore(self):
        """
        Returns local user store

        .. IMPORTANT:: Deprecated

            Use the ``multiproject.core.users.get_userstore()`` instead

        """
        from multiproject.core.users import MySqlUserStore

        return MySqlUserStore()

    def getAuthenticationStore(self):
        """
        Returns ldap authentication store
        If you want to use MySQL store to authentication, just return it here

        .. IMPORTANT:: Deprecated

            Use the ``multiproject.core.users.get_authstore()`` instead

        """
        from multiproject.core.users import LdapUserStore

        return LdapUserStore()

    @deprecated
    def getAdminDbConnection(self):
        """
        DEPRECATED: Use the context managers from core.db.py instead!
        """
        return get_connection(self.db_admin_schema_name)

    @deprecated
    def getAnalyticalDbConnection(self):
        """
        DEPRECATED: Use the context managers from core.db.py instead!
        """
        return get_connection(self.db_analytical_schema_name)

    @deprecated
    def getDbConnection(self, dbname=None):
        """
        Helper function for connecting into database
        DEPRECATED: Use the context managers from core.db.py instead!
        """
        return get_connection(dbname)

    def getMemcachedLocation(self):
        locations = []
        for host in self.memcached_host:
            locations.append(host + ':' + self.memcached_port)
        return locations

    def getMemcachedInstance(self):
        """
        Get memcached client
        :return: Instance of memcache client or if disabled stubclient that works similarly.
        """
        if Configuration.__memcached is None:
            # Create instance (stub if disabled)
            if self.memcached_enabled:
                try:
                    import memcache
                    Configuration.__memcached = memcache.Client(self.getMemcachedLocation(), debug=0)
                except ImportError:
                    memcache = None
                    Configuration.__memcached = MemcacheStub()
            else:
                Configuration.__memcached = MemcacheStub()
        return Configuration.__memcached

    def resolveProjectName(self, env):
        """ Helper function for resolving project name based on environment
        """
        return env.path.split('/')[-1]

    def getEnvironmentHomeConfigPath(self):
        """ Helper function for resolving main project's configuration file
            environment name
        """
        return self.sys_projects_root + '/' + self.sys_home_project_name + '/conf/trac.ini'

    def getEnvironmentConfigPath(self, envname):
        """ Helper function for resolving main project's configuration file
            environment name
        """
        return self.sys_projects_root + '/' + envname + '/conf/trac.ini'

    def getEnvironmentUrl(self, env_name):
        """ Helper function for resolving environment base url
        """
        url = self.url_projects_path + '/' + env_name
        return url

    def getEnvironmentDbPath(self, env_name):
        """ Helper function for resolving environment db connection path based
            on environment name
        """
        path = 'mysql://' + self.db_user + ':' + self.db_password
        path += '@' + self.db_host + ":" + str(self.db_port) + '/' + env_name
        return path

    def getEnvironmentVcsPath(self, env_name):
        """ Helper function for resolving environment svn path based on
            environment name
        """
        return self.sys_vcs_root + '/' + env_name

    def makeEnvironmentDownloadsPath(self, env_name):
        """ Helper function for environment download path
        """
        return self.sys_root + '/downloads/' + env_name + '/'

    def getEnvironmentDownloadsPath(self, env):
        """ Helper function for resolving environment download path
        """
        return self.sys_root + '/downloads/' + self.resolveProjectName(env) + '/'

    def getEnvironmentDownloadsUrl(self, env, id):
        """ Helper function for resolving environment download path
        """
        return self.getEnvironmentUrl(self.resolveProjectName(env)) + '/downloads/' + str(id)

    def getEnvironmentSysPath(self, env_name):
        """ Helper function for resolving environment filesystem path based on
            environment name
        """
        return self.sys_projects_root + '/' + env_name

    def getVersionControlType(self, env_name):
        """
        .. WARNING::

           Do not call this unless absolutely needed
           This will initialize new trac environment which is heavy operation to do
        """
        # TODO: whole method should be removed
        env = open_environment(conf.getEnvironmentSysPath(env_name), use_cache=True)
        return env.config.get('trac', 'repository_type')

    def getVersionControlName(self, vcs_type):
        if vcs_type == 'svn':
            return 'Subversion'
        elif vcs_type == 'git':
            return 'Git'
        elif vcs_type == 'hg':
            return 'Mercurial'
        elif vcs_type == 'perforce':
            return 'Perforce'
        elif vcs_type == 'bzr':
            return 'Bazaar'
        else:
            return 'Unknown version control system'

    def cleanupProjectName(self, pname):
        return str(pname).strip('\n\r\a\b\t\v\f\e\"\'*')

    def safe_address(self, address):
        """
        Ensures the given address points to service itself
        :returns: Address or None if address is considered dangerous

        .. IMPORTANT:: Deprecated

           Use :func:`multiproject.core.util.safe_address` instead
        """
        if address:
            if address.startswith("http://" + self.domain_name) or address.startswith("https://" + self.domain_name):
                return address
        return None

    def redirect(self, req, toaddress=None):
        """
        Redirects user to specified address

        .. IMPORTANT:: Deprecated

           Use :func:`multiproject.core.util.redirect` instead
        """
        if not req.session.has_key('goto'):
            req.session['goto'] = req.base_url + req.path_info
            req.session.save()
        if toaddress:
            req.redirect(toaddress)

    def filter_login_error(self, chrome):
        """
        Removes trac internal notice about login error.
        """
        # FIXME: Should not be placed in configuration
        if chrome.has_key('notices'):
            for notice in chrome['notices']:
                if issubclass(notice.__class__, Fragment) and notice.generate().render().startswith(
                    'You are currently not logged in. You may want to '):
                    chrome['notices'].remove(notice)
                    return True
        return False

conf = Configuration.instance()
