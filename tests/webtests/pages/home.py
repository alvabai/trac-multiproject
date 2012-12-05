# -*- coding: utf-8 -*-
"""
Contains home project related page views/objects
"""
from webtests.pages.base import PageObject, PageElement, TextInput, Checkbox, Link, Select, ElementNotFoundError


class LoginPage(PageObject):
    """
    Login page (/home/user)
    """
    def __init__(self):
        super(LoginPage, self).__init__()
        browser = self._browser
        self.username = TextInput(browser, 'input#fnloginUsername')
        self.password = Checkbox(browser, 'input#fnloginPassword')
        self.submit = PageElement(browser, 'input.blueInputBtn')


class WelcomePage(PageObject):

    def __init__(self):
        super(WelcomePage, self).__init__()
        # NOTE: All public projects link cannot be added because not all environments have it enabled
        browser = self._browser
        self.my_projects = Link(browser, partial_text='Go to My Projects')
        self.create_project = Link(browser, partial_text='Create new project')


class CreateProjectPage(PageObject):
    """
    Login page (/home/user)
    """
    def __init__(self):
        super(CreateProjectPage, self).__init__()
        browser = self._browser
        self.name = TextInput(browser, 'input#prj_long_name')
        self.identifier = TextInput(browser, 'input#prj_short_name')
        self.description = TextInput(browser, 'textarea#prj_description')
        self.vcs_type = Select(browser, 'select#vcstype')
        self.submit = PageElement(browser, 'input#submit_create_form')

    def select_vcs(self, vcstype):
        browser = self._browser
        element = browser.find_option_by_value(vcstype)
        if not element:
            raise ElementNotFoundError(browser, vcstype)

        element[0].click()

