# -*- coding: utf-8; tab-width: 4 -*-
"""
Contents of this module
"""
import time
from ConfigParser import ConfigParser
import logging
import os
import urllib

from webtests.toolkit import WebBrowser, take_screenshot

initialized = False


class PageObject(object):
    """
    Model for the page
    """
    _browser = None
    _page_config = None

    def __init__(self, section=None):
        """
        :param section: Explicitly give out section name to be used for getting selector.
        Otherwise class name is used.
        """
        global initialized

        self.required_texts = []
        self.forbidden_texts = []
        self.section = section or self.__class__.__name__

        if not self._browser or not self._browser._config:
            raise Exception('Attribute _browser needs to be set first')

        config = self._browser._config

        # NOTE: Wait a little before loading the page browser can find elements
        time.sleep(float(config.get('request_sleep', '0.5')))

        # If already loaded, return right away
        if self._page_config is not None:
            return

        # Read page_definition location, relative to config file itself
        # (or if environment variables or home dir is used in path, the directly from those)
        page_config_path = os.path.join(
            os.path.dirname(config.path),
            os.path.expandvars(os.path.expanduser(config['page_definitions']))
        )

        # If still not found, give up
        if not os.path.exists(page_config_path):
            raise ValueError('configuration file %s not found' % page_config_path)
        elif not initialized:
            logging.info('Using page definitions: %s' % page_config_path)

        with open(page_config_path) as conffd:
            # Load default configuration
            page_config = ConfigParser()
            page_config.readfp(conffd)
            page_config.read(page_config_path)

            self._page_config = page_config

        initialized = True

    def selector(self, key):
        """
        Return selector from the configuration file. If the key value
        contains a colon character, the first part is considered as a selector type.

        :param key: Key name
        :return: Dictionary with two values: {'selector_type':'selector_value'}

        Example config::

            [PageName]
            name1 = value              # css selector by default
            name2 = partial_text:value # partial_text selector is used instead

        Python output:

        >>> link = PageObject()
        >>> link.selector('name1')
        {'css':'value'}
        >>> link.selector('name2')
        {'partial_text':'value'}

        """
        if not self._page_config:
            raise Exception('Page config missing: %s is incorrectly initialized' % self.__class__)

        value = self._page_config.get(self.section, key)

        # If colon exists, consider first part to be a selector type
        if ':' in value:
            parts = value.split(':', 1)
            return dict(str(parts[0]).strip(), str(parts[1]).strip())

        # Default to css selector
        return {'css': value}


    def verify_texts(self):
        """
        Check that all required texts defined in ``self.texts_present`` are present
        and none of ``self.forbidden_texts`` are.
        :raises: Exception if there is issue with texts present.
        """
        browser = self._browser
        for text in self.forbidden_texts:
            if browser.is_text_present(text):
                raise Exception('Forbidden text `%s` is present on the page.' % text)
        for text in self.required_texts:
            if not browser.is_text_present(text):
                raise Exception('Required text `%s` is not present on the page.' % text)

    def take_screenshot(self, nameformat=None):
        return take_screenshot(self._browser, nameformat)


class PageElement(object):
    """
    Base object for page elements. Works a bit like factory method, returns different instance
    based on circumstances.
    """
    def __new__(cls, browser, css=None, **kwargs):
        """
        Example with css_selector:
        >>> elem = PageElement('h1#role') # css-like selector
        Example with kwargs:
        >>> elem = PageElement(tag='h1')
        >>> elem = PageElement(text='hello world')

        :param css: CSS selector
        :param kwargs: Key=matcher, value=selector
        :returns: Instance of splinter ElementApi (?) if css_selector matches element on the page,
        otherwise instance of ElementNotFound is returned.
        """
        if isinstance(browser, WebBrowser):
            browser = browser.instance

        matches = None
        matchers = {
            'css': 'find_by_css',
            'xpath': 'find_by_xpath',
            'tag': 'find_by_tag',
            'partial_text': 'find_link_by_partial_text',
            'partial_href': 'find_link_by_partial_href',
            'text': 'find_link_by_text'
        }

        # Default to CSS selector
        if not kwargs:
            assert css, 'Either css or other type of selector needs to be given'
            kwargs['css'] = css

        for matcher, selector in kwargs.items():
            matches = getattr(browser, matchers[matcher])(selector)
            if matches:
                break

        if matches:
            element = matches.first
            element.browser = browser
            return element

        raise ElementNotFoundError(browser, kwargs)


class TextInput(PageElement):
    pass


class Submit(PageElement):
    pass


class Checkbox(PageElement):
    pass


class Select(PageElement):
    pass


class Link(PageElement):
    pass


class ElementNotFoundError(Exception):
    """
    Custom error that is thrown when element matcher did
    not found the specified element.
    """
    def __init__(self, browser, selectors, *args, **kwargs):
        self.selectors_msg = '''Selectors %s didn't match any elements on the page (%s) and
        'therefore the attempt to call method on it failed.''' % (selectors, browser.url)

        # Try taking screenshot from issue
        take_screenshot(browser, nameformat='${browser}-error.${ext}')

        super(ElementNotFoundError, self).__init__(self.selectors_msg, *args, **kwargs)

    def __str__(self):
        return self.selectors_msg


class URL(object):
    """
    Helper class for easy URL generation.

    >>> url = URL('http://localhost/')
    >>> url('home')
    'http://localhost/home'
    >>> url('home', foo='bar', hum='baz')
    'http://localhost/home?foo=bar&hum=baz'

    """
    def __init__(self, baseurl='http://localhost/'):
        self.baseurl = baseurl[:-1] if baseurl.endswith('/') else baseurl
        self.path = ''

    def __call__(self, *args, **kwargs):
        """
        Emulates function while being a class
        """
        if args:
            self.path = '/'.join([str(arg) for arg in args])

        if kwargs:
            urlargs = [(str(key), str(val)) for key, val in kwargs.items()]
            self.path = '%s?%s' % (self.path, urllib.urlencode(urlargs, True))

        return str(self)

    def __str__(self):
        """
        Return string presentation of the URL class... the URL itself
        """
        self.url = self.baseurl + '/%s' % self.path
        return self.url

