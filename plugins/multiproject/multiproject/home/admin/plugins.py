# -*- coding: utf-8 -*-
import os, sys, shutil, inspect, pkg_resources

from trac import __version__ as TRAC_VERSION
from trac.admin.api import IAdminPanelProvider
from trac.core import Component, implements, TracError
# from trac.env import Environment
from trac.util import get_pkginfo, get_module_path
from trac.util.text import to_unicode
from trac.util.translation import _
from trac.config import Configuration as trac_configuration
from multiproject.core.configuration import Configuration as multiproject_configuration

conf = multiproject_configuration.instance()

def is_component_enabled(self, cls):
    """Implemented to only allow activation of components that are not
    disabled in the configuration.

    This is called by the `ComponentManager` base class when a component is
    about to be activated. If this method returns false, the component does
    not get activated."""

    if not isinstance(cls, basestring):
        component_name = (cls.__module__ + '.' + cls.__name__).lower()
    else:
        component_name = cls.lower()

    rules = [(name.lower(), value.lower() in ('enabled', 'on', 'required'))
             for name, value in self.config.options('components')]
    rules.sort(lambda a, b:-cmp(len(a[0]), len(b[0])))

    for pattern, enabled in rules:
        if component_name == pattern or pattern.endswith('*') \
                and component_name.startswith(pattern[:-1]):
            if component_name.startswith('webadmin.'):
                return False
            return enabled

    if component_name.startswith('trac.versioncontrol.'):
        return self.config.get('trac', 'repository_dir') != ''

    # By default, all components in the trac package are enabled
    return component_name.startswith('trac.')

# Replace orginal method with this. Orginal location is "trac.env.Environment"
# Environment.is_component_enabled = is_component_enabled

