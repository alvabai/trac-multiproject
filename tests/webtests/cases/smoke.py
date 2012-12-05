# -*- coding: utf-8 -*-
"""
Contents of this module
"""
import logging
import os
import time
import unittest

from webtests import WebBrowser, HttpResponseError, URL, ElementNotFoundError, Config
from webtests.pages.base import PageObject
from webtests.pages.home import LoginPage
from webtests.pages.home import WelcomePage
from webtests.pages.home import CreateProjectPage
from webtests.pages.project import (
    ProjectLayout, TicketsPage, NewTicketPage, TicketReviewPage, WikiPage, EditWikiPage,
    TimelinePage, RoadmapPage, SourcePage, SearchPage, FilesPage, DiscussionPage, AdminPage,
    AdminSystemPage
)


class SmokeTestCase(unittest.TestCase):
    """
    Smoke test set to cover basic usage of the service
    """
    def setUp(self):

        # Read configuration path set by custom Nose plugin (see tasks/dist.py:test)
        config_path = getattr(self, 'config_path', os.path.join(os.curdir, 'tests.ini'))

        self.project_name = 'New project'
        self.project_env = 'newproject'
        self.project_desc = 'desc for new project'

        self.config = Config(config_path)

        self.browser = WebBrowser(self.config)
        self.user = self.config['user']
        self.password = self.config['password']
        self.host = self.config['host']
        self.url = URL(self.config['host'])

        # Monkeypatch PageObject to have config and browser
        #PageObject._config = self.config
        PageObject._browser = self.browser

        # Login to service
        self.browser.visit(self.url('home/user'))

        login = LoginPage()
        login.username.value = self.user
        login.password.value = self.password
        login.submit.click()

        # Remove the project if it exists
        # FIXME: This one is bit odd: service returns 404 but status code is 200
        # while page models raises ElementNotFoundError
        try:
            self.browser.visit(self.url(self.project_env))
            if self.browser.status_code.is_success():
                project_summary = ProjectLayout()
                project_summary.navigation.admin.click()
                adminpage = AdminPage()
                adminpage.admin_navigation.system.click()
                adminremove = AdminSystemPage()
                adminremove.remove_project()
                time.sleep(2)
        except (HttpResponseError, ElementNotFoundError) as err:
            logging.info('Project was not found, no need to remove it (%s)' % err)
            pass

    def test_smoke(self):
        # Login to service
        ticket_summary = 'Testitiketti'
        ticket_description = 'testi testi testi'
        wiki_text = 'wiki test'
        wiki_comment = 'testing'

        # ensure the old project with the same identifier is removed
        # Head to create project page
        self.browser.visit(self.host + 'home')
        welcome = WelcomePage()
        welcome.create_project.click()

        # Create new project
        create = CreateProjectPage()
        create.name.value = self.project_name
        create.identifier.value = self.project_env
        create.description.value = self.project_desc
        create.select_vcs(self.config['vcs'])
        create.take_screenshot()
        create.submit.click()

        # We're on the project summary page
        layout = ProjectLayout()

        # Head to create a new ticket
        layout.navigation.tickets.click()

        tickets = TicketsPage()
        tickets.new_ticket.click()

        new_ticket = NewTicketPage()
        new_ticket.summary.value = ticket_summary
        new_ticket.description.value = ticket_description
        new_ticket.take_screenshot()
        new_ticket.submit.click()

        # We're on the review page of the new ticket, check for the entered values to be present
        ticket_review = TicketReviewPage()
        assert self.browser.is_text_present(ticket_summary)
        assert self.browser.is_text_present(ticket_description)

        # Add cc
        # TODO: Implement modify as a context
        ticket_review.activate_modify()
        ticket_review.set_cc(self.user)
        ticket_review.take_screenshot()
        ticket_review.submit.click()

        # Go to wiki
        ticket_review = TicketReviewPage()
        ticket_review.navigation.wiki.click()

        wiki = WikiPage()
        wiki.edit_page.click()

        # edit the wiki page
        edit_wiki = EditWikiPage()
        edit_wiki.text.value = wiki_text
        edit_wiki.comment.value = wiki_comment
        edit_wiki.submit.click()

        # check the modifications are there
        wiki = WikiPage()
        wiki.take_screenshot()
        assert self.browser.is_text_present(wiki_text)
        wiki.navigation.timeline.click()

        timeline = TimelinePage()
        assert self.browser.is_text_present(wiki_comment)
        assert self.browser.is_text_present(ticket_summary)
        assert self.browser.is_text_present(ticket_description)
        timeline.take_screenshot()
        timeline.navigation.roadmap.click()

        roadmap = RoadmapPage()
        roadmap.verify_texts()
        roadmap.take_screenshot()
        roadmap.navigation.source.click()

        source = SourcePage()
        source.verify_texts()
        source.take_screenshot()
        source.navigation.files.click()

        files = FilesPage()
        files.verify_texts()
        files.take_screenshot()
        files.navigation.search.click()

        # Search for created ticket
        search = SearchPage()
        search.verify_texts()
        search.select_area('Tickets')
        time.sleep(3)  # Sleep due the ajax request that enables the field
        search.do_search(ticket_summary)
        time.sleep(3)  # Sleep due the ajax request
        assert self.browser.is_text_present('defect: %s' % ticket_summary)
        search.take_screenshot()
        search.navigation.discussion.click()

        # Finally, land on discussion page
        discussion = DiscussionPage()
        discussion.verify_texts()
        discussion.take_screenshot()
        discussion.navigation.admin.click()

        # Go through each admin view
        admin = AdminPage()
        admin.verify_texts()

        admin = AdminPage()
        admin.take_screenshot()
        admin.admin_navigation.basic.click()

        admin = AdminPage()
        admin.take_screenshot()
        admin.admin_navigation.announcement.click()

        admin = AdminPage()
        admin.take_screenshot()
        admin.admin_navigation.backup.click()

        admin = AdminPage()
        admin.take_screenshot()
        admin.admin_navigation.category.click()

        admin = AdminPage()
        admin.take_screenshot()
        admin.admin_navigation.icon.click()

        admin = AdminPage()
        admin.take_screenshot()
        admin.admin_navigation.relation.click()

        admin = AdminPage()
        admin.take_screenshot()
        admin.admin_navigation.storage.click()

        admin = AdminPage()
        admin.take_screenshot()
        admin.admin_navigation.system.click()

        admin = AdminPage()
        admin.take_screenshot()
        admin.admin_navigation.forum.click()

        admin = AdminPage()
        admin.take_screenshot()
        admin.admin_navigation.forum_group.click()

        admin = AdminPage()
        admin.take_screenshot()
        admin.admin_navigation.permissions.click()

        admin = AdminPage()
        admin.take_screenshot()
        admin.admin_navigation.group.click()

        admin = AdminPage()
        admin.take_screenshot()
        admin.admin_navigation.component.click()

        admin = AdminPage()
        admin.take_screenshot()
        admin.admin_navigation.milestone.click()

        admin = AdminPage()
        admin.take_screenshot()
        admin.admin_navigation.priority.click()

        admin = AdminPage()
        admin.take_screenshot()
        admin.admin_navigation.resolution.click()

        admin = AdminPage()
        admin.take_screenshot()
        admin.admin_navigation.severity.click()

        admin = AdminPage()
        admin.take_screenshot()
        admin.admin_navigation.ticket_type.click()

        admin = AdminPage()
        admin.take_screenshot()
        admin.admin_navigation.version.click()

    def tearDown(self):
        #self.browser.quit()
        pass
