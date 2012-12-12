# -*- coding: utf-8 -*-
"""
This module contains the fabric tasks for distributing the package/release
"""
from datetime import datetime
import os
import io
import shutil
from glob import glob

from fabric.api import task, cd, local, lcd, settings, show, hide
import re

from fablib.api import PROJECT_DIR, BUILD_DIR, PLUGIN_DIRS, DIST_DIR, PKG_NAME, SRC_DIRS
from fablib.api import build_join, dist_join, get_files, get_bool_str, set_version_in_file, join, rel_join
from fablib.api import TarResource, SVNResource, GitResource, TemplateResource, HTMLResourceParser
from fablib.api import exists, run, sudo, put, abort, logger, config, split_package_name
from fablib.utils import Apache


@task
def clean():
    """
    Clean up the generated files and temp dirs
    """
    # Clean dist dir
    shutil.rmtree(DIST_DIR, ignore_errors=True)

    # Clean build dir
    shutil.rmtree(BUILD_DIR, ignore_errors=True)
    for plugin_dir in PLUGIN_DIRS:
        shutil.rmtree(os.path.join(PROJECT_DIR, plugin_dir, 'dist'), ignore_errors=True)


@task
def build(release='false', compress='false', docs='', pkgs='tar', version='', ext='false'):
    """
    Create distributable packages. Builds eggs and tar.gz compressed packages, based on
    parameters. Also capable of downloading and patching external dependencies.

    :param release:
        Make release build or not. Release sets/increments the version number. Default 'false'
    :param compress:
        Compress js/css files nor not. Default 'false'
    :param docs:
        Names of the documentation targets to build. Default '' means no doc building
    :param pkgs:
        Package formats to build sources into, separated with space. Valid values: tar deb rpm
    :param version:
        Version number to set for whole package. Default '' -> take the version from VERSION.txt
        (or default to 1.0.0)
    :param ext:
        Build and include external modules into big package. Default is 'false'

    Examples::

        fab dist.build
        fab dist.build:release=true,docs=html
        fab dist.build:compress=true,version=1.2.3,pkgs="deb tar rpm"

    .. NOTE:: Python modules get their version number from setup.py

    """
    # NOTE: Fabric parameters are always in string format

    # Get the list of package formats (space delimeter)
    pkg_formats = pkgs.split(' ')

    # Determine the version: parameter vs. VERSION.txt vs. default
    if not version:
        version_path = os.path.join(PROJECT_DIR, 'VERSION.txt')
        if os.path.exists(version_path):
            version = set_version_in_file(version_path, version)
        else:
            version = '1.0.0'

    # Create package name from pkg name and version
    package_name = '%s-%s' % (PKG_NAME, version)
    pkg_join = lambda *path: join(BUILD_DIR, package_name, *path)

    logger.info('Preparing build env...')

    # Copy relevant files to build dir (so that they can be edited directly)
    shutil.rmtree(BUILD_DIR, ignore_errors=True)
    del SRC_DIRS[SRC_DIRS.index('libs')]
    del SRC_DIRS[SRC_DIRS.index('etc')]
    for src_dir in SRC_DIRS:
        shutil.copytree(src_dir, pkg_join(src_dir))

    if not os.path.exists(DIST_DIR):
        os.makedirs(DIST_DIR)

    # Copy additional files
    shutil.copy('README.rst', pkg_join('README'))
    os.makedirs(pkg_join('scripts'))
    shutil.copy(rel_join('scripts/deploy.sh'), pkg_join('scripts/deploy.sh'))
    shutil.copy(rel_join('scripts/update.py'), pkg_join('scripts/update.py'))
    shutil.copytree(rel_join('scripts/hooks'), pkg_join('scripts/hooks'))
    shutil.copytree(rel_join('scripts/cron'), pkg_join('scripts/cron'))

    # Build documentation
    if docs:
        # List the target formats/builders
        builddoc(docs, pkg_join('docs'))
    else:
        # Ensure there is at least empty directory (for archive)
        os.makedirs(pkg_join('docs'))

    # Build configuration
    buildetc(outdir=pkg_join('etc'), section='DEFAULT')

    # Increment version of each plugin if making a release
    if get_bool_str(release):
        logger.info('Setting/incrementing version numbers...')
        for setuppy_path in get_files(pkg_join('plugins'), 'setup.py', recursive=True):
            # Check if plugin folder contains VERSION.txt (non-versioned file)
            version_path = os.path.join(os.path.dirname(setuppy_path), 'VERSION.txt')
            if not os.path.exists(version_path):
                logger.warning('VERSION.txt missing, using version found in setup.py')
                version_path = setuppy_path

            # Set version information in file.
            # NOTE: If version is empty, it is determined from version file (either VERSION.txt or setup.py)
            set_version_in_file(version_path, version)

    # Optional compress (edits copied files under build)
    if get_bool_str(compress):
        logger.info('Compressing files...')

        with settings(warn_only=True):
            # Compress theme resources
            for respath in get_files(pkg_join('themes'), '*.css', recursive=True):
                local('yui-compressor --charset utf-8 -o %s %s' % (respath, respath))
            for respath in get_files(pkg_join('themes'), '*.js', recursive=True):
                local('yui-compressor --charset utf-8 -o %s %s' % (respath, respath))

            # Compress plugin resources
            for respath in get_files(pkg_join('plugins'), '*.css', recursive=True):
                local('yui-compressor --charset utf-8 -o %s %s' % (respath, respath))
            for respath in get_files(pkg_join('plugins'), '*.js', recursive=True):
                local('yui-compressor --charset utf-8 -o %s %s' % (respath, respath))

        # Aggregate js+css resources into bundle
        for template_path in get_files(pkg_join('themes'), 'resources.html', recursive=True):
            logger.info('Template path: %s' % template_path)
            bundle(template_path, pkg_join('themes/default/htdocs'))

        logger.info('Compression completed.')

    # Build eggs and source packages (in build dir)
    logger.info('Laying eggs and source packages...')
    with lcd(pkg_join()):
        for plugin_dir in PLUGIN_DIRS:
            with lcd(plugin_dir):
                local('python setup.py bdist_egg')
                local('python setup.py sdist')

    # Optionally build external modules as well
    # Retrieve and build external modules and copy the artifacts into plugins
    # NOTE: Next egg copying will put them into correct place, no need to rerun the file copy
    if get_bool_str(ext):
        buildext()
        for egg in get_files(build_join('ext'), '*.egg', recursive=True):
            shutil.copy(egg, pkg_join('plugins', os.path.basename(egg)))

    # Copy eggs and sdisted files from plugins directory to dist and plugin directories
    for egg in get_files(pkg_join('plugins/multiproject'), '*.egg', recursive=True):
        shutil.copy(egg, dist_join(os.path.basename(egg)))
        shutil.copy(egg, pkg_join('plugins'))

    for targz in get_files(pkg_join('plugins'), '*.tar.gz', recursive=True):
        shutil.copy(targz, dist_join(os.path.basename(targz)))

    # Create dist if not available
    if not os.path.exists(DIST_DIR):
        os.makedirs(DIST_DIR)

    # Create one big package to contain 'em all
    if 'tar.gz' in pkg_formats or 'tar' in pkg_formats:
        logger.info('Creating complete .tar.gz package...')
        # TODO: Archive could be implemented in pure python
        # TODO: These patterns seem to assume build dir == project dir
        exclude_patterns = [
            '.*', 'tests', 'documents', '*.egg-info', 'ext/libs', 'ext/plugins',
            'sample', 'build', 'plugins/multiproject'
        ]
        exclude_param = ' '.join(['--exclude=%s' % pt for pt in exclude_patterns])
        with lcd(BUILD_DIR):
            local('tar -czf %s.tar.gz --exclude-vcs %s %s' %
                (dist_join(package_name), exclude_param, package_name))

    # Debian package
    if 'deb' in pkg_formats:
        logger.info('Creating .deb package...')
        try:
            from stdeb import command
        except ImportError:
            command = None
            abort('Module stddep (http://pypi.python.org/pypi/stdeb) was not found, cannot build .deb package')

        # Run setup.py bdist_deb inside each plugin. It generates deb_dist/<pkgname>/ directory
        for setuppy_path in get_files(os.path.abspath(pkg_join('plugins')), 'setup.py', recursive=True):
            plugin_dir = os.path.dirname(setuppy_path)

            with settings(hide('stdout', 'stderr')):
                with lcd(plugin_dir):
                    local('python setup.py --command-packages=stdeb.command bdist_deb')

                # Package command needs to be run inside the generated folder. Find it and run the command
                for debdist_path in get_files(os.path.join(plugin_dir, 'deb_dist'), 'setup.py', recursive=True):
                    with lcd(os.path.dirname(debdist_path)):
                        local('dpkg-buildpackage -rfakeroot -uc -us')

        # Copy .deb packages to dist
        for deb_path in get_files(pkg_join('plugins'), '*.deb', recursive=True):
            shutil.copy(deb_path, dist_join(os.path.basename(deb_path)))

    # Redhat package
    if 'rpm' in pkg_formats:
        logger.info('Creating .rpm package...')

        with settings(hide('stdout', 'running')):
            # Run setup.py bdist_rpm inside each plugin. It generates deb_dist/<pkgname>/ directory
            for setuppy_path in get_files(os.path.abspath(pkg_join('plugins')), 'setup.py', recursive=True):
                plugin_dir = os.path.dirname(setuppy_path)
                with lcd(plugin_dir):
                    local('python setup.py bdist_rpm')

            # Copy .rpm packages to dist
            for rpm_path in get_files(pkg_join('plugins'), '*.rpm', recursive=True):
                shutil.copy(rpm_path, dist_join(os.path.basename(rpm_path)))

    logger.info('Building completed.')


