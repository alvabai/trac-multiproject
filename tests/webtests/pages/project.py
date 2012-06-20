# -*- coding: utf-8 -*-
"""
Contains project related Page Objects

NewTicketPage class uses selectors from configuration file as an example and proof of concept.
"""
from webtests.toolkit import WebBrowser
from webtests.pages.base import PageObject, PageElement, TextInput, Checkbox, Link, WebBrowser, Submit


class Navigation(PageObject):

    def __init__(self):
        super(Navigation, self).__init__()
        self.summary = Link(partial_text="Summary")
        self.wiki = Link(partial_text="Wiki")
        self.timeline = Link(partial_text="Timeline")
        self.roadmap = Link(partial_text="Roadmap")
        self.source = Link(partial_text="Source")
        self.files = Link(partial_text="Files")
        self.tickets = Link(partial_text="Tickets")
        self.search = Link(text="Search")
        self.admin = Link(partial_text="Admin")
        self.discussion = Link(partial_text="Discussion")


class ProjectLayout(PageObject):
    """
    Abstraction for project layout, should contain everything that is
    accessible from all pages, e.g. navigation.
    """

    def __init__(self):
        super(ProjectLayout, self).__init__()
        self.navigation = Navigation()


class TicketsPage(ProjectLayout):
    def __init__(self):
        super(TicketsPage, self).__init__()
        self.new_ticket = Link(partial_text='New Ticket')


class NewTicketPage(ProjectLayout):

    def __init__(self):
        super(NewTicketPage, self).__init__()
        self.summary = TextInput(**self.selector('summary'))
        self.reporter = TextInput(**self.selector('reporter'))
        self.description = TextInput(**self.selector('description'))
        self.submit = PageElement(**self.selector('submit'))


class TicketReviewPage(ProjectLayout):
    """
    Single ticket view
    """
    def __init__(self):
        super(TicketReviewPage, self).__init__()
        self.modify = Link(**self.selector('modify'))
        self.submit = PageElement(**self.selector('submit'))

        # Elements that are hidden/non-existing at first
        self.cc_block = None
        self.cc_field = None
        self.cc_button = None

    def activate_modify(self):
        self.modify.click()
        self.cc_block = TextInput(**self.selector('cc_block'))
        self.cc_button = PageElement(**self.selector('cc_button'))

    def set_cc(self, value):
        # Click to button just for testing purposes
        self.cc_button.click()

        # Input field is hidden until block is clicked
        self.cc_block.click()
        self.cc_field = TextInput(**self.selector('cc_input'))
        self.cc_field.value = value


class WikiPage(ProjectLayout):

    def __init__(self):
        super(WikiPage, self).__init__()
        browser = WebBrowser()
        self.edit_page = browser.find_by_value('Edit this page')


class EditWikiPage(ProjectLayout):

    def __init__(self):
        super(EditWikiPage, self).__init__()
        self.text = TextInput('textarea#text')
        self.comment = TextInput('input#comment')
        self.preview = PageElement('input[name="preview"]')
        self.review = PageElement('input[name="diff"]')
        self.submit = PageElement('input[name="save"]')


class TimelinePage(ProjectLayout):
    pass


class RoadmapPage(ProjectLayout):

    def __init__(self):
        super(RoadmapPage, self).__init__()
        self.required_texts = ['Show completed milestones']


class SourcePage(ProjectLayout):

    def __init__(self):
        super(SourcePage, self).__init__()
        self.required_texts = ['All sources']


class FilesPage(ProjectLayout):

    def __init__(self):
        super(FilesPage, self).__init__()
        self.required_texts = ['Last modified']


class SearchPage(ProjectLayout):

    def __init__(self):
        super(SearchPage, self).__init__()
        self.input = TextInput('input#searchForProjects')
        self.submit = Submit('button#searchProjectsBtn')
        self.required_texts = ['Select area']

    def select_area(self, title):
        """
        Find and click the search criteria link based on title

        :param str title: Link title
        """
        browser = WebBrowser()
        arealink = browser.find_link_by_text(title).last
        arealink.click()

    def do_search(self, term):
        self.input.fill(term)
        self.submit.click()


class AdminNavigation(PageObject):
    def __init__(self):
        super(AdminNavigation, self).__init__()
        self.basic = Link(partial_text="Basic")
        self.announcement = Link(partial_text="Announcements")
        self.backup = Link(partial_text="Backup")
        self.category = Link(partial_text="Categorization")
        self.icon = Link(partial_text="Project Icon")
        self.relation = Link(partial_text="Project relations")
        self.storage = Link(partial_text="Storages")
        self.system = Link(partial_text="System")
        self.forum = Link(partial_text="Forums")
        self.forum_group = Link(partial_text="Forum Groups")
        self.download = Link(partial_text="Downloads")
        self.platform = Link(partial_text="Platforms")
        self.type = Link(partial_text="Types")
        self.user = Link(partial_text="Users")
        self.group = Link(partial_text="Groups")
        self.component = Link(partial_text="Components")
        self.milestone = Link(partial_text="Milestones")
        self.priority = Link(partial_text="Priorities")
        self.resolution = Link(partial_text="Resolutions")
        self.severity = Link(partial_text="Severities")
        self.ticket_type = Link(partial_text="Ticket Types")
        self.version = Link(partial_text="Versions")


class AdminPage(ProjectLayout):

    def __init__(self):
        super(AdminPage, self).__init__()
        self.admin_navigation = AdminNavigation()
        self.required_texts = ['Basic Settings']

class AdminSystemPage(ProjectLayout):

    def remove_project(self):
        button = PageElement('input[name="remove"]')
        button.click()

        # Handle alert confirmation
        browser = WebBrowser()
        alert = browser.get_alert()
        alert.accept()


class DiscussionPage(ProjectLayout):

    def __init__(self):
        super(DiscussionPage, self).__init__()
        self.required_texts = ['Forum index', 'Moderator']
