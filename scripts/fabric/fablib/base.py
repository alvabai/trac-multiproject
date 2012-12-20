# -*- coding: utf-8 -*-
"""
Classes, modules and functions used by other modules.
Only dependant on Fabric and itself

- StatusLoggerHandler: Custom log handler to print log entries to stdout along with the Fabric information
- Config: Custom config reader for fabric.ini

"""
from HTMLParser import HTMLParser
import shutil
import tempfile
import string
import logging
import ConfigParser, os
import glob
import fnmatch
import re
import sys
import fileinput
import tarfile

import requests
from fabric import api
from fabric.state import env


class StatusLoggerHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        logging.Handler.__init__(self, level=level)


    def handle(self, record):
        """
        Includes some Fabric related info into logging messages
        """
        host = env.host_string if env.host_string else 'localhost'

        print("[%s] %s" % (host, record.msg))


class TemplateResource(object):
    """
    Class for template files (containing placeholders) and replacing them
    with actual values in-place.

    Example usage:

    >>> tfile = file('/tmp/file.txt', 'w+b')
    >>> tfile.write('hello ${target}')
    >>> tfile.close()
    >>>
    >>> template = TemplateResource('/tmp/file.txt')
    >>> template.build(target='world')

    """
    def __init__(self, templatepath):
        """
        Initiates the template

        Parameters:
            - templatepath: Path to template resource in local filesystem

        """
        assert os.path.exists(templatepath), 'Template file %s cannot be found' % templatepath
        self.templatepath = templatepath


    def build(self, **kwargs):
        """
        Replace the template placeholders with given named parameters.
        Changes are done in file directly. The missing placeholder values are left as-is.

        Returns None
        """
        # Use fileinput module to edit in place: all the data written in stdout is written in file
        for line in fileinput.input(self.templatepath, inplace=1):
            tmpl = string.Template(line)
            line = tmpl.safe_substitute(kwargs)
            sys.stdout.write(line)


class Resource(object):
    """
    Base class for external resources

    >>> Resource('res', '')

    """
    def __init__(self, name, url):
        self.name = name
        self.url = url


    def retrieve(self, outdir, auth=()):
        """
        Downloads the resource. Subclasses should overwrite this method.
        In a case of authentication, provide it in format like

        - outdir: Directory where to place the download
        - auth: Authentication tuple. See http://docs.python-requests.org/en/latest/user/quickstart/#basic-authentication

        Returns the path to the downloaded resource

        """
        logger.info('Downloading resource from %s' % self.url)
        outfile = None

        res = requests.get(self.url, auth=auth)
        if res.status_code != 200:
            logger.error('Failed to retrieve resource from: %s' % self.url)
            return

        # Create target dir if not existing already
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        # Get file name from headers, if available. Format
        # 'content-disposition': 'inline; filename="gitosis-dedb3dc63f413ed6eeba8082b7e93ad136b16d0d.tar.gz"'
        if 'content-disposition' in res.headers:
            match = re.search(string=res.headers['content-disposition'], pattern='filename="(?P<filename>[\w|-|\d|\.]+)"')
            if match:
                logger.info('Taking resource target from headers')
                outfile = match.group['filename']

        if not outfile:
            outfile = join(outdir, os.path.basename(self.url))
            logger.debug('Generating resource target from URL: %s' % outfile)

        output = join(outdir, outfile)
        f = open(output, 'w+b')
        f.write(res.content)
        f.close()

        return output

    def __str__(self):
        return "Fabric {0}, resource id: {1}, fetched from {2}".format(
            self.__class__.__name__, self.name, self.url)


class TarResource(Resource):
    """
    Download the resource and extract it to specified folder.
    If there is a root directory in the archive (instead of multiple files in root), the
    files and folders inside the subfolder are extracted directory to output folder

    >>> res = TarResource('trac', 'http://ftp.edgewall.com/pub/trac/Trac-0.12.2.tar.gz')
    >>> res.retrieve('/tmp/folder')

    .. WARNING:: The contents of the target folder are deleted!

    """
    def retrieve(self, outdir, auth=()):
        # Download the file using Resource class
        outpath = super(TarResource, self).retrieve(outdir, auth)

        # Extract the package
        logger.debug('Extracting archived package to: %s' % outdir)

        # Support for tar.gz
        if self.url.endswith('gz'):
            archive = tarfile.open(outpath, mode='r:gz')
        else:
            archive = tarfile.open(outpath, mode='r')

        # Get the root path, if any
        self.prefix = os.path.commonprefix(archive.getnames())

        # Extract files to temp directory and copy the files from there, based on prefix
        temp_dir = tempfile.mkdtemp()
        logger.debug('Copying files from %s --> %s' % (join(temp_dir, self.prefix), outdir))
        archive.extractall(temp_dir)

        if os.path.exists(outdir):
            shutil.rmtree(outdir, ignore_errors=True)
        shutil.copytree(join(temp_dir, self.prefix), outdir)
        shutil.rmtree(temp_dir, ignore_errors=True)

        return outpath


