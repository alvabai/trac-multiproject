
from multiproject.core.configuration import conf
from multiproject.core.db import admin_query, admin_transaction, safe_int, safe_string
from multiproject.core.cache.category_cache import CategoryCache
from trac.util.translation import _


class CQDECategoryStore(object):
    """ DAO for contexts and categories
    """

    def __init__(self):
        # TODO cache some database results
        #self.__cache = CategoryCache.instance()
        pass

    def get_contexts(self):
        """ Returns a list of Context class instances
        """
        contexts = []
        with admin_query() as cursor:
            try:
                query = "SELECT * FROM contexts"
                cursor.execute(query)

                for row in cursor:
                    context = Context.from_sql_row(row)
                    contexts.append(context)
            except:
                conf.log.exception("Failed to read contexts from database.")

        return contexts

    def get_context(self, context_name):
        """ Returns a context object by name
        """
        context = None
        with admin_query() as cursor:
            try:
                query = "SELECT * FROM contexts WHERE context_name = %s"
                cursor.execute(query, context_name)
                row = cursor.fetchone()
                if row:
                    context = Context.from_sql_row(row)
            except:
                conf.log.exception("Exception. Was not able to read context('%s') from database." % str(context_name))

        return context

    def get_context_by_id(self, context_id):
        """ Returns a context object by id
        """
        context_id = safe_int(context_id)
        context = None
        with admin_query() as cursor:
            try:
                cursor.execute("SELECT * FROM contexts WHERE context_id = %s", context_id)
                row = cursor.fetchone()
                if row:
                    context = Context.from_sql_row(row)
            except:
                conf.log.exception("Exception. Was not able to read context(%d) from database.", context_id)

        return context

    def get_categories(self, context_id):
        """ Returns a list of Category class instances


        ### Used only in xmlrpc
        """
        context_id = safe_int(context_id) or 0

        categories = []
        with admin_query() as cursor:
            try:
                query = "SELECT * FROM categories WHERE context_id = %d" % context_id
                cursor.execute(query)

                for row in cursor:
                    cat = Category.from_sql_row(row)
                    categories.append(cat)
            except:
                conf.log.exception(
                    "Was not able to read categories of context('%s') from database." % str(context_id))

        return sorted(categories, key=lambda x: x.name)

    def get_category_by_name(self, name):
        """ Returns a Category
        """
        category = None
        with admin_query() as cursor:
            try:
                query = "SELECT * FROM categories WHERE category_name = %s"
                cursor.execute(query, name)
                row = cursor.fetchone()
                if row:
                    category = Category.from_sql_row(row)
            except:
                conf.log.exception("Exception. Query failed when searching category('%s') from database." % str(name))

        return category

    def get_category_by_id(self, category_id):
        """
        :returns: Category
        """
        category = None
        category_id = safe_int(category_id)

        with admin_query() as cursor:
            try:
                cursor.execute("SELECT * FROM categories WHERE category_id = %s", category_id)
                row = cursor.fetchone()
                if row:
                    category = Category.from_sql_row(row)
            except:
                conf.log.exception(
                    "Exception. Query failed when searching category name by category_id('%s')." % str(category_id))

        return category

    def get_category_by_name_filter(self, name_filter, limit=None, context_ids=None):
        """
        Returns a list of categories matching filter.
        If context_ids are provided, search is restricted to the corresponding contexts.

        :returns: list of matched Categories
        """
        default_limit = 100

        if name_filter:
            name_filter = name_filter.lower()
        and_context_ids = ''
        if context_ids and len(context_ids) < 20:
            and_context_ids = ' AND context_id IN ({0}) '.format(
                ','.join([str(safe_int(id)) for id in context_ids])
            )

        limit = safe_int(limit) or default_limit

        query = """ SELECT * FROM categories
                    WHERE LOWER(category_name) LIKE '%{0}%'
                        {1}
                    LIMIT {2}""".format(safe_string(name_filter), and_context_ids, limit)

        categories = []
        conf.log.debug("Querying categories with query: %s", query)
        try:
            with admin_query() as cursor:
                cursor.execute(query)

                for row in cursor:
                    categories.append(Category.from_sql_row(row))
        except Exception:
            conf.log.exception(
                "Exception. Query failed when searching category by name_filter('%s') from database." % str(name_filter))

        return categories

    def get_all_categories(self):
        """
        :returns:
            A flat dictionary of all categories with category id as index::

                int category_id => Category category

        .. Note::

            All child categories are populated so that it's easy to
            start walking from any category through children.
            Also, the root categories (not child categories) are ordered by
            category_name.

        """
        # Try from cache
        cache = CategoryCache.instance()
        categories = cache.getAllCategories()
        if categories:
            return categories

        # Try from db
        query = "SELECT * FROM categories ORDER BY category_name"

        # First pass, Read all categories to hash id => categories
        categories = {}
        with admin_query() as cursor:
            try:
                cursor.execute(query)
                for row in cursor:
                    cat = Category.from_sql_row(row)
                    categories[cat.category_id] = cat
            except:
                conf.log.exception("Failed on building category tree")

        # Second pass, create hierarchy
        for id, category in categories.items():
            # Add category as a parent category's child category
            if category.parent:
                try:
                    categories[category.parent].add_child(category)
                except:
                    conf.log.warning("Inconsistent data. No parent category %d found" % category.parent)

        if categories:
            cache.setAllCategories(categories)

        return categories

    def get_all_categories_in_context(self, context_id):
        """
        :returns:
            A flat dictionary of categories in context with category id as index::

                int category_id => Category category

        .. Note::

            All child categories are populated so that it's easy to
            start walking from any category through children.
            Also, the root categories (not child categories) are ordered by
            category_name.

        """
        # Try from cache
        cache = CategoryCache.instance()
        categories = cache.get_categories_in_context(context_id)
        if categories:
            return categories

        # Try from db
        query = "SELECT * FROM categories WHERE context_id = %s ORDER BY category_name"

        # First pass, Read all categories to hash id => categories
        categories = {}
        with admin_query() as cursor:
            try:
                cursor.execute(query, context_id)
                for row in cursor:
                    cat = Category.from_sql_row(row)
                    categories[cat.category_id] = cat
            except:
                conf.log.exception("Failed on building category tree")

        # Second pass, create hierarchy
        for id, category in categories.items():
            # Add category as a parent category's child category
            if category.parent:
                try:
                    categories[category.parent].add_child(category)
                except:
                    conf.log.warning("Inconsistent data. No parent category %d found" % category.parent)

        if categories:
            cache.set_categories_in_context(categories, context_id)

        return categories

    def add_category(self, name, description, context, parent):
        """
        Add a new category.
        Raises Exception on error.
        """
        parent = safe_int(parent)
        name = str(name)
        context = safe_int(context)

        query = ("INSERT INTO `categories` (`category_name`, `description`, `parent_id`, `context_id`)"
                " VALUES(%s, %s, %s, %s);")
        existing_category = self.get_category_by_name(name)
        if existing_category:
            raise Exception("A category with the same name already exists.")

        try:
            with admin_transaction() as cursor:
                cursor.execute(query, (name, description, parent, context))
        except:
            conf.log.exception("Error when adding category.")
            raise Exception("Error when adding category.")
        finally:
            cache = CategoryCache.instance()
            cache.clearAllCategories()

    def remove_category(self, category_id):
        """
        Remove a category.
        Raises Exception on error.
        """
        category_id = safe_int(category_id)

        if not category_id:
            raise Exception("Invalid category provided.")

        query = "DELETE FROM categories WHERE category_id = %s"

        with admin_transaction() as cursor:
            try:
                cursor.execute(query, category_id)
            except:
                conf.log.exception("Failed to delete category %d" % category_id)
                raise Exception("Error when removing category.")
            finally:
                cache = CategoryCache.instance()
                cache.clearAllCategories()

    def edit_category(self, category_id, category_name, category_description):
        """
        Edits a category name and description.
        Raises Exception on error.
        """
        category_id = safe_int(category_id)

        if not category_id:
            raise Exception("Invalid category provided.")
        existing_category = self.get_category_by_name(category_name)
        if existing_category and existing_category.category_id != category_id:
            raise Exception("A category with the same name already exists.")

        try:
            with admin_transaction() as cursor:
                cursor.execute("UPDATE `categories`"
                               "   SET `category_name` = %s, `description` = %s "
                               " WHERE `category_id` = %s", (category_name, category_description, category_id))
        except:
            conf.log.exception("Failed to edit category %d" % category_id)
            raise Exception("Error when editing category.")
        finally:
            cache = CategoryCache.instance()
            cache.clearAllCategories()

    def move_category_to_root_of_context(self, category_id, new_context_id, all_categories = None):
        """
        Move a category (and its child categories) to new context (if not already there)
        and set the parent category to null.

        :param int category: category moved
        :param int new_context_id: new context
        :param all_categories: equal to self.get_all_categories()
        """

        if not all_categories:
            all_categories = self.get_all_categories()
        # all_categories comes from database

        # Validate new_context_id
        new_context_id = safe_int(new_context_id)
        context = self.get_context_by_id(new_context_id)
        if not context:
            raise Exception("Context was invalid.")

        # Validate category_id
        category_id = safe_int(category_id)
        if not all_categories.has_key(category_id):
            raise Exception("Category not found.")
        category = all_categories[category_id]

        must_change_context = True
        if category.context == new_context_id:
            if category.parent is None:
                raise Exception("Category is already a root category and has the required context.")
            else:
                must_change_context = False

        change_context_query = self._change_context_query(category_id, all_categories)

        try:
            with admin_transaction() as cursor:
                if must_change_context:
                    cursor.execute(change_context_query,
                        new_context_id)
                cursor.execute("UPDATE `categories` "
                               "    SET `parent_id` = NULL "
                               "  WHERE `category_id` = %s ", category_id)
        except:
            conf.log.exception("Failed to move category %s into context %d",
                category.name, new_context_id)
            raise Exception("Error when doing database transaction.")
        finally:
            cache = CategoryCache.instance()
            cache.clearAllCategories()

    def move_category_to_new_parent(self, category_id, new_parent_id, all_categories = None):
        """
        Move a category (and its child categories) to new context,
        possibly setting the parent category to null.

        :param int category: category moved
        :param int new_parent_id: new parent id
        :param all_categories: equal to self.get_all_categories()
        """
        if not all_categories:
            all_categories = self.get_all_categories()
        # all_categories comes from database

        # Validate category_id
        category_id = safe_int(category_id)
        if not all_categories.has_key(category_id):
            raise Exception("No repositioned category found.")
        category = all_categories[category_id]
        parent_category = None
        # Validate new_parent_id
        new_parent_id = safe_int(new_parent_id)
        if not all_categories.has_key(new_parent_id):
            raise Exception("No new parent category found.")
        parent_category = all_categories[new_parent_id]

        must_update_context = False
        if category.parent == new_parent_id and parent_category.context == category.context:
            raise Exception("Category's context and parent are already as required.")

        # Prevent making eternal loops.
        is_sub_category = self._is_sub_category_or_self(new_parent_id, category_id, all_categories)

        if is_sub_category:
            raise Exception("Cannot move category under its sub category.")

        change_context_query = ''
        if parent_category.context != category.context:
            must_update_context = True
            change_context_query = self._change_context_query(category_id, all_categories)

        try:
            with admin_transaction() as cursor:
                if must_update_context:
                    cursor.execute(change_context_query, parent_category.context)
                cursor.execute("UPDATE `categories` "
                               "    SET `parent_id` = %s "
                               "  WHERE `category_id` = %s ", (new_parent_id, category_id))
        except Exception as e:
            conf.log.exception("Failed to change parent category of %s to be %d: %s",
                category.name, new_parent_id, e)
            raise Exception("Error when updating parent.")
        finally:
            cache = CategoryCache.instance()
            cache.clearAllCategories()

    def _change_context_query(self, category_id, all_categories = None):
        """
        Returns a string like "UPDATE categories SET context_id = %s WHERE ... " for
        updating the contexts of the category and its child categories.

        If category doesn't exist, returns "".

        :param category_id: category id in question, must be valid category id!
        :param all_categories: equal to self.get_all_categories()
        :returns: sql_query
        """
        category_id = safe_int(category_id)
        if not all_categories:
            all_categories = self.get_all_categories()
        # all_categories comes from database
        format_id = lambda id_as_int: str(int(id_as_int))

        if not category_id or not all_categories.has_key(category_id):
            return "", _("Category was not found")
        category = all_categories[category_id]

        # Get children ids recursively, since their contexts must be updated also
        recursive_children_ids = [format_id(category.category_id)]
        not_handled_categories = category.children

        number_of_all_categories = len(all_categories)
        categories_handled = 0

        while len(not_handled_categories) > 0:
            new_not_handled_categories = []
            for category in not_handled_categories:
                # Filter and map here, if needed
                recursive_children_ids.append(format_id(category.category_id))
                categories_handled += 1
                if categories_handled > number_of_all_categories:
                    self.log.warning("Error in category data: Eternal loop when trying to find children of %s" % category_id)
                    raise Exception("Inconsistent data: there was eternal recursion.")
                new_not_handled_categories.extend(category.children)
            not_handled_categories = new_not_handled_categories

        query = ("UPDATE `categories` "
                 "    SET `context_id` = %%s "
                 "  WHERE `category_id` IN (%s) " % (', '.join(recursive_children_ids)))
        return query

    def _is_sub_category_or_self(self, category_id, parent_category_id, all_categories = None):
        """
        Returns True if category_id is the same or sub category of the parent_category_id.
        Returns True when parent_category cannot be put as a child for category_id.
        Raises exception on error.

        .. Note:: Returns true also when category_id == parent_category_id

        :param int category_id: category id, must be valid category id!
        :param int parent_category_id: expected parent category id, must be valid category id!
        :param all_categories: equal to self.get_all_categories()
        :returns: bool is category sub category of parent category or the same
        """
        category_id = safe_int(category_id)
        parent_category_id = safe_int(parent_category_id)
        if category_id == parent_category_id:
            return True
        if not all_categories:
            all_categories = self.get_all_categories()
        category = all_categories[category_id]
        if not category.parent:
            return False

        parent_category = all_categories[category.parent]
        number_of_all_categories = len(all_categories)
        categories_handled = 0
        result = False
        while parent_category:
            # Success condition
            if parent_category.category_id == parent_category_id:
                result = True
                break
            categories_handled += 1
            # Error conditions
            if parent_category.category_id == category_id:
                self.log.warning("Error in category data: Category %s is a sub category for itself" % category_id)
                raise Exception("Category is a sub category for itself")
            if categories_handled > number_of_all_categories:
                self.log.warning("Error in category data: Eternal loop when trying to find parents of %s" % category_id)
                raise Exception("Category is a sub category for itself")
            # Break loop condition
            if not parent_category.parent:
                break
            parent_category = all_categories[parent_category.parent]
        return result

    def get_all_project_categories(self, project_key, ordered = False):
        """ Returns a list of all project categories of the project.
        """
        cc = CategoryCache.instance()

        project_key = safe_int(project_key)

        categories = cc.getProjectCategories(project_key)
        if categories:
            return categories

        order_by = ''
        if ordered:
            order_by = 'ORDER BY categories.context_id, categories.category_name'

        query = """
            SELECT categories.* FROM categories
            INNER JOIN project_categories
                ON project_categories.category_key = categories.category_id
            WHERE project_categories.project_key = %s
            {order_by}""".format(order_by=order_by)

        categories = []
        with admin_query() as cursor:
            try:
                cursor.execute(query, (project_key,))
                for row in cursor:
                    cat = Category.from_sql_row(row)
                    categories.append(cat)
                if len(categories) > 0:
                    cc.setProjectCategories(project_key, categories)
            except:
                conf.log.exception("Exception. Query failed when searching project categories. Query('%s')." %
                                   str(query))

        return categories

    def get_nonbrowsable_context_ids(self):
        """ Return a list of those contexts that are not seen as categories
            by user but as a metadata related with project.
            Like Natural language, License, or Development status.
        """
        cntx_in = ', '.join(["'%s'" % safe_string(ctx) for ctx in conf.non_browsable_contexts])

        query = "SELECT context_id FROM contexts WHERE context_name IN (%s)" % cntx_in

        cntxts = []
        with admin_query() as cursor:
            try:
                cursor.execute(query)
                for row in cursor:
                    cntxts.append(row[0])
            except:
                conf.log.exception("Getting non-browsable context id's failed with query '%s'" % query)

        return cntxts

    def bind_category_project(self, project_key, category_key):
        """ Sets project to belong into given category
        """
        query = ("INSERT INTO project_categories (project_key, category_key) VALUES(%d, %d)" %
                 (safe_int(project_key), safe_int(category_key)))
        try:
            with admin_transaction() as cursor:
                cursor.execute(query)
        except:
            conf.log.exception("Failed to bind project %s into category %s" % (category_key, project_key))
            return False

        return True

    def unbind_category_project(self, project_key, category_key):
        """ Sets project NOT to belong into given category
        """
        params = (safe_int(project_key), safe_int(category_key))
        query = "DELETE FROM project_categories "
        query += "WHERE project_key = %d AND category_key = %d" % params

        try:
            with admin_transaction() as cursor:
                cursor.execute(query)
        except:
            conf.log.exception("Failed to unbind category %s from project %s" % (category_key, project_key))
            return False

        return True

    def merge_category_to_category(self, category_id, target_category_id, all_categories = None):
        """
        Updates projects pointing to category to use target_category,
        and removes category. Updates also contexts of category and its sub categories.
        Raises exception on error.
        """
        if not all_categories:
            all_categories = self.get_all_categories()
            # all_categories comes from database

        # Validate category_id
        category_id = safe_int(category_id)
        if not all_categories.has_key(category_id):
            raise Exception("Invalid merged category")
        category = all_categories[category_id]
        # Validate target_category_id
        target_category_id = safe_int(target_category_id)
        if not all_categories.has_key(target_category_id):
            raise Exception("Invalid target category")
        target_category = all_categories[target_category_id]
        # If the categories are the same, already fixed.
        if category_id == target_category_id:
            raise Exception("Two same categories given.")

        # Prevent making eternal loops by checking that
        # target category is not sub category of merged category.
        is_sub_category = self._is_sub_category_or_self(target_category_id,
            category_id, all_categories)
        if is_sub_category:
            raise Exception("Cannot merge category to sub category.")

        must_update_context = False
        change_context_query = ''
        # Check whether to update contexts
        if target_category.context != category.context:
            must_update_context = True
            change_context_query = self._change_context_query(category_id, all_categories)

        get_project_ids_with_both_categories = (""
        " SELECT `project_key` FROM `project_categories` pk1 "
        "  WHERE pk1.`category_key` = %s "
        "    AND EXISTS (SELECT pk2.`project_key` FROM `project_categories` pk2 "
        "                 WHERE pk1.`project_key` = pk2.`project_key` AND pk2.`category_key` = %s) ")

        update_project_categories =   (" UPDATE `project_categories` "
                                        "    SET `category_key` = %(target_category_id)s "
                                        "  WHERE `category_key` = %(category_id)s "
                                        "    AND `project_key` NOT IN (%(project_ids)s)")

        update_sub_category_parents = ("UPDATE `categories` "
                                       "   SET `parent_id` = %(target_category_id)s "
                                       " WHERE `parent_id` = %(category_id)s ")

        try:
            with admin_transaction() as cursor:
                # Get projects which have both target and merged categories
                cursor.execute(get_project_ids_with_both_categories, (category_id, target_category_id))
                ids = []
                for row in cursor:
                    ids.append(str(row[0]))

                # Update existing projects to use target_category
                cursor.execute(update_project_categories,
                        {'target_category_id' : target_category_id, 'category_id' : category_id,
                         'project_ids' : (', '.join(ids))})
                # Update the parent of child categories
                cursor.execute(update_sub_category_parents,
                        {'target_category_id' : target_category_id, 'category_id' : category_id})
                # Update the context of sub categories
                if must_update_context:
                    cursor.execute(change_context_query,
                        target_category.context)
                cursor.execute("DELETE FROM `categories` WHERE `category_id` = %s ", category_id)
        except Exception as e:
            conf.log.exception("Failed to merge category '%s' to '%s'" % (str(category.name), str(target_category.name)))
            raise Exception("Error when merging categories.")
        finally:
            cache = CategoryCache.instance()
            cache.clearAllCategories()

    def get_categories_by_project(self, project_key, context_id):
        """
        Searches categories belonging in project
        :returns: A list of categories
        """

        and_context_id = ''
        if context_id:
            and_context_id = 'AND cat.context_id = %s'
        query = """SELECT cat.* FROM categories AS cat
                        INNER JOIN project_categories AS pc ON pc.category_key = cat.category_id
                        WHERE pc.project_key = %s {and_context_id}""".format(and_context_id=and_context_id)

        category_list = []
        with admin_query() as cursor:
            try:
                if context_id:
                    cursor.execute(query, (project_key, context_id))
                else:
                    cursor.execute(query, project_key)

                for row in cursor:
                    category_list.append(Category.from_sql_row(row))
            except:
                conf.log.exception("Exception. Failed searching project categories. Query('%s'), project_key %d." %
                                   (str(query), project_key))

        return category_list

    def get_categories_with_invalid_context(self):
        """
        Gets category ids of categories whose parent has different contexts.

        The category editing administration needs this.
        """
        query = ("SELECT cat.*, p_cat.* FROM `categories` as cat, `categories` as p_cat "
                 " WHERE cat.`parent_id` = p_cat.`category_id` "
                 " AND cat.`context_id` <> p_cat.`context_id`")
        data = []
        with admin_query() as cursor:
            try:
                cursor.execute(query)
                for row in cursor:
                    category = Category.from_sql_row(row)
                    parent_category = Category.from_sql_row(row[5:])
                    data.append((category,parent_category))
            except:
                conf.log.exception(
                    "Exception. Query failed when searching categories with invalid contexts. Query('%s')." % str(query))
        return data