@task
def buildext(patch='true'):
    """
    Build and optionally patch the 3rd party modules and libraries.
    The outcome (tar.gz/egg) files are placed in dist directory

    .. NOTE::

        If you want to include the external release into multiproject-all package, run the build
        task with parameters::

            fab dist.build:ext=true

    """
    ext_resources = [
        TarResource('trac', 'http://ftp.edgewall.com/pub/trac/Trac-0.12.4.tar.gz'),
        TarResource('trac-mastertickets',
            'https://github.com/coderanger/trac-mastertickets/tarball/af6c1df92629a7dd9cc8cfeb21d0aeef6bb013a3'),
        TarResource('gitosis', 'https://github.com/tv42/gitosis/tarball/dedb3dc63f413ed6eeba8082b7e93ad136b16d0d'),
        TarResource('trac-git', 'https://github.com/hvr/trac-git-plugin/tarball/master'),
        SVNResource('trac-genshi', 'http://svn.edgewall.org/repos/genshi/branches/stable/0.6.x -r 1135'),
        SVNResource('trac-mercurial', 'http://svn.edgewall.com/repos/trac/plugins/0.12/mercurial-plugin -r 10108'),
        SVNResource('trac-xmlrpc', 'http://trac-hacks.org/svn/xmlrpcplugin/trunk -r 8869'),
        SVNResource('trac-customfieldadmin', 'http://trac-hacks.org/svn/customfieldadminplugin/0.11 -r 11265'),
        GitResource('batchmodify', 'https://projects.developer.nokia.com/git/batchmodify'),
        GitResource('childtickets', 'https://projects.developer.nokia.com/git/childtickets'),
        GitResource('tracdownloads', 'https://projects.developer.nokia.com/git/tracdownloads'),
        GitResource('tracdiscussion', 'https://projects.developer.nokia.com/git/tracdiscussion'),
    ]

    # Construct and create building directory for external resources
    extbuild = build_join('ext')
    shutil.rmtree(extbuild, ignore_errors=True)
    os.makedirs(extbuild)

    # Work in build directory
    with lcd(extbuild):
        # Retreive resource and place them to build directory
        for res in ext_resources:
            res.retrieve(join(extbuild, res.name))

        # Apply patches
        if get_bool_str(patch):

            # Patch Trac
            logger.info('Patching Trac...')
            with lcd(join(extbuild, 'trac')):
                for patch in get_files(join(PROJECT_DIR, 'ext/patches/trac'), '*.patch', recursive=True):
                    local('patch --ignore-whitespace -p0 -i %s' % patch)

            # Patch Gitosis
            logger.info('Patching Gitosis...')
            with lcd(join(extbuild, 'gitosis')):
                for patch in get_files(join(PROJECT_DIR, 'ext/patches/gitosis'), '*.patch', recursive=True):
                    local('patch --ignore-whitespace -p0 -i %s' % patch)

    # Build eggs (in build dir)
    logger.info('Laying eggs and source dists...')
    # Iterate folders where setup.py can be found
    for setuppy_path in get_files(os.path.abspath(extbuild), 'setup.py', recursive=True):
        plugin_dir = os.path.dirname(setuppy_path)
        logger.info('Building package for %s' % os.path.basename(plugin_dir))
        with lcd(plugin_dir):
            local('python setup.py bdist_egg')
            local('python setup.py sdist')

    # Copy distributable files to dist
    if not os.path.exists(DIST_DIR):
        os.makedirs(DIST_DIR)

    for egg in get_files(os.path.abspath(extbuild), '*.egg', recursive=True):
        shutil.copy(egg, join(DIST_DIR, os.path.basename(egg)))

    for targz in get_files(os.path.abspath(extbuild), '*.tar.gz', recursive=True):
        shutil.copy(targz, join(DIST_DIR, os.path.basename(targz)))