class SVNResource(Resource):
    """
    Retrieve SVN resource using svn command, expected to found in $PATH

    .. WARNING:: The contents of the target folder are deleted!

    """
    def retrieve(self, outdir, auth=()):
        """
        Downloads the resource. Subclasses should overwrite this method.
        In a case of authentication, provide it in format like

        - outdir: Path where to place the download
        - auth: Authentication tuple. See http://docs.python-requests.org/en/latest/user/quickstart/#basic-authentication

        """
        # Extract files to temp directory and copy the files from there, based on prefix
        temp_dir = tempfile.mkdtemp()
        cmd = 'svn co -q %s %s' % (self.url, temp_dir)
        if auth:
            cmd = 'svn co -q --username %s --password %s %s %s' % (auth[0], auth[1], self.url, temp_dir)

        if os.path.isfile(outdir):
            logger.error('Given target %s is a file while directory is required. Giving up.' % outdir)
            return

        if not os.path.exists(outdir):
            os.makedirs(outdir)

        logger.debug('Checking out the SVN repository %s to %s' % (self.url, temp_dir))
        api.local(cmd)

        if os.path.exists(outdir):
            shutil.rmtree(outdir, ignore_errors=True)
        shutil.copytree(temp_dir, outdir)
        shutil.rmtree(temp_dir, ignore_errors=True)


class GitResource(Resource):
    """
    Retrieve Git resource using git command, expected to found in $PATH
    """
    def retrieve(self, output, auth=()):
        """
        Downloads the resource. Subclasses should overwrite this method.
        In a case of authentication, provide it in format like

        - output: Path where to place the download
        - auth: Not supported atm.

        """
        temp_dir = tempfile.mkdtemp()
        cmd = 'git clone -q %s %s' % (self.url, temp_dir)
        if auth:
            logger.warning('Authentication is not supported - trying to clone repository without')

        if os.path.isfile(output):
            logger.error('Given target is a file while directory is required. Giving up.')
            return

        if not os.path.exists(output):
            os.makedirs(output)

        logger.debug('Checking out the Git repository %s to %s' % (self.url, temp_dir))
        api.local(cmd)

        if os.path.exists(output):
            shutil.rmtree(output, ignore_errors=True)
        shutil.copytree(temp_dir, output)
        shutil.rmtree(temp_dir, ignore_errors=True)


