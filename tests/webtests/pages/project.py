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
        browser = self._browser
        self.summary = Link(browser, partial_text="Summary")
        self.wiki = Link(browser, partial_text="Wiki")
        self.timeline = Link(browser, partial_text="Timeline")
        self.roadmap = Link(browser, partial_text="Roadmap")
        self.source = Link(browser, partial_text="Source")
        self.files = Link(browser, partial_text="Files")
        self.tickets = Link(browser, partial_text="Tickets")
        self.search = Link(browser, text="Search")
        self.admin = Link(browser, partial_text="Admin")
        self.discussion = Link(browser, partial_text="Discussion")


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
        self.new_ticket = Link(self._browser, partial_text='New Ticket')


class NewTicketPage(ProjectLayout):

    def __init__(self):
        super(NewTicketPage, self).__init__()
        browser = self._browser
        self.summary = TextInput(browser, **self.selector('summary'))
        self.reporter = TextInput(browser, **self.selector('reporter'))
        self.description = TextInput(browser, **self.selector('description'))
        self.submit = PageElement(browser, **self.selector('submit'))


class TicketReviewPage(ProjectLayout):
    """
    Single ticket view
    """
    def __init__(self):
        super(TicketReviewPage, self).__init__()
        self.modify = Link(self._browser, **self.selector('modify'))
        self.submit = PageElement(self._browser, **self.selector('submit'))

        # Elements that are hidden/non-existing at first
        self.cc_block = None
        self.cc_field = None
        self.cc_button = None

    def activate_modify(self):
        self.modify.click()
        self.cc_block = TextInput(self._browser, **self.selector('cc_block'))
        self.cc_button = PageElement(self._browser, **self.selector('cc_button'))

    def set_cc(self, value):
        # Input field is hidden until block is clicked
        self.cc_field = TextInput(self._browser, **self.selector('cc_input'))
        self.cc_field.value = value
        self.cc_button.click()


class WikiPage(ProjectLayout):

    def __init__(self):
        super(WikiPage, self).__init__()
        browser = self._browser
        self.edit_page = browser.find_by_value('Edit this page')


class EditWikiPage(ProjectLayout):

    def __init__(self):
        super(EditWikiPage, self).__init__()
        browser = self._browser
        self.text = TextInput(browser, 'textarea#text')
        self.comment = TextInput(browser, 'input#comment')
        self.preview = PageElement(browser, 'input[name="preview"]')
        self.review = PageElement(browser, 'input[name="diff"]')
        self.submit = PageElement(browser, 'input[name="save"]')


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
        self.required_texts = ['Date modified']


class SearchPage(ProjectLayout):

    def __init__(self):
        super(SearchPage, self).__init__()
        self.input = TextInput(self._browser, 'input#searchForProjects')
        self.submit = Submit(self._browser, 'button#searchProjectsBtn')
        self.required_texts = ['Select area']

    def select_area(self, title):
        """
        Find and click the search criteria link based on title

        :param str title: Link title
        """
        browser = self._browser
        arealink = browser.find_link_by_text(title).last
        arealink.click()

    def do_search(self, term):
        self.input.fill(term)
        self.submit.click()


class AdminNavigation(PageObject):
    def __init__(self):
        super(AdminNavigation, self).__init__()
        browser = self._browser
        self.basic = Link(browser, partial_text="Basic")
        self.announcement = Link(browser, partial_text="Announcements")
        self.backup = Link(browser, partial_text="Backup")
        self.category = Link(browser, partial_text="Categorization")
        self.icon = Link(browser, partial_text="Project Icon")
        self.system = Link(browser, partial_text="System")
        self.forum = Link(browser, partial_text="Forums")
        self.forum_group = Link(browser, partial_text="Forum Groups")
        self.permissions = Link(browser, partial_text="Permissions")
        self.group = Link(browser, partial_text="Groups")
        self.component = Link(browser, partial_text="Components")
        self.milestone = Link(browser, partial_text="Milestones")
        self.priority = Link(browser, partial_text="Priorities")
        self.resolution = Link(browser, partial_text="Resolutions")
        self.severity = Link(browser, partial_text="Severities")
        self.ticket_type = Link(browser, partial_text="Ticket Types")
        self.version = Link(browser, partial_text="Versions")


class AdminPage(ProjectLayout):

    def __init__(self):
        super(AdminPage, self).__init__()
        self.admin_navigation = AdminNavigation()
        self.required_texts = ['Basic Settings']


class AdminSystemPage(ProjectLayout):

    def remove_project(self):
        button = PageElement(self._browser, 'input[name="remove"]')
        button.click()

        # Handle confirmation dialog: first button is Confirmation
        browser = self._browser
        browser.find_by_css('span.ui-button-text').first.click()


class DiscussionPage(ProjectLayout):

    def __init__(self):
        super(DiscussionPage, self).__init__()
        self.required_texts = ['Forum index', 'Moderator']
