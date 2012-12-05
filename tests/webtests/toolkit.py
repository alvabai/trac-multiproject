# -*- coding: utf-8 -*-
"""
WebBrowser:
    Simple wrapper on top of ``splinter.browser.Browser``

Config:
    Singleton class for reading the test configuration

    The configuration file is tests.ini which should be placed
    in the webtests root directory.

    The configuration file can include any number of environment
    setups. The setup used in the test run can be chosen by 'setup'
    entry in the 'general' section
"""
from urlparse import urlparse
from string import Template
import logging
import os
from ConfigParser import ConfigParser, NoOptionError

from splinter.browser import Browser


__all__ = ['Config', 'WebBrowser']


class Config(object):
    """
    Small wrapper on top of ConfigParser, reading configuration file ``tests.ini``
    automatically from:

    - Current folder
    - User home folder

    To read the values::

        config = Config()
        config.get('section', 'optionname', 'default')

    """
    instance = None

    def __new__(cls, config_path):
        if not Config.instance:
            Config.instance = super(Config, cls).__new__(cls, config_path)
        return Config.instance

    def __init__(self, config_path):
        """
        Initialize test configuration.

        """
        # Find and parse tests configuration
        self.parser = ConfigParser(self.defaults())
        paths = [os.path.expanduser(config_path)]
        paths_found = self.parser.read(paths)
        if not paths_found:
            raise Exception('Configuration file was not found from expected locations: %s' % paths)

        self.path = paths_found[0]
        self.group = self.parser.get('general', 'setup')

        logging.info('Using test configuration: %s, setup: %s' % (self.path, self.group))

    def __getitem__(self, item):
        """
        Provides config access in lookup style:

        >>> config = Config()
        >>> config['key']
        'value'

        """
        return self.get(item)

    def get(self, option, default=None):
        """
        Reads the option from specified section, or returns
        the default
        """
        try:
            return self.parser.get(self.group, option)
        except NoOptionError:
            if default is None:
                raise
        return default

        # If no default is set, raise an error
        if default is None:
            raise NoOptionError
        return default


    def defaults(self):
        """
        Returns the configuration defaults
        """
        return {
            'host':'localhost',
            'user':'tracadmin',
            'password':'tracadmin',
            'page_definitions':'',
            'vcs':'svn', # Valid values: svn, git, hg
            'style':'',
        }

class WebBrowser(object):
  """
  Singleton browser
  """
  instance = None

  def __new__(cls, config):
      if not WebBrowser.instance:
          # Read the browser driver from config: chrome (default), firefox,..
          WebBrowser.instance = Browser(config.get('browser', 'chrome').lower())
          WebBrowser.instance._config = config
      return WebBrowser.instance


def take_screenshot(browser, nameformat=None):
    """
    Take screenshot immediatelly from the current browser view.

    Screenshots are created to location defined in configuration by
    ``screenshot_dir = /tmp`` (defaults to ``/tmp``)

    .. NOTE::

        - If ``screenshot_dir`` is empty, taking screenshots is skipped altogher.
        - Image format is always PNG

    :param str nameformat:
        Optional name format that can contain placeholders:

        - browser: Name of the browser: chrome, firefox, ..
        - sequence: Running sequence number 1,2,3...
        - url: URL to the browser

        Defaults to: ${browser}-${sequence}-${url}.${ext}

    :return: Path to screenshot
    """
    config = browser._config
    browser_name = config.get('browser', 'chrome')
    screenshot_dir = config.get('screenshot_dir', '/tmp')

    # If not set, skip taking screenshots
    if not screenshot_dir:
        return

    # Using singleton class as calculator
    browser.screenshot_counter = browser.screenshot_counter + 1 if hasattr(browser, 'screenshot_counter') else 1

    parseresult = urlparse(browser.url)
    path = parseresult.path[1:] if parseresult.path.startswith('/') else parseresult.path
    urlfile = path.replace('/','_')

    nametemplate = Template(nameformat or '${browser}-${sequence}-${url}.${ext}')
    filename = nametemplate.substitute(browser=browser_name, sequence=browser.screenshot_counter, url=urlfile, ext='png')
    screenshot_file = os.path.join(screenshot_dir, filename)

    try:
        # Create screenshot dir if not existing yet
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)

        # Try taking the screenshot (may fail with some drivers)
        browser.driver.save_screenshot(screenshot_file)
        logging.info('Captured screenshot to: %s' % screenshot_file)

    except Exception:
        logging.warning('Failed to take screenshot')

    return screenshot_file