@task
def buildetc(outdir=None, section=None):
    """
    Builds the configuration file based given configuration values in ``fabfile.ini``.

    Parameters:
        - outdir: Option path to directory where the built configuration files are placed. Subdirectory is created
          for each section.
        - section: Optional section name, if you want to build only one section. In this case, no subdirectory is created.

    """
    # Copy configuration files under build dir where they can be processed; config.config is a ConfigParser
    # object. config is a global object imported via fablib.api
    sections = [section] if section else config.get_setups_sections()

    # Iterate all sections unless the specific name is given
    for csection in sections:
        dest = csection.replace('setup:', '')

        # Set the target directory based on given parameters
        if section:
            build_etc = outdir
        elif outdir:
            build_etc = build_join(outdir, dest)
        else:
            build_etc = build_join('etc', dest)

        logger.info('Target directory for configuration files: %s' % build_etc)

        # Create target dir if needed
        if not os.path.exists(build_etc):
            os.makedirs(build_etc)

        # Copy the config files from etc/templates, place them in build/etc/<section> and replace the placeholders
        etc_src = rel_join('etc/templates')
        for configfile in get_files(etc_src, pattern='*.ini, *.conf, *.sql, *.sh, multiproject', recursive=True):
            # Copy the configuration file into build_etc directory, using the same directory structure
            configcopy = build_join(build_etc, configfile.replace(etc_src, './'))
            configcopy_dir = os.path.dirname(configcopy)
            if not os.path.exists(configcopy_dir):
                os.makedirs(configcopy_dir)
            shutil.copy(configfile, configcopy)

            # Replace placeholder in configfile
            logger.info('Building configuration file: %s' % configcopy)
            template = TemplateResource(configcopy)
            template.build(**dict(config.config.items(csection)))