class PluginAdminPanel(Component):
    """ Enhanced Trac admin panel component for plugins
    """
    implements(IAdminPanelProvider)

    def __init__(self):
        self.trac_path = get_module_path(sys.modules['trac.core'])

    def get_admin_panels(self, req):
        if 'TRAC_ADMIN' in req.perm:
            yield ('general', _('General'), 'plugin', _('Plugins'))

    def render_admin_panel(self, req, cat, page, path_info):
        req.perm.require('TRAC_ADMIN')

        if req.method == 'POST':
            if 'install' in req.args:
                self._do_install(req)
            elif 'uninstall' in req.args:
                self._do_uninstall(req)
            else:
                self._do_update(req)
            anchor = ''
            if req.args.has_key('plugin'):
                anchor = '#no%d' % (int(req.args.get('plugin')) + 1)
            req.redirect(req.href.admin(cat, page) + anchor)

        return self._render_view(req)

    # Internal methods
    def _do_install(self, req):
        """Install a plugin."""
        if not req.args.has_key('plugin_file'):
            raise TracError(_('No file uploaded'))
        upload = req.args['plugin_file']
        if isinstance(upload, unicode) or not upload.filename:
            raise TracError(_('No file uploaded'))
        plugin_filename = upload.filename.replace('\\', '/').replace(':', '/')
        plugin_filename = os.path.basename(plugin_filename)
        if not plugin_filename:
            raise TracError(_('No file uploaded'))
        if not plugin_filename.endswith('.egg') and \
                not plugin_filename.endswith('.py'):
            raise TracError(_('Uploaded file is not a Python source file or '
                              'egg'))

        target_path = os.path.join(self.env.path, 'plugins', plugin_filename)
        if os.path.isfile(target_path):
            raise TracError(_('Plugin %(name)s already installed',
                              name = plugin_filename))

        self.log.info('Installing plugin %s', plugin_filename)
        flags = os.O_CREAT + os.O_WRONLY + os.O_EXCL
        try:
            flags += os.O_BINARY #@UndefinedVariable
        except AttributeError:
            # OS_BINARY not available on every platform
            pass
        target_file = os.fdopen(os.open(target_path, flags, 0666), 'w')
        try:
            shutil.copyfileobj(upload.file, target_file)
            self.log.info('Plugin %s installed to %s', plugin_filename,
                          target_path)
        finally:
            target_file.close()

        # TODO: Validate that the uploaded file is actually a valid Trac plugin

        # Make the environment reset itself on the next request
        self.env.config.touch()

    def _do_uninstall(self, req):
        """Uninstall a plugin."""
        plugin_filename = req.args.get('plugin_filename')
        if not plugin_filename:
            return
        plugin_path = os.path.join(self.env.path, 'plugins', plugin_filename)
        if not os.path.isfile(plugin_path):
            return
        self.log.info('Uninstalling plugin %s', plugin_filename)
        os.remove(plugin_path)

        # Make the environment reset itself on the next request
        self.env.config.touch()

    def _do_update(self, req):
        """Update component enablement."""
        components = req.args.getlist('component')
        oenabled = req.args.getlist('enable')
        penabled = req.args.getlist('prjenable')

        changes = False
        changed = {}

        # Set global project configuration
        prjconf = trac_configuration(conf.global_conf_path)

        for component in components:
            c_state = self.get_project_component_state(component, self.config)
            c_activated = (component in oenabled)

            if self.is_plugin_changed(c_state, c_activated):
                self.config.set('components', component,
                                c_activated and 'enabled' or 'disabled')
                self.log.info('%sabling component %s',
                                c_activated and 'En' or 'Dis', component)
                changes = True

            if prjconf:
                cip_state = self.get_project_component_state(component, prjconf)
                cip_activated = (component in penabled)

                if self.is_plugin_changed(cip_state, cip_activated):
                    self.log.info('%sabling project component %s',
                                    cip_activated and 'En' or 'Dis', component)
                    changed[component] = cip_activated and 'enabled' or 'disabled'
                    changes = True

        if prjconf:
            scomponents = req.args.getlist('setting')
            static_items = req.args.getlist('static_setting')

            for scomponent in scomponents:
                values = self.get_project_component_value(scomponent, None, prjconf)
                saved_value = self.parse_value(0, values)
                saved_static = self.parse_value(1, values)

                current_value = req.args.get(scomponent + '.value').replace('|', '')
                current_static = (scomponent in static_items)

                if saved_value != current_value or saved_static != current_static:
                    if current_static:
                        final_value = current_value
                    else:
                        final_value = current_value + '|no'

                    prjconf.set('settings', scomponent, final_value)
                    changes = True

        if changes:
            self.config.save()

            if prjconf:
                for key in changed.keys():
                    prjconf.set('components', key, changed[key])
                prjconf.save()

    def get_project_component_state(self, cls, confset):
        if not isinstance(cls, basestring):
            component_name = (cls.__module__ + '.' + cls.__name__).lower()
        else:
            component_name = cls.lower()

        rules = [(name.lower(), value.lower())
                 for name, value in confset.options('components')]
        rules.sort(lambda a, b:-cmp(len(a[0]), len(b[0])))

        for pattern, status in rules:
            if component_name == pattern or pattern.endswith('*') \
                    and component_name.startswith(pattern[:-1]):
                if component_name.startswith('webadmin.'):
                    return 'hide'
                return status

        if component_name.startswith('trac.versioncontrol.'):
            if self.config.get('trac', 'repository_dir') != '':
                return 'enabled'

        # By default, all components in the trac package are enabled
        if component_name.startswith('trac.'):
            return 'enabled'

        return 'disabled'

    def get_project_component_value(self, cls, default, prjconf):
        if not isinstance(cls, basestring):
            component_name = cls.__module__.lower()
        else:
            component_name = cls.lower()

        rules = [(name.lower(), value.lower())
                 for name, value in prjconf.options('components')]
        rules.sort(lambda a, b:-cmp(len(a[0]), len(b[0])))

        for pattern, status in rules:
            if component_name == pattern:
                return status

        return default

    def parse_value(self, position, values, default = None):
        if values:
            retval = values.split("|")
            count = len(retval)
            if count > position:
                return retval[position]
        return default

    def parse_boolean_value(self, position, values, default = None):
        if values:
            retval = values.split("|")
            count = len(retval)
            if count > position:
                return retval[position].lower() in ('true', 'yes')
        return default

    def is_plugin_changed(self, state, activated):
        if state == 'enabled':
            if not activated:
                return True
        if state == 'disabled':
            if activated:
                return True
        return False

    def is_plugin_enabled(self, state):
        if state == 'enabled' or state == 'required':
            return True
        else:
            return False

    def is_plugin_required(self, state):
        if state == 'required':
            return True
        else:
            return False

    def is_plugin_shown(self, state):
        if state == 'hide':
            return False
        else:
            return True

    def getSettings(self, cls, store):
        if not isinstance(cls, basestring):
            mymodule = cls.__module__.lower()
        else:
            mymodule = cls.lower()

        # Do not add duplicates
        for object in store:
            if mymodule in object['module']:
                return

        mycount = len(mymodule.split('.'))

        prjconf = trac_configuration(conf.global_conf_path)

        rules = [(name.lower(), value.lower())
                 for name, value in prjconf.options('components')]
        rules.sort(lambda a, b:-cmp(len(a[0]), len(b[0])))

        for pattern, value in rules:
            if pattern.startswith(mymodule + '.'):
                item = pattern.split(".")
                count = len(item)
                if count > mycount:
                    header = item[mycount]
                    if count > (mycount + 1):
                        store.append({
                                'module': mymodule,
                                'name':  header + '.' + item[mycount + 1],
                                'default': self.parse_value(0, value),
                                'static':  self.parse_boolean_value(1, value, True)
                            })

    def _render_view(self, req):
        plugins = {}
        plugins_dir = os.path.realpath(os.path.join(self.env.path, 'plugins'))
        plugins_dir = os.path.normcase(plugins_dir) # needs to match loader.py

        from trac.core import ComponentMeta
        for component in ComponentMeta._components:
            module = sys.modules[component.__module__]

            dist = self._find_distribution(module)
            plugin_filename = None
            if os.path.realpath(os.path.dirname(dist.location)) == plugins_dir:
                plugin_filename = os.path.basename(dist.location)

            description = inspect.getdoc(component)
            if description:
                description = to_unicode(description).split('.', 1)[0] + '.'

            if dist.project_name not in plugins:
                readonly = True
                if plugin_filename and os.access(dist.location,
                                                 os.F_OK + os.W_OK):
                    readonly = False
                # retrieve plugin metadata
                info = get_pkginfo(dist)
                if not info:
                    info = {'summary': description}
                    for k in ('author author_email home_page url license trac'
                              .split()):
                        v = getattr(module, k, '')
                        if v:
                            if k == 'home_page' or k == 'url':
                                k = 'home_page'
                                v = v.replace('$', '').replace('URL: ', '')
                            info[k] = v
                # retrieve plugin version info
                version = dist.version
                if not version:
                    version = (getattr(module, 'version', '') or
                               getattr(module, 'revision', ''))
                    # special handling for "$Rev$" strings
                    version = version.replace('$', '').replace('Rev: ', 'r')
                plugins[dist.project_name] = {
                    'name': dist.project_name, 'version': version,
                    'path': dist.location, 'description': description,
                    'plugin_filename': plugin_filename, 'readonly': readonly,
                    'info': info, 'components': [],
                    'settingheader': dist.project_name,
                    'settings': []
                }

            self.getSettings(component, plugins[dist.project_name]['settings'])

            prjconf = trac_configuration(conf.global_conf_path)

            pstate = self.get_project_component_state(component, prjconf)
            ostate = self.get_project_component_state(component, self.config)

            plugins[dist.project_name]['components'].append({
                   'name': component.__name__, 'module': module.__name__,
                   'description': description,
                   'enabled': self.is_plugin_enabled(ostate),
                   'required': self.is_plugin_required(ostate),
                   'view': self.is_plugin_shown(ostate),
                   'penabled': self.is_plugin_enabled(pstate),
                   'prequired': self.is_plugin_required(pstate),
                   'pview': self.is_plugin_shown(pstate),
               })

        def component_order(a, b):
            c = cmp(len(a['module'].split('.')), len(b['module'].split('.')))
            if c == 0:
                c = cmp(a['module'].lower(), b['module'].lower())
                if c == 0:
                    c = cmp(a['name'].lower(), b['name'].lower())
            return c
        for category in plugins:
            plugins[category]['components'].sort(component_order)

        plugin_list = [plugins['Trac']]
        addons = [key for key in plugins.keys() if key != 'Trac']
        addons.sort()
        plugin_list += [plugins[category] for category in addons]

        data = {
            'plugins': plugin_list,
            'readonly': not os.access(plugins_dir, os.F_OK + os.W_OK),
        }
        return 'admin_home_plugins.html', data


    def _find_distribution(self, module):
        path = get_module_path(module)
        if path == self.trac_path:
            return pkg_resources.Distribution(project_name = 'Trac',
                                              version = TRAC_VERSION,
                                              location = path)
        for dist in pkg_resources.find_distributions(path, only = True):
            return dist
        else:
            # This is a plain Python source file, not an egg
            return pkg_resources.Distribution(project_name = module.__name__,
                                              version = '',
                                              location = module.__file__)

