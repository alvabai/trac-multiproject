# -*- coding: utf-8 -*-
from trac.admin.api import IAdminPanelProvider
from trac.core import Component, implements
from trac.web.chrome import add_notice, add_warning, add_script, add_stylesheet
from trac.util.translation import _

from multiproject.core.categories import CQDECategoryStore, Category

class CategoryEditorAdminPanel(Component):
    """ Trac component for editing category structure
    """
    implements(IAdminPanelProvider)

    def get_admin_panels(self, req):
        if 'TRAC_ADMIN' in req.perm:
            yield ('general', _('General'), 'categoryeditor', _('Edit categories'))

    def render_admin_panel(self, req, cat, page, path_info):
        req.perm.require("TRAC_ADMIN")
        self.categorystore = CQDECategoryStore()

        data = {}
        if req.method == 'POST':
            if req.args.get('add'):
                self.add_category(req)
            if req.args.get('remove'):
                self.remove_category(req)
            if req.args.get('edit'):
                self.edit_category(req)
            if req.args.get('move'):
                self.move_category_to_new_context(req)
            if req.args.get('merge'):
                self.merge_to_category(req)
            if req.args.get('reposition'):
                self.move_category_to_new_parent(req)

        contexts = self.categorystore.get_contexts()
        context_by_id = {}
        categories_per_context = {}
        for context in contexts:
            context_by_id[context.context_id] = context
            categories_per_context[context.context_id] = \
                self.categorystore.get_all_categories_in_context(context.context_id)
        is_rdf_description = lambda x: x.startswith('http://')

        data['context_by_id'] = context_by_id
        data['categories_per_context'] = categories_per_context
        data['envurl'] = req.base_path
        data['invalid_categories'] = self.categorystore.get_categories_with_invalid_context()
        data['is_rdf_description'] = is_rdf_description
        add_script(req, 'multiproject/js/jquery-ui.js')
        add_script(req, 'multiproject/js/categorization.js')
        add_stylesheet(req, 'multiproject/css/jquery-ui.css')
        return 'admin_categoryeditor.html', data

    def add_category(self, req):
        req.perm.require('TRAC_ADMIN')
        context = req.args.get('context', '').strip()
        category = req.args.get('category', '').strip()
        parent = req.args.get('parent', '').strip()
        license_url = req.args.get('license_url', '').strip()

        if not context or not category:
            return
        if license_url:
            category = category + "#" + license_url

        
        if parent == "NONE" or parent == '':
            parent = None

        try:
            self.categorystore.add_category(category, category, context, parent)
            add_notice(req, _('Category %(what)s has been added.',
                              what=category))
        except Exception as e:
            add_warning(req, _('Category %(what)s cannot be added. ',
                               what=category) + _(str(e)))

    def remove_category(self, req):
        req.perm.require('TRAC_ADMIN')
        category = self._translate_req_to_category(req, 'removed');

        if not category:
            return

        try:
            self.categorystore.remove_category(category.category_id)
            add_notice(req, _('Category has been removed.'))
        except Exception as e:
            add_warning(req, _('Category was not removed. ') + _(str(e)))

    def edit_category(self, req):
        req.perm.require('TRAC_ADMIN')
        category_id = req.args.get('edited_category_id', '')
        if category_id.isdigit():
            category = self.categorystore.get_category_by_id(category_id)
        if not category_id or not category:
            add_warning(req, _('Invalid category id provided.'))
            return
        category_name = req.args.get('edited_category_name', '')
        category_description = req.args.get('edited_category_description', '')
        if len(category_description.split("#")) == 2:
            category_name = category_name + "#" + category_description.split("#")[1]
        if not category_name or not category_description:
            add_warning(req, _('Category name and description cannot be empty. "%s" "%s"'%(category_name, category_description)))
            return

        if category.name == category_name and category.description == category_description:
            add_warning(req, _('Category name and description are already as requested.'))
            return

        try:
            self.categorystore.edit_category(category.category_id, category_name, category_description)
            add_notice(req, _('Category has been edited.'))
        except Exception as e:
            add_warning(req, _('Category was not edited. ') + _(str(e)))


    def move_category_to_new_context(self, req):
        req.perm.require('TRAC_ADMIN')
        new_context = req.args.get('newcontext', '').strip()
        # possible params involved in req: 'moved_category_id' or 'moved_category_name'
        category = self._translate_req_to_category(req, 'moved')

        if not new_context or not category:
            return

        try:
            self.categorystore.move_category_to_root_of_context(category.category_id, new_context)
            add_notice(req, _('Category %(what)s has been moved.',
                              what=category.name))
        except Exception as e:
            add_warning(req, _('Category %(what)s cannot be moved. ',
                               what=category.name) + _(str(e)))

    def move_category_to_new_parent(self, req):
        req.perm.require('TRAC_ADMIN')
        new_context = req.args.get('newcontext', '').strip()
        # possible params involved in req: 'repositioned_category_id' or 'repositioned_category_name'
        category = self._translate_req_to_category(req, 'repositioned')
        root_category =  req.args.get('root_category')
        parent_category_id = None
        parent_category = None
        if not root_category:
            # possible params involved in req: 'new_parent_category_id' or 'new_parent_category_name'
            parent_category = self._translate_req_to_category(req, 'new_parent')
            if parent_category:
                parent_category_id = parent_category.category_id

        if not category or (not root_category and not parent_category):
            add_warning(req, _('Invalid parameters, nothing done. '))
            return

        if root_category:
            try:
                self.categorystore.move_category_to_root_of_context(category.category_id,
                    category.context)
                add_notice(req, _('Category %(what)s has been moved to be root category.',
                    what=category.name))
            except Exception as e:
                add_warning(req, _('Category %(what)s was not moved to be root category. ',
                    what=category.name) + _(str(e)))
        else:
            try:
                self.categorystore.move_category_to_new_parent(category.category_id,
                    parent_category_id)
                add_notice(req, _('Category %(what)s has been moved to parent %(parent)s.',
                    what=category.name, parent=parent_category.name))
            except Exception as e:
                add_warning(req, _('Category %(what)s was not moved to parent %(parent)s. ',
                    what=category.name, parent=parent_category.name) + _(str(e)))

    def merge_to_category(self, req):
        req.perm.require('TRAC_ADMIN')

        # possible params involved in req: target_category_name, target_category_id
        target_category = self._translate_req_to_category(req, 'target')
        # possible params involved in req: merged_category_id, merged_category_name
        merged_category = self._translate_req_to_category(req, 'merged')
        if not target_category or not merged_category:
            add_warning(req, _('Invalid merge category parameters: No corresponding category found.'))
            return

        try:
            self.categorystore.merge_category_to_category(merged_category.category_id,
                target_category.category_id)
            add_notice(req, _('Category %(merged)s has been merged to %(target)s.',
                merged = merged_category.name, target = target_category.name))
        except Exception as e:
            add_warning(req, _('Category %(what)s was not merged. ',
                what=merged_category.name) + _(str(e)))

    def _translate_req_to_category(self, req, prefix):
        """
        :returns: :py:class:`multiproject.core.categories.Category` or None
        """
        category_id = req.args.get(prefix + '_category_id', '').strip()
        category_name = req.args.get(prefix + '_category_name','').strip()
        if category_id.isdigit():
            category = self.categorystore.get_category_by_id(int(category_id))
        else:
            self.log.debug("searching %s with: %s " % (prefix, category_name))
            category = self.categorystore.get_category_by_name(category_name)
        return category