class Config(object):
    """
    Configuration reader class. Singleton.
    """
    _instance = None
    config = None

    def __new__(cls, config_paths):

        if not cls._instance:
            config_paths = [os.path.expandvars(os.path.expanduser(cpath)) for cpath in config_paths]

            cls._instance = super(Config, cls).__new__(cls, config_paths)
            cls._instance.config = ConfigParser.ConfigParser(defaults=Config.get_defaults())
            found_paths = cls._instance.config.read(config_paths)

            if found_paths:
                logger.info('Reading configuration from: %s' % ', '.join(found_paths))
            else:
                logger.warn('No config files were found. Using defaults only')

        return cls._instance


    def __init__(self, config_paths):
        pass


    def __getitem__(self, item):
        """
        Returns value of configuration key
        based on current host or global section

        For example, if current task is connected to 10.12.43.2
        and it can be found from config::

            [DEFAULT]
            mykey = 'defaultval'

            [setup:testenv]
            fe_hosts = 10.12.43.2
            db_hosts = 10.12.43.2
            mc_hosts = 10.12.43.2
            mykey = 'myvalue'

        Then:

        >>> config = Config()
        >>> config['mykey']
        'myvalue'

        """
        # Default section where to read
        section = 'DEFAULT'

        # Try to determine the section based on current host name
        host_string = env.get('host_string', '')
        if host_string:

            default = {}

            # Iterate roledefs and match hostname with them
            for rolename, hosts in env.get('roledefs', default).items():
                # Skip the layer specific roles
                if rolename[-2:] in ['fe', 'db', 'mc']:
                    pass
                elif host_string in hosts:
                    section = 'setup:%s' % rolename

        # Check if option can be found and fallback to 'DEFAULT'
        if not self.config.has_option(section, item):
            logger.debug('Option cannot be found: %s, falling back' % item)
            section = 'DEFAULT'

        value = self.config.get(section, item)
        logger.debug('Reading config [%s] %s = %s' % (section, item, value))

        return value


    def get(self, key):
        """
        Returns the configuration value based on requested key
        If key cannot be found, configuration returns default defined in :func:`get_defaults`
        """
        return self[key]


    def get_setups_sections(self):
        """
        Returns list of setups defined in configuration file.
        Each setup is defined as a own ini section, starting with name "setup:"

        Example::

            [setup:name]
            foo = bar

        """
        return [sect for sect in self.config.sections() if sect.startswith('setup:')]


    def set_roles(self, env):
        """
        Applies/generates roledefs based on config::

            [setup:dnc-qa]
            fe_hosts = dnc-qa-fe1, dnc-qa-fe2
            mc_hosts = dnc-qa-mc1, dnc-qa-mc2
            db_hosts = dnc-qa-db

        Updated roledef::

            env.roledefs = {
                'dnc-qa-fe': ['dnc-qa-fe1', 'dnc-qa-fe2'],
                'dnc-qa-mc': ['dnc-qa-mc1', 'dnc-qa-mc2'],
                'dnc-qa-db': ['dnc-qa-db']
            }

        """
        for setupsect_name in self.get_setups_sections():
            setup_hosts = []

            # Add also roles per layer
            for layer in ['fe', 'mc', 'db']:
                # Create rolename based on section name and layer
                rolename = '%s-%s' % (setupsect_name.replace('setup:', ''), layer)
                # Read configuration value and convert it to list
                hosts = [host.strip() for host in self.config.get(setupsect_name, '%s_hosts' % layer).split(',')]
                # Update role definition
                env.roledefs.update({rolename: hosts})
                # Add also to all_host
                setup_hosts += hosts

            # Create one host to have all hosts. Use set to make remove duplicates
            env.roledefs.update({setupsect_name.replace('setup:', ''): list(set(setup_hosts))})


    def get_item(self, section='global'):
        """
        Returns the value
        """
        #return self.config.item()
        pass


    @classmethod
    def get_defaults(cls):
        """
        Returns the default configuration keys/values
        """
        return {
            'sudo_password_path': '',
            'webserver_user': 'www-data',
            'webserver_group': 'www-data',
            'domain_name': 'localhost',
            'sys_logs_path': '/var/log/trac',
            'sys_conf_path': '/etc/trac',
            'trac_root': '/var/www/trac',
            'trac_logs_path': '/var/www/trac/logs',
            'trac_conf_path': '/var/www/trac/config',
            'trac_htdocs': '/var/www/trac/trac-htdocs',
            'trac_theme_root': '/var/www/trac/themes',
            'trac_theme_path': '/var/www/trac/themes/default',
            'trac_theme_htdocs': '/var/www/trac/themes/default/htdocs',
            'trac_theme_images': '/var/www/trac/themes/default/htdocs/images',
            'trac_projects_path': '/var/www/trac/projects',
            'trac_webdav_path': '/var/www/trac/webdav',
            'trac_repositories_path': '/var/www/trac/repositories',
            'trac_project_archives_path': '/var/www/trac/archives',
            'gen_content_path': '/var/www/trac/results',
            'analytics_log_path': '/var/www/trac/analytics',
            'python_path': 'main_interpreter',
            'git_core_path': '/usr/lib/git-core',
            'git_bin_path': '/usr/bin/git',
            'hgweb_path': '/var/www/hgweb',
            'db_user': 'trac',
            'db_password': 'DBPASSWORD',
            'db_host': 'localhost',
            'fe_hosts': '',
            'db_hosts': '',
            'mc_hosts': '',
            'tmp_dir': '/tmp',
            'log_level': 'info',
            'ext_path_template': 'ext/plugins/{ext_name}',
        }

