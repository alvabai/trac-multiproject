# -*- coding: utf-8 -*-
from pkg_resources import resource_filename

from trac.wiki.model import WikiPage
from trac.mimeview.api import Context, WikiTextRenderer
from trac.core import Component, implements
from trac.perm import IPermissionRequestor
from trac.web import IRequestHandler
from trac.web.chrome import ITemplateProvider, INavigationContributor, tag, Markup
from trac.util.datefmt import LocalTimezone, utc
from trac.util.translation import _

from multiproject.common.projects import Projects
from multiproject.core.categories import CQDECategoryStore
from multiproject.core.permissions import CQDEUserGroupStore
from multiproject.project.timeline import ProjectTimelineEvents


def local_to_utc(dt):
    aware = dt
    if not dt.tzinfo:
        local_tz = LocalTimezone()
        aware = local_tz.localize(dt)
    return aware.astimezone(utc)

def format_dt(dt):
    utc_dt = local_to_utc(dt)
    return utc_dt.isoformat().split('+')[0].split('.')[0]


class SummaryModule(Component):
    """ Trac component for showing project summary
    """
    implements(ITemplateProvider, IRequestHandler, IPermissionRequestor, INavigationContributor)

    def match_request(self, req):
        """ Path used for showing this page
        """
        return req.path_info.startswith('/summary')

    def process_request(self, req):
        """ Process request for listing, creating and removing projects
        """
        data = {}

        if req.authname == 'anonymous':
            req.perm.require('SUMMARY_VIEW')

        if not ('SUMMARY_VIEW' in req.perm or 'PRIVATE_SUMMARY_VIEW' in req.perm):
            return 'no_access.html', data, None

        data = self._init_data_for_summary(req)

        return 'summary.html', data, None

    def get_active_navigation_item(self, req):
        return 'summary'

    def get_navigation_items(self, req):
        if 'SUMMARY_VIEW' in req.perm:
            yield ('mainnav', 'summary',
                   tag.a('Summary', href = req.href()))

    def _init_data_for_summary(self, req):
        """
        Reads all necessary data to display the summary page. Uses
        downloads plugin, gets metadata, team and timeline...

        :returns: A massive dict containing all data needed on the summary page
        """
        data = {}

        env_name = self.env.path.split('/')[-1]
        project = Projects().get_project(env_name=env_name)

        # Get project metadata (categories)
        (combined_categories, separated_categories_per_context, context_by_id,
         context_order, languages) = self._metadata(project)

        # Get recent timeline events
        timeline = ProjectTimelineEvents(self.env)
        events = timeline.get_latest_timeline_events(req, 5)

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

        # Get project visibility, Public or Private
        ug = CQDEUserGroupStore(project.trac_environment_key)
        visibility = _('Public') if ug.is_public_project() else _('Private')

        summary_content = None
        summary_wiki = WikiPage(self.env, 'SummaryPage')
        if summary_wiki:
            context = Context.from_request(req, summary_wiki.resource)
            wiki_renderer = WikiTextRenderer(self.env)
            summary_content = wiki_renderer.render(context, 'text/x-trac-wiki', summary_wiki.text)

        data = {
            '_project_': project, # project object of a project we are in
            'activities': events, # list of latest activities
            'downloads': downloads, # list of featured downloads
            'combined_categories': combined_categories,
            'separated_categories_per_context': separated_categories_per_context,
            'context_order': context_order,
            'languages': languages,
            'context_by_id': context_by_id,
            'visibility_label': visibility, # Private / Public
            'wiki_summary': summary_content, # Rendered content of the SummaryPage
            'is_summary': True,
            'env': self.env,
            'fmt_date': format_dt,
        }

        return data

    def _metadata(self, project):
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

    def get_permission_actions(self):
        return ['SUMMARY_VIEW', 'PRIVATE_SUMMARY_VIEW',
                'ALLOW_REQUEST_MEMBERSHIP', 'TEAM_VIEW']

    def get_templates_dirs(self):
        return [resource_filename('multiproject.project.summary', 'templates')]

    def get_htdocs_dirs(self):
        return []