@task
def upload(package, rdir=''):
    """
    Uploads the given package to remote host

    :param str package: Path to package, absolute or relative
    :param str rdir: Remote directory where to upload the package. Defaults to users home directory

    Examples::

        fab dist.upload:package.tar.gz,/tmp
        fab dist.upload:package=../../package.tar.gz
        fab dist.upload:package=../../packa*.tar.gz
        fab dist.upload:package=../../package.tar.gz,rdir=/tmp

    .. NOTE::

        Special paths, containing environment variables or tilde characters are not supported.

    """
    # Use glob to find package from local filesystem (glob supports wildcards)
    pmatches = glob(os.path.expandvars(os.path.expanduser(package)))
    if not pmatches:
        return abort('No package can be found with name: %s' % package)

    # Upload package(s) to remote host and determine the name of release folder
    for pmatch in pmatches:
        package = os.path.normpath(pmatch)

        # Get the release name from package: drop the extension and version
        packagename = os.path.basename(package)
        target_path = join(rdir, packagename)  if rdir else packagename
        target_dir = os.path.dirname(target_path)

        # Upload package to specified directory, with the same name as the orig
        logger.info('Uploading the package: %s -> %s' % (package, target_path))

        if not exists(target_dir):
            run(target_dir)

        put(package, target_path)


