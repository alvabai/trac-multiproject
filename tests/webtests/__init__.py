# -*- coding: utf-8 -*-
"""
This module contains the functional testcases, run by Selenium.
See docs/testing/functional.rst for how to -instructions.
"""
# Import common objects into webtests namespace
from splinter.request_handler.status_code import HttpResponseError

from webtests.toolkit import WebBrowser, Config
from webtests.pages.base import URL
from webtests.pages.base import PageObject
from webtests.pages.base import PageElement
from webtests.pages.base import TextInput
from webtests.pages.base import Checkbox
from webtests.pages.base import ElementNotFoundError
