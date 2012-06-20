# -*- coding: utf-8 -*-
"""
Contains home project related page views/objects
"""
from webtests.toolkit import WebBrowser
from webtests.pages.base import PageObject, PageElement, TextInput, Checkbox, Link, Select, ElementNotFoundError


class LoginPage(PageObject):
    """
    Login page (/home/user)
    """
    def __init__(self):
        super(LoginPage, self).__init__()
        self.username = TextInput('input#fnloginUsername')
        self.password = Checkbox('input#fnloginPassword')
        self.submit = PageElement('input.blueInputBtn')


class WelcomePage(PageObject):

    def __init__(self):
        super(WelcomePage, self).__init__()
        # NOTE: All public projects link cannot be added because not all environments have it enabled
        self.my_projects = Link(partial_text='Go to My Projects')
        self.create_project = Link(partial_text='Create new project')


class CreateProjectPage(PageObject):
    """
    Login page (/home/user)
    """
    def __init__(self):
        super(CreateProjectPage, self).__init__()
        self.name = TextInput('input#prj_long_name')
        self.identifier = TextInput('input#prj_short_name')
        self.description = TextInput('textarea#prj_description')
        self.vcs_type = Select('select#vcstype')
        self.submit = PageElement('input#submit_create_form')

    def select_vcs(self, vcstype):
        browser = WebBrowser()
        element = browser.find_option_by_value(vcstype)
        if not element:
            raise ElementNotFoundError(vcstype)

        element[0].click()