@task
def deploy(package, opts=''):
    """
    Uploads the given package to remote host and deploys it there.

    :param str package:
        Path to tar.gz package in local file system. In case of wildcard, all the matched package are deployed.
        Package can be in formats: tar.gz (custom package structure, deb, rpm
    :param str opts:
        Optional parameters to pass to deploying app (easy_install, rpm, dpkg, deploy.sh)

    Examples::

        fab dist.deploy:package=../../package.tar.gz
        fab dist.deploy:package=../../package.tar.gz,opts="--theme --activate"
        fab dist.deploy:package=../../*.deb
        fab dist.deploy:package=../../*.deb,opts='--force'

    """
    # Use glob to find package from local filesystem (glob supports wildcards)
    pmatches = glob(os.path.expandvars(os.path.expanduser(package)))
    if not pmatches:
        return abort('No package can be found with name: %s' % package)

    # Iterate matched packages
    # Upload package(s) to remote host and determine the name of release folder
    for pmatch in pmatches:
        package = os.path.normpath(pmatch)

        # Get the release name from package: drop the extension and version
        packagename = os.path.basename(package)
        releasename, releaseversion, releaseextension = split_package_name(packagename)

        # Upload package to home directory, with same as the orig
        logger.info('Uploading the package: %s -> %s' % (package, packagename))
        put(package, packagename)

        logger.info('Release name: %s' % releasename)

        # Run the package specific deployment actions
        if releaseextension == 'tar.gz':
            deploy_targz(packagename, opts)
        elif releaseextension == 'egg':
            opts = opts or '-Z'
            sudo('easy_install %s %s' % (opts, packagename))
        elif releaseextension == 'deb':
            opts = opts or '--install'
            sudo('dpkg %s %s' % (opts, packagename))
        elif releaseextension == 'rpm':
            opts = opts or '-Uvh'
            sudo('rpm %s %s' % (opts, packagename))

        # Remove the package
        with cd('~'):
            sudo('rm -f ./%s' % packagename)

    # Restart apache
    logger.info('Restarting apache')
    apache = Apache()
    apache.restart()


def deploy_targz(packagename, opts):
    """
    Run the deploy activities for source/custom tar.gz package.
    The script can deploy following kind of tar.gz packages:

    - Python source package: if setup.py is found from root folder, it is run with python setup.py install
    - Custom source package (created with build task): runs scripts/deploy.sh found from the package

    :param str packagename: Name of the package to deploy. Example 'mypackage-1.1.0.tar.gz'
    :param str opts: Optional parameters to pass to deploying app (easy_install, rpm, dpkg, deploy.sh)

    """
    root_dir = config['trac_root']
    webserver_user = config['webserver_user']
    webserver_group = config['webserver_group']
    releasename, releaseversion, releaseextension = split_package_name(packagename)

    # Get the subdirectory (where all the files are place) of the archive, if any
    out = run('tar ztf %s' % packagename)
    subdir = os.path.commonprefix(out.stdout.splitlines())

    run('tar zxf %s' % packagename)

    with cd('~/%s' % subdir):
        # Run the setup.py if is found
        if exists('setup.py'):
            logger.info('Installing python module from source, using: %s/setup.py' % releasename)
            sudo('python setup.py install %s' % opts)

        # Custom package, expect to find scripts/deploy.sh
        else:
            logger.info('Running deploy script ./scripts/deploy.sh at directory: %s' % subdir)
            with settings(show('stdout')):
                sudo('./scripts/deploy.sh %s' % opts)

            # Fix file permissions
            logger.info('Setting the permissions to deployment folder')
            sudo('chown -L -R %s:%s %s' % (webserver_user, webserver_group, join(root_dir, 'dist', 'current')))

    # Cleanup - needs to be done with sudo because of sudo is being used at running deploy.sh (at the moment)
    with cd('~'):
        logger.info('Cleaning up...')
        if subdir:
            sudo('rm -rf ./%s' % subdir)
        sudo('rm -rf ./%s' % releasename)


@task
def builddoc(builders='', rootdir=None, sphinxopts='', apidoc='false'):
    """
    Build documentation. Requires Sphinx.

    :param builders: List of document builders separated with comma
    :param rootdir: Directory where to generate documents, per builder (optional)
    :param sphinxopts: Additional parameters to pass to Sphinx
    :param apidoc: If true, runs also apidoc. Defaults to false.
    """
    builders = builders.split(',') if builders else ['html']
    rootdir = rootdir if rootdir else build_join('docs')
    sphinxopts = sphinxopts or '-E'
    sourcedir = rel_join('docs')
    pysourcedir = rel_join('plugins/multiproject/multiproject')
    exclude_paths = ['tests', 'core/test', 'core/tests']

    for builder in builders:
        docbuild = os.path.join(rootdir, builder)
        if not os.path.exists(docbuild):
            os.makedirs(docbuild)

        if get_bool_str(apidoc):
            local('rm -rf %s' % join(sourcedir, 'reference'))
            local('sphinx-apidoc -o %s/reference %s %s' % (sourcedir, pysourcedir, ' '.join(exclude_paths)))
        local('sphinx-build %s -b %s %s %s' % (sphinxopts, builder, sourcedir, docbuild))

        logger.info('Built %s documentation to: %s' % (builder, docbuild))

