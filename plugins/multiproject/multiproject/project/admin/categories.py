# -*- coding: utf-8 -*-
import re

from trac.core import Component, implements, TracError
from trac.web import IRequestHandler
from trac.admin.api import IAdminPanelProvider
from trac.web.chrome import add_notice, add_warning, add_script, add_stylesheet
from trac.util.translation import _

from multiproject.common.projects import Project
from multiproject.core.categories import CQDECategoryStore, Context
from multiproject.core.db import safe_int


class CategorizationAdminPanel(Component):
    """ Trac admin panel component for categorizing project
    """
    implements(IAdminPanelProvider, IRequestHandler)

    def __init__(self):
        self.categ = CQDECategoryStore()
        self.first_context = None

    # IAdminPanelProvider interface requirement
    def get_admin_panels(self, req):
        """ Admin panel navigation items
        """
        if 'TRAC_ADMIN' in req.perm:
            yield ('general', 'General', 'categorization', 'Categorization')

    # IAdminPanelProvider interface requirement
    def render_admin_panel(self, req, cat, page, path_info):
        """ Renders categorization admin panel
        """
        req.perm.require('TRAC_ADMIN')


        context_data = self._get_context_data()
        if req.args.get('add_and_bind'):
            self.add_and_bind_category(req, context_data)

        add_script(req, 'multiproject/js/jquery-ui.js')
        add_script(req, 'multiproject/js/categorization.js')
        add_stylesheet(req, 'multiproject/css/jquery-ui.css')

        all_contexts = context_data['all_contexts']
        not_separate_context_ids = context_data['not_separate_context_ids']
        context_by_id = context_data['context_by_id']
        combined_context_ids = context_data['combined_context_ids']

        # First index is reserved for main context
        contexts = [None]
        main_context_id = context_data['main_context_id']
        for context in all_contexts:
            if context.context_id in not_separate_context_ids:
                continue
            contexts.append(context)
        if main_context_id != -1:
            contexts[0] = context_by_id[main_context_id]
        else:
            # No main context id -> drop the first one
            contexts = contexts[1:]

        main_addable_contexts = []
        for context_id in not_separate_context_ids:
            if context_by_id[context_id].edit_type == Context.EDIT_TYPE_ADD:
                main_addable_contexts.append(context_by_id[context_id])

        cats_per_context, project_cats_per_context = self._get_categories_data(context_data)

        data = {}
        data['env'] = req.base_path
        data['contexts'] = contexts
        data['categories_per_context'] = cats_per_context
        data['project_categories_per_context'] = project_cats_per_context
        data['main_addable_contexts'] = main_addable_contexts
        data['not_separate_context_ids'] = not_separate_context_ids
        return 'admin_categories.html', data

    def match_request(self, req):
        """ Path to categorization for ajax requests
        """
        return re.match(r'/categories(?:_trac)?(?:/.*)?$', req.path_info)

    def process_request(self, req):
        """ Ajax request processing. Binding and unbinding categories
        """
        req.perm.require('TRAC_ADMIN')


        # Get parameters
        action = req.args.get('action')
        context_key = req.args.get('context_key')
        category_key = req.args.get('category_key')

        context_data = self._get_context_data(context_key)
        project_key = context_data['project_key']

        # Select action
        if "bind" == action:
            #if req.method != 'POST':
            #    raise TracError('POST request required')
            self.categ.bind_category_project(project_key, category_key)
        elif "unbind" == action:
            #if req.method != 'POST':
            #    raise TracError('POST request required')
            self.categ.unbind_category_project(project_key, category_key)

        return self.show_categories(req, context_key, context_data)

    def show_categories(self, req, context_key, context_data):
        """ Shows those categories that belongs into project and context
            that is given.
        """
        context_key = safe_int(context_key)

        if (context_key in context_data['combined_context_ids']
            or context_key in context_data['autocomplete_context_ids']):
            raise TracError('Cannot show combined categories')
        context_id = context_key
        # categories for main context are stored to index -1
        if context_key == context_data['main_context_id']:
            context_id = -1

        cats_per_context, project_cats_per_context = self._get_categories_data(context_data)
        data = {
            'context': context_data['context_by_id'][context_key],
            'categories': cats_per_context[context_id],
            'project_categories': project_cats_per_context[context_id],
            'env': req.base_path
        }

        return 'categories.html', data, None

    def add_and_bind_category(self, req, context_data):
        """
        Called by render_admin_panel
        """
        req.perm.require('TRAC_ADMIN')
        if req.method != 'POST':
            raise TracError('POST request required')

        category_name = req.args.get('category_name', '')
        l_url = req.args.get('license_url')
        if category_name and l_url:
            category_name = category_name.strip()
            l_url = l_url.strip()
            category_name = category_name + "#" + l_url

        cat = self.categ.get_category_by_name(category_name)
        if not cat:
            context_id = safe_int(req.args.get('context_id', '').strip())

            if not context_id or context_id not in context_data['context_by_id']:
                add_warning(req, _("Invalid context"))
                return

            if not category_name:
                add_warning(req, _("Invalid category"))
                return

            context = context_data['context_by_id'][context_id]

            if context.edit_type != context.EDIT_TYPE_ADD:
                add_warning(req, _("Adding category into context %(context_name) is not allowed",
                    context_name=context.name))
                return

            try:
                self.categ.add_category(category_name, category_name, context_id, None)
                cat = self.categ.get_category_by_name(category_name)
            except Exception as e:
                add_warning(req, _('Category %(what)s cannot be added.',
                    what = category_name) + _(str(e)))
                return

        project_key = context_data['project_key']
        if cat and project_key and self.categ.bind_category_project(project_key, cat.category_id):
            add_notice(req, _('Category %(what)s has been added.',
                               what = category_name.split("#")[0]))
        else:
            add_warning(req, _('Category %(what)s cannot be added.',
                               what = category_name.split("#")[0]))

    def _get_context_data(self, context_id = None):
        """

        Returns dict with keys and values (type means here context.admin_type)::
            combined_context_ids: ids of contexts of type combined but not autocomplete
            not_separate_context_ids: set of ids of contexts of type combined, main, or autocomplete
            autocomplete_context_ids: ids of contexts of type autocomplete
            main_context_id: id of the context with type main, defaults to -1
            context_by_id: context_id => context mapping
            all_contexts: all contexts
            involved_context_ids: ids of contexts for which the categories are needed to be fetched
            context_id: safe context id of the request

        :returns: dict with data
        """
        main_context_id = -1

        combined_context_ids = []
        autocomplete_context_ids = []
        not_separate_context_ids = set([])
        context_by_id = {}
        all_contexts = self.categ.get_contexts()
        context_id = safe_int(context_id)
        project_key = Project.get(self.env).id

        for context in all_contexts:
            context_by_id[context.context_id] = context
            if context.admin_type == context.ADMIN_TYPE_MAIN:
                if main_context_id != -1:
                    self.log.warning("Invalid category data: Duplicate main contexts")
                    context.admin_type = context.ADMIN_TYPE_COMBINED
                else:
                    main_context_id = context.context_id
                    not_separate_context_ids.add(context.context_id)
            if context.admin_type == context.ADMIN_TYPE_COMBINED:
                combined_context_ids.append(context.context_id)
                not_separate_context_ids.add(context.context_id)
            elif context.admin_type == context.ADMIN_TYPE_AUTOCOMPLETE:
                autocomplete_context_ids.append(context.context_id)
                not_separate_context_ids.add(context.context_id)
        if main_context_id == -1:
            self.log.warning('Invalid category data: Main context not set!')

        involved_context_ids = []
        if context_id:
            if context_id not in context_by_id:
                raise TracError('Invalid context id provided %s' %context_id.__class__)
            if context_id == main_context_id:
                involved_context_ids = [main_context_id]+combined_context_ids+autocomplete_context_ids
            else:
                involved_context_ids = [context_id]
        else:
            involved_context_ids = [context.context_id for context in all_contexts]
        data = {'project_key': project_key,
           'autocomplete_context_ids': autocomplete_context_ids,
           'combined_context_ids': combined_context_ids,
           'not_separate_context_ids': not_separate_context_ids,
           'main_context_id': main_context_id,
           'context_by_id': context_by_id,
           'all_contexts': all_contexts,
           'involved_context_ids': involved_context_ids,
           'context_id': context_id}
        return data

    def _get_categories_data(self, context_data):
        """
        Returns 'categories_per_context' and 'project_categories_per_context',
        both being dictionaries with context_id keys and values, which are
        dictionaries with category_id keys and category values.
        """
        context_by_id = context_data['context_by_id']
        main_context_id = context_data['main_context_id']
        project_key = context_data['project_key']
        categories_per_context = {-1: {}}
        project_categories_per_context = {-1: {}}
        for i_context_id in context_data['involved_context_ids']:
            context = context_by_id[i_context_id]
            if context.admin_type in (context.ADMIN_TYPE_MAIN, context.ADMIN_TYPE_COMBINED):
                categories_per_context[-1].update(
                    self.categ.get_all_categories_in_context(i_context_id))
                project_categories_per_context[-1].update(
                    self._get_categories_by_project(project_key, i_context_id)
                    )
            elif context.admin_type == context.ADMIN_TYPE_AUTOCOMPLETE:
                # categories_per_context[i_context_id] -- don't show anywhere!
                project_categories_per_context[-1].update(
                    self._get_categories_by_project(project_key, i_context_id))
            else:
                categories_per_context[i_context_id] = \
                    self.categ.get_all_categories_in_context(i_context_id)
                project_categories_per_context[i_context_id] = \
                    self._get_categories_by_project(project_key, i_context_id)
        categories_per_context[main_context_id] = categories_per_context[-1]
        project_categories_per_context[main_context_id] = project_categories_per_context[-1]

        return categories_per_context, project_categories_per_context

    def _get_categories_by_project(self, project_key, context_id):
        category_dict = {}
        for category in self.categ.get_categories_by_project(project_key, context_id):
            category_dict[category.category_id] = category
        return category_dict

    def _get_context_name(self, context_key, all_contexts = None):
        if not all_contexts:
            all_contexts = self.categ.get_contexts()

        for c in all_contexts:
            if c.context_id == int(context_key):
                return c.name
        return ""
