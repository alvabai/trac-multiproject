# -*- coding: utf-8 -*-
import re
from pkg_resources import resource_filename #@UnresolvedImport

from genshi.builder import tag
from trac.wiki.model import WikiPage
from trac.core import Component, implements
from trac.mimeview.api import Context, WikiTextRenderer
from trac.web import IRequestHandler
from trac.web.chrome import ITemplateProvider, INavigationContributor

from multiproject.common.projects import Projects
from multiproject.core.configuration import conf
from multiproject.home.timeline.api import GlobalTimeline

class WelcomeModule(Component):
    """ Trac component for showing welcome screen for user with most relevant
        user content in it.

        Should be used on home project only.
    """
    implements(ITemplateProvider, IRequestHandler, INavigationContributor)

    # INavigationContributor methods
    def get_active_navigation_item(self, req):
        """ Item that is highlighted when welcome is active
        """
        return 'Welcome'

    def get_navigation_items(self, req):
        """ Introduce navigation item
        """
        yield ('mainnav', 'Welcome',
               tag.a('Welcome', href = req.href.welcome()))

    # IRequestHandler methods
    def match_request(self, req):
        """ Match /welcome path to this page
        """
        return re.match(r'/welcome(?:_trac)?(?:/.*)?$', req.path_info)

    def process_request(self, req):
        """ Render welcome page
        """

        # Prepare data for template
        prjs = Projects()
        data = {}
        data['baseurl'] = conf.url_projects_path
        if req.authname == 'anonymous':
            conf.redirect(req)

        # Get project count
        data['project_count'] = prjs.project_count()

        store = conf.getUserStore()
        user = store.getUser(req.authname)
        global_timeline = GlobalTimeline()

        anon = store.getUser('anonymous')
        if anon:
            data['mostactiveprojects'] = prjs.get_projects_for_rss(anon.id, 0, 5, "MOSTACTIVE")
            data['newestprojects'] = prjs.get_projects_for_rss(anon.id, 0, 5, "NEWESTFILTERED")
            data['featuredprojects'] = prjs.get_projects_for_rss(anon.id, 0, 5, "FEATURED")

        data['is_insider'] = user.isProjectBrowsingAllowed()
        data['latest_events'] = global_timeline.get_latest_events(req.authname, 5)

        # Check if user is allowed to create project
        data['can_create_project'] = user.can_create_project()

        # Configuration values the welcome page wants
        data['site_name'] = conf.site_name
        data['site_title_text'] = conf.site_title_text
        data['site_punch_line'] = conf.punch_line
        data['site_theme_path'] = conf.getThemePath()

        wiki_welcome = self._get_welcome_page(req)
        if wiki_welcome:
            data['wiki_welcome'] = wiki_welcome

        return "welcome.html", data, None

    def _get_welcome_page(self, req):
        rendered_page = None
        wiki_welcome = WikiPage(self.env, 'WelcomePage')
        if wiki_welcome:
            context = Context.from_request(req, wiki_welcome.resource)
            wiki_renderer = WikiTextRenderer(self.env)
            rendered_page = wiki_renderer.render(context, 'text/x-trac-wiki', wiki_welcome.text)
        return rendered_page

    # ITemplateProvider methods
    def get_templates_dirs(self):
        return [resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        return []