class HTMLResourceParser(HTMLParser):
    """
    Simple parser for finding the CSS and JS links from
    HTML files

    >>> hrp = HTMLResourceParser()
    >>> hrp.feed('<html><link ref="stylesheet" href="foo.css" /><script type="text/javascript" src="foo.js" /></html>')
    >>> hrp.get_styles()
    [{'href':'foo.css', 'rel':'stylesheet'}]
    >>> hrp.get_scripts()
    [{'src':'foo.js', 'type':'text/javascript'}]

    """
    def __init__(self, *args, **kwargs):
        # NOTE: HTMLParser parent id old style class, cannot use super
        HTMLParser.__init__(self)

        self._styles = []
        self._scripts = []

    @property
    def styles(self):
        """
        :returns: List of styles
        """
        if not self._styles:
            logger.warning('No styles found - have you feed the parser yet?')
        return self._styles

    @property
    def scripts(self):
        """
        :returns: List of styles
        """
        if not self._scripts:
            logger.warning('No scripts found - have you feed the parser yet?')
        return self._scripts

    def handle_starttag(self, tag, attrs):
        """
        Collect the relevant tags
        """
        # Collect javascripts with separate resource
        if tag == 'script':
            attrd = dict(attrs)
            if attrd.get('src'):
                self._scripts.append(attrd)

        # Collect stylesheets (based on rel info)
        if tag == 'link':
            attrd = dict(attrs)
            if attrd.get('rel', '') == 'stylesheet':
                self._styles.append(attrd)


def annotate_from_sshconfig(env):
    """
    Adds support for reading the host names, users and ports from ~/ssh/config

    Replaces the hosts defined in ssh config with actual host names, so that Fabric
    can take the advantage from it

    .. IMPORTANT:: This does not support /etc/ssh/ssh_config yet!

    """
    from os.path import expanduser
    from paramiko.config import SSHConfig

    def hostinfo(host, config):
        hive = config.lookup(host)
        if 'hostname' in hive:
            host = hive['hostname']
        if 'user' in hive:
            host = '%s@%s' % (hive['user'], host)
        if 'port' in hive:
            host = '%s:%s' % (host, hive['port'])
        return host

    # Look for user config, if found, parse it and update roledefs. Otherwise just ignore it (it is not required at all)
    try:
        config_file = file(expanduser('~/.ssh/config'))
    except IOError:
        pass
    else:
        config = SSHConfig()
        config.parse(config_file)
        keys = [config.lookup(host).get('identityfile', None)
            for host in api.env.hosts]
        env.key_filename = [expanduser(key) for key in keys if key is not None]
        env.hosts = [hostinfo(host, config) for host in env.hosts]

        for role, rolehosts in env.roledefs.items():
            env.roledefs[role] = [hostinfo(host, config) for host in rolehosts]


def get_files(dirname, pattern, recursive=False):
    """
    Iterates all the files matching with the glob pattern.

    .. NOTE::

        You can define multiple patterns separated with comma: "*.txt, *.conf"

    If recursive is set False, only the directory defined with dirname
    is searched.

    Example usage::

    >>> for jspath in get_files('themes', '*.js', recursive=True):
    >>>   print jspath
    >>> for txtfile in get_files('themes/nokia', '*.txt'):
    >>>   print txtfile
    >>> for config in get_files('/etc', '*.conf,*.ini'):
    >>>   print config

    """
    dirname = rel_join(dirname)

    # Walk the filesystem recursively
    if recursive:
        for root, dirs, files in os.walk(dirname):
            for filename in files:
                for pat in pattern.split(','):
                    if fnmatch.fnmatch(filename, pat.strip()):
                        yield os.path.join(root, filename)

    # Just match the pattern within dirname -directory
    else:
        for pat in pattern.split(','):
            for filename in glob.glob(os.path.join(dirname, pat.strip())):
                yield filename


