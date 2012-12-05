"""
This py file can be also used as a python script to deploy htdocs.
.See python [this file] -h
"""
from ConfigParser import ConfigParser
import os

from trac.admin import AdminCommandError
from trac.util import copytree
from trac.util.text import printout
from trac.web.chrome import Chrome

from multiproject.core.util.mockenv import MockEnvironment


def _get_enabled_components(config_file):
    """:returns list of enabled components in the ``config_file``"""
    config_parser = ConfigParser()
    config_parser.read(config_file)
    if config_parser.has_section('components'):
        return [key for key, val in config_parser.items('components') if val == 'enabled']


def deploy_htdocs(env, dest=None, config_file=None, also_common=False, path=None):
    """
    :param Environment env: Environment instance, may be home or normal project.
    :param str dest: Destination where to put files. Defaults to [multiproject] static_htdocs_path.
    """
    keys = set()

    # construct list of enabled pugins in home project and normal project
    enabled_plugins = []
    project_ini = env.config.get('multiproject', 'global_conf_path')
    home_ini = os.path.join(env.config.get('multiproject', 'sys_projects_root'),
        env.config.get('multiproject', 'sys_home_project_name'), 'conf', 'trac.ini')
    enabled_plugins.extend(_get_enabled_components(project_ini))
    enabled_plugins.extend(_get_enabled_components(home_ini))

    env = MockEnvironment(config_file, enabled_plugins, path)

    if dest is None:
        dest = env.config.get('multiproject', 'static_htdocs_path', default=None)
        if dest is None:
            raise AdminCommandError('Destination not given and '
                                    '[multiproject] static_htdocs_path configuration is not set')
    chrome_target = dest

    # A slightly edited snippet from trac.env.EnvironmentAdmin._do_deploy
    chrome = Chrome(env)

    os.path.normpath(dest)

    for provider in chrome.template_providers:
        paths = list(provider.get_htdocs_dirs() or [])
        if not len(paths):
            continue
        for key, root in paths:
            if key == 'site':
                continue
            if key == 'common' and not also_common:
                continue
            keys.add(key)
            source = os.path.normpath(root)
            if os.path.exists(source):
                dest = os.path.join(chrome_target, key)
                copytree(source, dest, overwrite=True)

    printout('  Static htdocs deployed to directory %s ' % chrome_target)
    dirs = sorted([str(dir) for dir
                   in env.config.getlist('multiproject', 'static_htdocs_plugin_dirs', default=['*'])])
    if len(dirs) == 1 and dirs[0] == '*':
        pass
    elif dirs and set(dirs) != keys:
        printout('  Warning: [multiproject] static_htdocs_plugin_dirs is not up-to-date!')
        extra_dirs = [dir for dir in dirs if dir not in keys]
        if extra_dirs:
            printout('  It contains the following extra directories, which should be removed:')
            printout('    %s' % extra_dirs)
        extra_keys = [key for key in keys if key not in dirs]
        if extra_keys:
            printout('  The urls of the htdocs of the following plugins are not changed ')
            printout('  to use [multiproject] static_htdocs_location:')
            printout('    %s' % sorted(extra_keys))
        printout('  To fix these errors, change the configuration to be as follows:')
        printout('    "static_htdocs_plugin_dirs = %s"' % ','.join(sorted(list(keys))))
    elif not dirs:
        printout('  To use the static htdocs of the global plugins as static files, ')
        printout('  change the configuration to be as follows:')
        printout('    "static_htdocs_plugin_dirs = %s"' % ','.join(sorted(list(keys))))
