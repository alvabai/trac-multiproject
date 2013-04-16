# -*- coding: utf-8 -*-
from pkg_resources import resource_filename

from trac.wiki.model import WikiPage
from trac.wiki import IWikiMacroProvider
from trac.mimeview.api import Context, WikiTextRenderer
from trac.core import Component, implements
from trac.perm import IPermissionRequestor
from trac.web import IRequestHandler
from trac.web.chrome import ITemplateProvider, INavigationContributor, tag, Chrome, add_script, add_stylesheet
from trac.util.datefmt import LocalTimezone, utc
from trac.util.translation import _

from multiproject.core.util import to_web_time
from multiproject.core.categories import CQDECategoryStore
from multiproject.core.permissions import CQDEUserGroupStore
from multiproject.common.projects import Project
from multiproject.project.timeline import ProjectTimelineEvents


def local_to_utc(dt):
    aware = dt
    if not dt.tzinfo:
        local_tz = LocalTimezone()
        aware = local_tz.localize(dt)
    return aware.astimezone(utc)


class SummaryModule(Component):
    """ Trac component for showing project summary
    """
    implements(ITemplateProvider, IRequestHandler, IPermissionRequestor, INavigationContributor, IWikiMacroProvider)

    # Macros
    macros = {
        'ProjectSummary': '''
Provides a block for project summary.

Example usage:
{{{
[[ProjectSummary]]
}}}
''',
    }

    # IRequestHandler methods

    def match_request(self, req):
        """ Path used for showing this page
        """
        return req.path_info.startswith('/summary')

    def process_request(self, req):
        """ Process request for listing, creating and removing projects
        """
        add_script(req, 'multiproject/js/summary.js')
        data = {}

        if req.authname == 'anonymous':
            req.perm.require('PROJECT_VIEW')


        if not ('PROJECT_VIEW' in req.perm or 'PROJECT_PRIVATE_VIEW' in req.perm):
            return 'no_access.html', data, None

        # Load project from db
        project = Project.get(self.env)

        if req.args.get('action') == 'timeline_events':
            return self.get_summary_timeline_events(req, project.created)

        # TODO: Move project timeline implementation into macro
        # Get recent timeline events
        
        # TODO: Move project downloads implementation into macro
        # Get list of featured downloads
        downloads = []
        if self.env.is_component_enabled('tracdownloads.api.DownloadsApi'):
            api = None

            # In case of import error we don't have it, so don't return any downloads
            try:
                from tracdownloads.api import DownloadsApi
                api = DownloadsApi(self.env)
            except ImportError:
                self.log.warning("Unable to import DownloadsApi, but it's enabled.")

            if api:
                downloads = api.get_summary_items()

        # Load wiki:SummaryPage and show it as a main page
        summary_content = None
        summary_wiki = WikiPage(self.env, 'SummaryPage')
        if summary_wiki:
            context = Context.from_request(req, summary_wiki.resource)
            wiki_renderer = WikiTextRenderer(self.env)
            summary_content = wiki_renderer.render(context, 'text/x-trac-wiki', summary_wiki.text)

        
        data = {
            '_project_': project, # project object of a project we are in
            'downloads': downloads, # list of featured downloads
            'wiki_summary': summary_content, # Rendered content of the SummaryPage
            'is_summary': True,
            'env': self.env,
        }

        return 'summary.html', data, None

    def get_summary_timeline_events(self, req, project_created):
        timeline = ProjectTimelineEvents(self.env)
        #events = timeline.get_latest_timeline_events(req, 5)
        events = timeline.get_latest_timeline_events(req, 5, project_created)
        data = {
            'activities': events
        }
        return 'timeline_partial.html', data, None

    # INavigationContributor methods

    def get_active_navigation_item(self, req):
        return 'summary'

    def get_navigation_items(self, req):
        if 'PROJECT_VIEW' in req.perm:
            yield ('mainnav', 'summary',
                   tag.a('Summary', href = req.href()))

    # IPermissionRequestor methods

    def get_permission_actions(self):
        return ['PROJECT_VIEW', 'PROJECT_PRIVATE_VIEW',
                'MEMBERSHIP_REQUEST_CREATE', 'TEAM_VIEW']

    # ITemplateProvider methods

    def get_templates_dirs(self):
        return [resource_filename('multiproject.project.summary', 'templates')]

    def get_htdocs_dirs(self):
        return []

    # IWikiMacroProvider methods

    def get_macros(self):
        for macro in self.macros:
            yield macro

    def get_macro_description(self, name):
        return self.macros.get(name)

    def expand_macro(self, formatter, name, content, args=None):
        """
        Returns the outcome from macro.
        Supported arguments:

        - project: Name of the project to show status / provide follow buttons. Defaults to current project

        """
        req = formatter.req

        # Load project from db
        project = Project.get(self.env)

        # Get project metadata (categories)
        (combined_categories, separated_categories_per_context, context_by_id,
         context_order, languages) = self._get_project_categories(project)

        # Get project visibility: public or private
        visibility = _('Public') if project.public else _('Private')

        # Return rendered HTML with JS attached to it
        data = {
            '_project_': project,
            'combined_categories': combined_categories,
            'separated_categories_per_context': separated_categories_per_context,
            'context_order': context_order,
            'languages': languages,
            'context_by_id': context_by_id,
            'visibility_label': visibility, # Private / Public
            'to_web_time': to_web_time # TODO: Is this really required?
        }

        chrome = Chrome(self.env)
        stream = chrome.render_template(req, 'multiproject_summary.html', data, fragment=True)
        if req.form_token:
            stream |= chrome._add_form_token(req.form_token)

        return stream

    # Internal methods

    def _get_project_categories(self, project):
        """
        Create list of categories. License, Language and Development status are shown separately
        and are therefore taken out from the category listing.
        """
        # Get api
        cs = CQDECategoryStore()

        # Get categories and specialcase contexts
        categories = cs.get_all_project_categories(project.id)
        contexts = cs.get_contexts()

        combined_categories = []
        separated_categories_per_context = {}

        categories_by_any_context_id = {}
        context_by_id = {}

        # Setup the contexts dicts
        for context in contexts:
            context_by_id[context.context_id] = context
            if context.summary_name:
                # If context has summary name, it is shown as separated in the summary page
                new_list = []
                categories_by_any_context_id[context.context_id] = new_list
                separated_categories_per_context[context.context_id] = new_list
            else:
                categories_by_any_context_id[context.context_id] = combined_categories

        sort_opts = {'key':lambda c:c.name, 'cmp':lambda x,y: cmp(x.lower(), y.lower())}

        # Now, categories_by_any_context_id has key for each context id
        for category in categories:
            categories_by_any_context_id[category.context].append(category)
        for context_id in separated_categories_per_context:
            separated_categories_per_context[context_id].sort(**sort_opts)

        combined_categories.sort(**sort_opts)

        # Sort alphabetically, case-insensitively
        context_order = [c.context_id for c in
                         sorted(map(lambda id:context_by_id[id],
                             separated_categories_per_context.keys()),
                             key=lambda c:c.summary_name)]

        languages = []
        for context_id in separated_categories_per_context:
            context = context_by_id[context_id]
            if (context.summary_name
                and context.summary_name.lower() in ('language','natural language')):
                # Here, we expect that the description contains the language tag.
                # http://www.w3schools.com/tags/att_meta_http_equiv.asp
                # http://www.w3.org/TR/2011/WD-html-markup-20110113/meta.http-equiv.content-language.html
                languages = [c.description for c in separated_categories_per_context[context_id]]


        return (combined_categories, separated_categories_per_context, context_by_id,
               context_order, languages)
