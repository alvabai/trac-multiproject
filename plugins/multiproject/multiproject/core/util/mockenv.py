import os

from trac.config import Configuration
from trac.core import ComponentManager
from trac.env import Environment


class MockEnvironment(Environment):
    """
    An mock Environment object which does not need real environment.
    Useful for when needing real environment like access to loaded plugins etc
    but no environment is at hand. Looks like normal project by default but can be
    made to look like home project environment or hybrid of both.

    .. WARNING:: Be careful when using this!
    """
    def __init__(self, config_file=None, enabled_plugins=None, path=None):
        """
        :param str config_file: path to the main configuration file.
            Defaults to ``/etc/trac/project.ini`` which is normal project configuration.
        :param list enabled_plugins:
            An explicit list of plugins to load, instead of reading enabled [components]
            from ``config_file``. If empty list is given no plugins are loaded.
            However plugins can be still listed via ``extra_plugins`` arg.
        :param str path: path to the imaginary trac location.
        """
        if config_file is None:
            # TODO: switch to some constant when can be done without conf
            from multiproject.core.configuration import Configuration as multiproj_config
            conf = multiproj_config.instance()
            config_file = conf.config_file

        # From Environment.setup_config:
        self.config = Configuration(config_file)

        if path is None:
            path = os.path.join(self.config.get('multiproject', 'sys_projects_root'), '__mock_environment__')
        if enabled_plugins is not None:
            # explicit list given, disable all from configuration
            for key, val in self.config.options('components'):
                self.config.remove('components', key)
            # and replace with the given list
            for plugin in enabled_plugins:
                self.config.set('components', plugin, u'enabled')

        # We override the Environment.__init__ here.

        # Environment.__init__ is as follows:

        # ComponentManager.__init__(self)
        #
        # self.path = path
        # self.systeminfo = []
        # self._href = self._abs_href = None
        #
        # if create:
        #     self.create(options)
        # else:
        #     self.verify()
        #     self.setup_config()
        #
        # if create:
        #     for setup_participant in self.setup_participants:
        #         setup_participant.environment_created()

        # The Environment.setup_config is as follows:

        # self.config = Configuration(os.path.join(self.path, 'conf',
        #         'trac.ini'))
        #         self.setup_log()
        #         from trac.loader import load_components
        #         plugins_dir = self.shared_plugins_dir
        #         load_components(self, plugins_dir and (plugins_dir,))

        # We use suitable lines from these as follows:

        # From Environment.__init__:
        ComponentManager.__init__(self)

        self.path = path
        self.systeminfo = []
        self._href = self._abs_href = None

        # Our own plugin hack ends here, and setup_config lines continue here
        self.setup_log()
        from trac.loader import load_components
        load_components(self)