class Category(object):
    """ Class for database Category entities
    """

    def __init__(self):
        self.category_id = None
        self.name = None
        self.description = None
        self.parent = None # TODO: rename parent with parent_id
        self.context = None # TODO: rename context with context_id
        self.children = []

    @staticmethod
    def from_sql_row(row):
        """ Static factory method
        """
        cat = Category()
        cat.category_id = row[0]
        cat.name = row[1]
        cat.description = row[2]
        cat.parent = row[3]
        cat.context = row[4]
        return cat

    def __repr__(self):
        return "<Category:" + str(self.category_id) + ":" + str(self.name) + ">"

    def add_child(self, category):
        """ Adds category to object not into database
        """
        self.children.append(category)

    def has_children(self):
        """ Tells if category has children
        """
        return len(self.children) > 0

    def copy_without_children(self):
        cat = Category()
        cat.category_id = self.category_id
        cat.name = self.name
        cat.description = self.description
        cat.parent = self.parent
        cat.context = self.context
        # cat.children = [] by __init__
        return cat

class Context(object):
    """
    .. py:class:: Context

        Class for database Context entities

    .. py:attribute:: summary_name

        Text shown in the summary page, instead of the context.name.
        If summary_name is '', context's categories are combined to one list.
        Maybe short_name would be better name.

    .. py:attribute:: explore_projects_visibility

        Controls how contexts are grouped in view.
        In future, might change to 'is_grouped' or some integer denoting the group.

    .. py:attribute:: admin_type

        More or less a hint of what kind of dat (list, tree, ..) the contexts consists of.
        Currently, this holds also similar data as the explore_projects_visibility, which might
        change in the future, when this almost duplicate data is removed.

    .. py:attribute:: edit_type

        Controls how the normal users are able to edit categories.
        With current implementation, a flag user_addable with values 0 or 1 would be better.

    """

    # Subject to change, this is why we use constants
    EDIT_TYPE_NONE = 'none'
    EDIT_TYPE_ADD = 'add'
    ADMIN_TYPE_LIST = 'list'
    ADMIN_TYPE_MAIN = 'main'
    ADMIN_TYPE_AUTOCOMPLETE = 'autocomplete'
    ADMIN_TYPE_COMBINED = 'combined'
    ADMIN_TYPE_LIST = 'list'
    ADMIN_TYPE_SELECT_BOX = 'select_box'
    ADMIN_TYPE_TREE = 'tree'
    EXPLORE_PROJECT_TYPE_COMBINED = 'combined'
    EXPLORE_PROJECT_TYPE_SEPARATE = 'separate'

    def __init__(self):
        self.context_id = None
        self.name = None

        # Not shown to user. Could be dropped?
        self.description = None

        # TODO: is this really needed? If yes, rename to short_name
        self.summary_name = None

        # TODO: currently, "is_grouped" would be more appropriate name, with values 0 or 1
        self.explore_projects_visibility = self.EXPLORE_PROJECT_TYPE_SEPARATE

        # TODO: rename to context_type, with values 'list', 'tree', 'select_box', 'not_shown'
        # and implement so that "if is_grouped { not_shown: -> 'autocomplete', else: 'combined' }.
        # If context is combined into other context, the other context's context_type "overrides"
        # context's context_type, unless the context's context_type is 'not_shown'.
        self.admin_type = self.ADMIN_TYPE_TREE

        # TODO: currently, "user_addable" would be more appropriate name, with values 0 or 1
        self.edit_type = self.EDIT_TYPE_NONE

        self.children = []

    @staticmethod
    def from_sql_row(row):
        """ Static factory method
        """
        context = Context()
        context.context_id = row[0]
        context.name = row[1]
        context.description = row[2]
        context.summary_name = row[3]
        context.explore_projects_visibility = row[4]
        context.admin_type = row[5]
        context.edit_type = row[6]
        return context

    def __repr__(self):
        return "<Context:" + str(self.context_id) + ":" + str(self.name) + ">"

    def add_child(self, category):
        """ Add direct child in the context. Will not add into database.
        """
        self.children.append(category)

    def has_children(self):
        """ Tells if category has children
        """
        return len(self.children) > 0
