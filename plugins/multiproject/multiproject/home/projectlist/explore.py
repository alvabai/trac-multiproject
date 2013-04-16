# -*- coding: utf-8 -*-
import math
import bisect
import os.path

from trac.core import Component, implements
from trac.perm import PermissionCache
from trac.web.api import IRequestHandler
from trac.web.chrome import add_stylesheet, add_script
from trac.util.translation import _

from multiproject.core.configuration import conf
from multiproject.core.watchlist import CQDEWatchlistStore
from multiproject.core.categories import CQDECategoryStore
from multiproject.core.db import admin_query, safe_int
from multiproject.common.projects import Projects
from multiproject.common.projects import HomeProject


class FindProjectsModule(Component):
    implements(IRequestHandler)

    MAX_RESULTS_TO_DISPLAY = 100
    DEFAULT_RESULTS_TO_DISPLAY = 10
    SUBPAGE_RANGE = 2
    TOP_CATEGORY_COUNT = 12
    LIST_EMPTY_CATEGORIES = False

    # List tabs that we have
    TABS = [('active', 'Active'),
            ('recent', "Recent")]

    DEFAULT_TAB = 'active'

    def match_request(self, req):
        """ Match /welcome path to this page
        """
        return req.path_info.startswith('/project/explore')

    def process_request(self, req):
        """ Process find page request
        """
        explore_comp = self.env[FindProjectsModule]
        if not explore_comp.has_explore_perm(req):
            req.redirect(conf.url_home_path)

        action = req.args.get('action') or 'page'
        if action == 'results':
            return self._filtered_resultset_partial(req)
        elif action == 'rss':
            return self._filtered_resultset_partial(req, rss = True)
        else:
            return self._show_regular_page(req)

    def _filtered_resultset_partial(self, req, rss = False):
        # Fetch request arguments
        filter, category_id_list, sub_page = self.fetch_req_args(req)

        # Which tab is requested
        tab = self.resolve_tab(req)

        # Get optional number of results per page.
        # If not set, or bigger than max, default to MAX_RESULTS_TO_DISPLAY
        numresults = req.args.get('numresults', '')
        if not numresults or not numresults.isdigit():
            numresults = self.DEFAULT_RESULTS_TO_DISPLAY
        elif int(numresults) > self.MAX_RESULTS_TO_DISPLAY:
            numresults = self.MAX_RESULTS_TO_DISPLAY
        numresults = int(numresults)

        # Fetch projects based on tab
        if tab == "download":
            projects = Projects().searchMostDownloaded()
            activities = None
            if projects is None:
                project_count = 0
            else:
                project_count = len(projects)
        else:
            projects, activities, project_count = Projects().search(filter, category_id_list, req.authname, tab, sub_page, numresults)

        # Some calculations for pagination
        # NOTE: math.ceil returns a float
        total_page_count = int(math.ceil(float(project_count) / numresults))

        range_center_point = sub_page
        if range_center_point <= self.SUBPAGE_RANGE:
            range_center_point = 1 + self.SUBPAGE_RANGE

        if range_center_point + 1 >= total_page_count:
            range_center_point = total_page_count - self.SUBPAGE_RANGE

        start_page = range_center_point - self.SUBPAGE_RANGE
        if start_page < 1:
            start_page = 1

        end_page = range_center_point + self.SUBPAGE_RANGE
        if end_page > total_page_count:
            end_page = total_page_count

            
        if projects or len(projects) > 0:
            # Activity css classes for activity meters
            if activities:
                activity_classes = self.activities_to_classes(activities)
            else:
                activity_classes = {}
            # Get categories for projects that was searched
            project_categories = self.get_project_categories(projects)
            # Get number of project watchers
            project_watchers = self.get_project_watchers(projects)
        else:
            activity_classes = {}
            project_categories = ""
            project_watchers = ""
        if project_count:
            if tab == 'recent':
                showing_clause = _("Showing %(start)s - %(end)s most recent projects out of %(total)s",
                    start = (sub_page - 1) * numresults + 1,
                    end = min(sub_page * numresults, project_count),
                    total = project_count)
            elif tab == 'download':
                showing_clause = _("Showing %(start)s - %(end)s most recent projects out of %(total)s",
                    start = (sub_page - 1) * numresults + 1,
                    end = min(sub_page * numresults, project_count),
                    total = project_count)
            else:
                showing_clause = _("Showing %(start)s - %(end)s active projects out of %(total)s",
                    start = (sub_page - 1) * numresults + 1,
                    end = min(sub_page * numresults, project_count),
                    total = project_count)
        else:
            showing_clause = _("No results")

        if not rss:

            return "projects_partial.html", {'projects':projects,
                               'project_categories':project_categories,
                               'project_watchers':project_watchers,
                               'selected_categories':category_id_list,
                               'selected_tab':tab,
                               'tabs':self.TABS,
                               'total_pages':total_page_count,
                               'start_page':start_page,
                               'end_page':end_page,
                               'sub_page':sub_page,
                               'showing_clause':showing_clause,
                               'activity_classes':activity_classes,
                               'search_filter':filter or 'Search Projects'}, None
        else:
            data = {}
            data['projects'] = projects
            data['projroot'] = conf.url_service
            data['host'] = conf.domain_name
            if tab == 'active':
                data['sorting'] = "most active"
            elif tab == 'recent':
                data['sorting'] = "most recent"
            else:
                data['sorting'] = ""

            # TODO: optimize find_categories
            categories = self._find_categories(category_id_list)
            cat_string = ""
            sec_string = ""
            if len(categories) == 1:
                cat_string = "in " + categories[0] + " category"
                sec_string = "in " + categories[0] + " section"
            elif len(categories) > 1:
                cat_string = "in " + ", ".join(categories) + " categories"
                sec_string = "in " + ", ".join(categories) + " sections"
            data['category_string'] = cat_string
            data['section_string'] = sec_string
            data['resultslink'] = conf.url_service + req.href() + req.path_info + "#" + req.query_string

            return "project_list.rss", data, 'application/rss+xml'

    def _find_categories(self, category_id_list):
        """
        """
        if not category_id_list:
            return []

        query = ("SELECT category_name FROM categories WHERE category_id in (%s)" %
                 ",".join(str(safe_int(item)) for item in category_id_list))

        data = []
        with admin_query() as cursor:
            try:
                conf.log.debug(query)
                cursor.execute(query)

                for row in cursor:
                    data.append(row[0])
            except:
                conf.log.exception("Finding categories failed: '''%s'''" % query)
                raise

        return data


    def _show_regular_page(self, req):
        req_data = {}
        # Resolve some static data needed on page (categories and project count)
        cs = CQDECategoryStore()
        all_categories = cs.get_all_categories()

        all_contexts = cs.get_contexts()
        combined_context_ids, combined_contexts, non_combined_contexts = self.get_combined_contexts(all_contexts)

        # Total count of projects and count of projects in categories
        direct_category_counts = Projects().get_project_counts_per_category(req.authname)

        req_data['direct_category_counts'] = direct_category_counts
        req_data['combined_context_ids'] = combined_context_ids
        req_data['non_combined_contexts'] = non_combined_contexts

        self.set_category_data_into_request_data(all_categories, req_data)

        add_stylesheet(req, 'multiproject/css/multiproject.css')
        add_script(req, 'multiproject/js/jquery.ba-bbq.js')
        add_script(req, 'multiproject/js/explore.js')

        return "find.html", {
            'top_categories': req_data['top_categories'],
            'categories': req_data['root_categories_of_combined_contexts'],
            'nonbrowsable_cntxt': req_data['non_empty_non_combined_contexts'],
            'selected_tab': self.DEFAULT_TAB,
            'tabs': self.TABS}, \
            None

    def get_combined_contexts(self, all_contexts):
        """
        Returns combined contexts categories and their ids
        """

        # TODO: Change this to use combined_contexts
        combined_contexts = {}
        combined_context_ids = []
        non_combined_contexts = {}

        for context in all_contexts:
            if context.explore_projects_visibility == context.EXPLORE_PROJECT_TYPE_COMBINED:
                combined_contexts[context.context_id] = context
                combined_context_ids.append(context.context_id)
            else:
                non_combined_contexts[context.context_id] = context

        return combined_context_ids, combined_contexts, non_combined_contexts

    def set_category_data_into_request_data(self, categories, req_data):
        """
        Counts projects in categories.

        Puts keys 'top_categories', 'root_categories_of_combined_contexts',
        and 'non_empty_non_combined_contexts' into req_data.

        :param dict categories: Dictionary of category id => category (with child categories)
        :param dict req_data: Dictionary having direct_category_counts and combined_context_ids
        """
        direct_category_counts = req_data['direct_category_counts']
        combined_context_ids = req_data['combined_context_ids']
        # contains category_id => Category (with additional cumulative_count attribute)
        new_categories_with_counts = {}
        root_categories_of_combined_contexts = []
        non_combined_contexts = req_data['non_combined_contexts']
        non_empty_non_combined_contexts = {}

        # List of triples: (-count, name, category) in a sorted order (smallest first)
        top_category_triples = []

        for category_orig in categories.values():
            category = self.get_cumulative_cat_project_count(category_orig, direct_category_counts,
                new_categories_with_counts)
            count = category.cumulative_count
            # Only those categories with cumulative count > 0 are given into the template function.
            if category.parent is None and count > 0:
                if category.context in combined_context_ids:

                    # We want largest of count, minimum of name
                    # -> minimum of -count, minimum of name
                    pushed_triple = (-count, category.name, category)
                    # If old minimum value is the same, push category into top categories.
                    insertion_index = bisect.bisect(top_category_triples, pushed_triple)
                    if len(top_category_triples) < self.TOP_CATEGORY_COUNT:
                        top_category_triples.insert(insertion_index, pushed_triple)
                    elif insertion_index >= len(top_category_triples):
                        root_categories_of_combined_contexts.append(category)
                    else:
                        # insertion_index < len(top_category_triples), so let's pop out the last one
                        top_category_triples.insert(insertion_index, pushed_triple)
                        popped_triple = top_category_triples.pop()
                        root_categories_of_combined_contexts.append(popped_triple[2])
                else:
                    # context not in combined_context_ids
                    # Add this category as a child of the proper context
                    context = non_combined_contexts[category.context]
                    if category.context not in non_empty_non_combined_contexts:
                        non_empty_non_combined_contexts[category.context] = context
                    context.add_child(category)

        sort_opts = {'key':lambda c:c.name, 'cmp':lambda x,y: cmp(x.lower(), y.lower())}

        root_categories_of_combined_contexts.sort(**sort_opts)
        req_data['root_categories_of_combined_contexts'] = root_categories_of_combined_contexts
        non_empty_non_combined_contexts = sorted(non_empty_non_combined_contexts.values(),**sort_opts)
        req_data['non_empty_non_combined_contexts'] = non_empty_non_combined_contexts

        top_root_categories = map(lambda x:x[2], top_category_triples)

        req_data['top_categories'] = top_root_categories

    def get_cumulative_cat_project_count(self, category, direct_counts, new_categories_with_counts):
        """
        Recursive method for fetching total project count
        for category and it's children
        """
        if category.category_id in new_categories_with_counts:
            return new_categories_with_counts[category.category_id]

        count = 0
        new_category = category.copy_without_children()
        if category.category_id in direct_counts:
            count = direct_counts[category.category_id]
        for sub_cat in category.children:
            new_sub_cat = self.get_cumulative_cat_project_count(sub_cat,
                direct_counts, new_categories_with_counts)
            if new_sub_cat.cumulative_count > 0:
                count += new_sub_cat.cumulative_count
                new_category.add_child(new_sub_cat)
        new_category.cumulative_count = count
        new_categories_with_counts[category.category_id] = new_category
        return new_category

    def resolve_tab(self, req):
        """ Based on url, resolve what to do
        """
        tab = req.args.get('tab') or self.DEFAULT_TAB
        if tab not in ['recent', 'active', 'download']:
            tab = self.DEFAULT_TAB
        return tab

    def fetch_req_args(self, req):
        """ Fetch arguments from request
        """
        # Keyword filter
        filter = req.args.get('f') or ''

        # Categories as filter
        category_id_list = []
        try:
            category_filters = req.args.get('c[]')
            if isinstance(category_filters, list):
                category_id_list = [int(item.replace('_top','')) for item in category_filters if item and item != 'all']
            elif category_filters != 'all':
                category_id_list = [int(category_filters.replace('_top',''))]
        except:
            self.log.debug("Improper category parameters when searching!")

        sub_page = req.args.get('page', '1')
        if not sub_page.isdigit():
            self.log.debug("Improper sub page parameter when searching!")
            sub_page = 1

        return filter, category_id_list, int(sub_page)

    def activities_to_classes(self, activities):
        """ Changes project activity into activity css classes of
            l,ql,qh,h (High, Quite High, Quite low, Low)
        """
        bounds = Projects().get_activity_quartals()
        project_classes = {}
        classes = ['l', 'ql', 'qh', 'h']

        # For each project_id, activity pair find correct css class
        for id, activity in activities.items():
            # low as default. Go through bounds until match
            index = 0
            for idx, bound in enumerate(bounds):
                if bound > activity:
                    break
                index = idx
            project_classes[id] = classes[index]
        return project_classes

    def get_project_categories(self, projects):
        """ Returns a map of project categories
            project_id => category string
        """
        cs = CQDECategoryStore()
        project_categories = {}

        for project in projects:
            cats = cs.get_all_project_categories(project.id, ordered=True)
            cats_joined = ', '.join([cat.name.split("#")[0] for cat in cats])
            project_categories[project.id] = cats_joined

        return project_categories

    def get_project_watchers(self, projects):
        """ Returns a map of project watchers.
            project_id => number of watchers
        """
        w = CQDEWatchlistStore()
        project_watchers = {}

        for project in projects:
            watchlist = w.get_watchers_by_project(project.id)
            project_watchers[project.id] = len(watchlist)

        return project_watchers

    def has_explore_perm(self, req):
        """
        Helper function for checking if user has permission to view explore view
        :param Request req: Trac request
        :return: True or False
        """
        perms = req.perm

        # Check if explore available for all
        if self.config.getbool('multiproject', 'allow_public_projects', True):
            return True

        # Check if user is TRAC_ADMIN in home env (open only if needed)
        if self.config.get('multiproject', 'sys_home_project_name') != os.path.basename(self.env.path):
            perms = PermissionCache(HomeProject().get_env(), req.authname)

        return 'TRAC_ADMIN' in perms