@task
def autobuild(taskname='builddoc', watchdir='docs', taskopts=''):
    """
    Run given task whenever the files are changed
    Requires pyinotify

    :param taskname: Name of fabric task to run on events (inside dist namespace).
    :param watchdir: Path to directory what to watch for events. Relative to current directory.
    :param taskopts: Options to pass to task, separated by comma
    """
    import pyinotify

    watchdir = os.path.join(os.path.curdir, watchdir)
    wm = pyinotify.WatchManager()
    event = 'IN_CLOSE_WRITE'
    mask = getattr(pyinotify, event)

    class EventHandler(pyinotify.ProcessEvent):
        handling = False

        def process_IN_CLOSE_WRITE(self, event):
            if not self.handling:
                self.handling = True
                logger.info('Autorunning task: %s' % taskname)
                if taskopts:
                    globals()[taskname](*[opt for opt in taskopts.split(',')])
                else:
                    globals()[taskname]()
                self.handling = False

    handler = EventHandler()
    notifier = pyinotify.Notifier(wm, handler)
    wm.add_watch(watchdir, mask, rec=True)

    logger.info('Listening %s for %s events and running task: %s' % (watchdir, event, taskname))
    notifier.loop()

@task
def trac_admin(env, cmd, sudoer=None):
    """
    Runs trac-admin command on specified environment with permiss
    :param env: Name or path to the environment
    :param cmd: Command to pass to trac-admin
    :param sudoer: Optional sudo user, defaults to Apache user

    Examples::

        fab dist.trac_admin:home,help
        fab dist.trac_admin:"home","mp deploy"
        fab dist.trac_admin:env="home",cmd="mp deploy",sudoer="root"
        fab dist.trac_admin:"/var/www/trac/projects/projectx","upgrade"
        fab dist.trac_admin:"/var/www/trac/projects/projectx","upgrade","www-data"

    """
    trac_root_dir = config['trac_root']
    sudoer = sudoer or config['webserver_user']
    if sudoer == 'root':
        sudoer = None

    # Check if path is given, otherwise consider it project name
    if not exists(env):
        env = os.path.join(trac_root_dir, 'projects', env)
        if not exists(env):
            return abort('Given environment "%s" cannot be found on server' % env)

    with cd(env):
        tracadmin_cmd = 'trac-admin %s %s' % (env, cmd)
        sudo(tracadmin_cmd, user=sudoer)


@task
def test(case='', config='tests.ini'):
    """
    Runs the functional tests against the setup specified in configuration

    :param str case: Name or path to case file
    :param str config: Path to config file, relative to current directory

    Examples::

        fab dist.test:smoke
        fab dist.test:path/to/case.py
        fab dist.test:smoke,~/firefox.ini
        fab dist.test:smoke,config=path/to/config.ini

    """
    try:
        from nose.core import TestProgram
        from nose.plugins import Plugin
    except ImportError:
        TestProgram = None
        Plugin = object
        return abort('For running tests, Nose testing framework is required. Please install it first: "pip install nose"')

    if not case:
        return abort('Please provide either name or path to test case')

    # Determine the case file: name or path accepted
    webtests_dir = rel_join('tests/webtests')
    casepath = os.path.abspath(case) if case.endswith('.py') else join(webtests_dir, 'cases/%s.py' % case)
    configpath = os.path.join(os.curdir, os.path.expanduser(config))

    logger.info('Running functional tests from: %s' % casepath)
    logger.info('Reading tests configuration from: %s' % configpath)

    class TestConfigPlugin(Plugin):
        """
        Simple Nose plugin to set test configuration path to testcase::

            class MyTestcase(unittest.TestCase)
                def setUp(self):
                    self.config_path

        """
        name = 'testconfig'
        can_configure = True
        enabled = True

        def options(self, parser, env):
            pass

        def configure(self, options, conf):
            pass

        def startTest(self, test):
            test_case = test.test.__class__
            test_case.config_path = configpath

    TestProgram(argv=['fab', casepath], addplugins=[TestConfigPlugin()])


