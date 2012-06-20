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
from contextlib import contextmanager
import time
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

    def __new__(cls, *arg):
        if not Config.instance:
            Config.instance = super(Config, cls).__new__(cls)
        return Config.instance

    def __init__(self):
        """
        Initialize test configuration. It expects to find tests.ini config file from:

        1. ~/tests.ini
        2. ./tests.ini

        """
        # Find and parse tests configuration
        self.parser = ConfigParser(self.defaults())
        self.path = self.parser.read([os.path.expanduser('~/tests.ini'), 'tests.ini'])[0]
        self.group = self.parser.get('general', 'setup')

        logging.info('Using test configuration: %s, setup: %s' % (self.path, self.group))
        logging.info('Using page definitions: %s' % os.path.join(self.path, self.get('page_definitions')))

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

  def __new__(cls, *arg):
      if not WebBrowser.instance:
          # Read the browser driver from config: chrome (default), firefox,..
          WebBrowser.instance = Browser(Config().get('browser', 'chrome').lower())
      return WebBrowser.instance


@contextmanager
def take_screenshot(browser):
    """
    Context funtion to take screenshot in the end of the current task.
    Name of the file is generated based on current browser url

    >>> with take_screenshot(browser):
    ...   browser.find_element_by_id('mylink').click()
    >>>

    """
    # Create FS compatible file name based on current browser url
    parseresult = urlparse(browser.current_url)
    path = parseresult.path[1:] if parseresult.path.startswith('/') else parseresult.path
    urlfile = path.replace('/','_')

    yield
    time.sleep(0.5)

    # TODO: Read the location from the configuration file
    browser.get_screenshot_as_file('/tmp/selenium_sc-%s.png' % urlfile)