def set_version_in_file(version_path, new_version=None):
    """
    Increments/replaces the version information found in given file.
    This file can be either setup.py or any other file containing following string (or similar)::

        version = "1.2.54-dev"
        version = 1.2

    This version information gets reset / incremented by one, based on arguments:

    - If new_version is given, it is used
    - If new_version is not given, the version in setup.py is incremented by one

    Input (found in setup.py):

        setup(
            name = 'mymodule',
            version = '3.0.0.12-dev'
        )

    Output (replaced in setup.py)::

        setup(
            name = 'mymodule',
            version = '3.0.0.13-dev'
        )

    Returns the new version number
    """
    # Regular expression to match with version information (like: 1.0.2-dev) in setup.py
    search_rexp = re.compile("version\s*=\s*'?(?P<version>[\d|\.]+)(?P<prefix>[\w|\d|\.|-]*)'?")

    # Use fileinput module to edit in place: all the data written in stdout is written in file
    for line in fileinput.input(version_path, inplace=1):
        match = search_rexp.search(line)
        if match:
            # Increment last digit of the numeric version
            version = match.group('version')
            # Get new version number if not given
            if not new_version:
                new_version = get_inc_version(version)

            line = line.replace(version, new_version)
        sys.stdout.write(line)

    return new_version


def get_inc_version(versionstr):
    """
    Increments the last digit of version string like '1.0.0'

    >>> _increment_version('1.0.0')
    '1.0.1'
    >>> _increment_version('1.3.0.1')
    '1.3.0.2'
    """
    parts = versionstr.split('.')
    parts[-1] = str(int(parts[-1])+1)
    return '.'.join(parts)


def get_bool_str(boolstr):
    """
    Returns boolean value based on given string
    """
    if boolstr.lower() in ('yes', 'true', '1', 'on'):
        return True
    return False


def split_package_name(packagename):
    """
    Splits the given package name into name and version

    >>> split_package_name('TracGit-0.12.0.2dev_r7757-py2.6.egg')
    ('TracGit', '0.12.0.2dev_r7757-py2.6', 'egg')
    >>> split_package_name('TracXMLRPC-1.1.0_r8688-py2.6', 'egg')
    ('TracXMLRPC', '1.1.0_r8688-py2.6', 'egg')
    >>> split_package_name('mypackage-name-1.1.0.tar.gz')
    ('mypackage-name', '1.1.0', 'tar.gz')

    Returns a tuple containing: (name, version, extension)

    """
    regx = re.compile('(?P<name>[\w|-]+)-(?P<version>\d.*$)')
    match = regx.search(packagename)

    # Figure out the extension (without leading dot)
    extension = os.path.splitext(packagename)[1]
    extension = extension[1:] if extension.startswith('.') else extension
    if packagename.endswith('tar.gz'):
        extension = 'tar.gz'

    # If regexp does not match, return packagename without version info
    if not match:
        return packagename, '', extension

    # Take the extension from the version info
    version = match.group('version')
    version = version.replace('.%s' % version, '')

    # Does the package name have extension after all? If extension seems numeric, revert action
    if extension.isdigit():
        version = match.group()
        extension = ''

    return match.group('name'), version, extension


def get_ext_path(ext_name):
    ext_path_template = config.get('ext_path_template')
    try:
        # Raise exception if {ext_name} was not found
        ext_path_template.index('{ext_name}')
        return rel_join(ext_path_template.format(ext_name=ext_name))
    except ValueError:
        # We assume that the template is the root of the ext dir
        return rel_join(ext_path_template, ext_name)


# Define handy and required global parameters
join = lambda *path: os.path.normpath(os.path.join(*path))

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = join(THIS_DIR, '../../../')
DIST_DIR = join(PROJECT_DIR, 'dist')
BUILD_DIR = join(PROJECT_DIR, 'build')
SRC_DIRS = [
    'etc',
    'plugins',
    'themes',
    'libs',
]
PLUGIN_DIRS = ['plugins/multiproject']
EXT_PLUGIN_DIRS = ['plugins/multiproject']
PKG_NAME = 'multiproject'

# Path helpers
rel_join = lambda *path: join(PROJECT_DIR, *path)
build_join = lambda *path: join(BUILD_DIR, *path)
dist_join = lambda *path: join(DIST_DIR, *path)


# Initiate logger with initial settings
logger = logging.getLogger('fabric')
logger.handlers = []
logger.addHandler(StatusLoggerHandler())
logger.setLevel(logging.INFO)

# Initiate config reader and change the log level
config_paths=['$FABFILEINI', '~/.fabfile.ini', '/etc/fabfile.ini', 'fabfile.ini']
config = Config(config_paths)
loglevel = config.get('log_level').upper()
logger.setLevel(getattr(logging, loglevel))