@task
def test_perf(params=''):
    """
    Runs the performance tests against the configured service and produce the report
    in dist/

    :params str params: Parameters to pass to Funkload bench

    Examples::

        fab dist.test_perf
        fab dist.test_perf:"-c 1:15 -D 1"

    """
    try:
        import funkload
    except ImportError:
        abort('Funkload module missing, please install it first')

    # Create report folder if needed
    report_dir = dist_join('report/html')
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    # Run the Funkload tests in perf test folder
    with lcd(rel_join('tests/perf')):
        with settings(show('running','stdout')):
            local('fl-run-bench %s tests.py MultiprojectTestCase.test_smoke' % params)
            local('fl-build-report -o %s --html smoke-bench.xml' % report_dir)

    logger.info('Testing completed. Test report can be found in: %s' % report_dir)


@task
def bundle(template_path='', resource_dir=''):
    """
    Finds out the resources files (css,js) from given template file (in example, ``resources.html``), bundles them into
    one package (stylepack_yymmdd.css, scriptpack_yymmdd.js) and generates bundle.html (in the same directory where
    template_path is), containing references to these files. This bundle.html file can be used in Genshi
    templates as follows::

         <xi:include href="bundle.html">
            <xi:fallback>
                <!-- Link resources normally -->
                <xi:include href="resources.html">
            <xi:fallback>
        </xi:include>

    Where ``resources.html`` contains::

        <html xmlns="http://www.w3.org/1999/xhtml"
              xmlns:py="http://genshi.edgewall.org/"
              py:strip="">
            <link rel="stylesheet" type="text/css" href="ui.css" />
            <script type="text/javascript" src="jquery-1.4.1.min.js" />
        </html>

    If bundle.html is found, only packaged resources are served to end users. Otherwise, the resources are served as-is.

    :param str template_path: Absolute path to HTML template
    :param str resource_dir: The parent directory where the resources are located in
    """
    assert template_path, 'Please provide template_path'
    assert resource_dir, 'Please provide resource_dir'

    now = datetime.utcnow()
    variable_regx = re.compile('\${(\w|-|_|\.)+}\/')
    hrp = HTMLResourceParser()

    logger.info('Parsing template file: %s' % template_path)

    # Operate with layout file
    with io.open(template_path, 'r') as layout_fd:
        # Read file into parser
        content = layout_fd.read()
        hrp.feed(content)

        # Bundle stylesheets
        css_bundle_path = os.path.join(resource_dir, 'css', now.strftime('stylepack_%y%m%d.css'))
        with io.open(css_bundle_path, 'w') as bundle_fd:
            # Iterate styles
            for style in hrp.styles:
                # Replace variable prefixed stylesheet with actual one
                style_path = os.path.join(resource_dir, variable_regx.sub('', style['href']))
                logger.debug('Bundle script: %s' % style_path)
                with io.open(style_path, 'r') as style_fd:
                    bundle_fd.write(style_fd.read())

        logger.info('Bundled %d stylesheets into %s' % (len(hrp.styles), css_bundle_path))

        # Bundle scripts
        js_bundle_path = os.path.join(resource_dir, 'js', now.strftime('scriptpack_%y%m%d.js'))
        with io.open(js_bundle_path, 'w') as bundle_fd:
            # Iterate scripts
            for script in hrp.scripts:
                # Replace variable prefixed script with actual one
                script_path = os.path.join(resource_dir, variable_regx.sub('', script['src']))
                logger.debug('Bundle script: %s' % script_path)
                with io.open(script_path, 'r') as script_fd:
                    bundle_fd.write(script_fd.read())

        logger.info('Bundled %d scripts into %s' % (len(hrp.scripts), js_bundle_path))

        # Generate build.html files, containing the resource links
        bundle_html_path = os.path.join(os.path.dirname(template_path), 'bundle.html')
        with open(bundle_html_path, 'w') as bundle_html_fd:
            bundle_html_fd.write('''
            <html xmlns="http://www.w3.org/1999/xhtml"
                  xmlns:py="http://genshi.edgewall.org/"
                  py:strip="">
                <link rel="stylesheet" type="text/css" href="${conf.theme_htdocs_location}/css/%s" />
                <script type="text/javascript" src="${conf.theme_htdocs_location}/js/%s" />
            </html>
            ''' % (os.path.basename(css_bundle_path), os.path.basename(js_bundle_path)))

        logger.info('Generated bundle HTML file: %s' % bundle_html_path)


