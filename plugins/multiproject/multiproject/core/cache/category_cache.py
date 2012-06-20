from multiproject.core.configuration import conf
from multiproject.core.exceptions import SingletonExistsException

class CategoryCache(object):
    """ Methods for caching all access control objects
        permissions, authetication and actions
    """
    __instance = None

    def __init__(self):
        if CategoryCache.__instance:
            raise SingletonExistsException()
        self.mc = conf.getMemcachedInstance()
        self.CATEGORY_CACHE_TIME = 5 * 60

    @staticmethod
    def instance():
        if CategoryCache.__instance is None:
            CategoryCache.__instance = CategoryCache()
        return CategoryCache.__instance

    # Caching instances of Project class
    def getProjectCategories(self, project_id):
        key = self.__project_categories_key(project_id)
        return self.mc.get(key)

    def setProjectCategories(self, project_id, categories):
        key = self.__project_categories_key(project_id)
        self.mc.set(key, categories, self.CATEGORY_CACHE_TIME)

    def clearProjectCategories(self, project_id):
        key = self.__project_categories_key(project_id)
        self.mc.delete(key)

    # Caching all categories list for CQDECategoryStore.get_all_categories
    def getAllCategories(self):
        key = self.__all_categories_key()
        return self.mc.get(key)

    def setAllCategories(self, categories):
        key = self.__all_categories_key()
        self.mc.set(key, categories, self.CATEGORY_CACHE_TIME)

    def clearAllCategories(self):
        key = self.__all_categories_key()
        self.mc.delete(key)

    # Caching all categories list for CQDECategoryStore.get_all_categories
    def get_categories_in_context(self, context_id):
        key = self.__categories_in_context_key(context_id)
        return self.mc.get(key)

    def set_categories_in_context(self, categories, context_id):
        key = self.__categories_in_context_key(context_id)
        self.mc.set(key, categories, self.CATEGORY_CACHE_TIME)

    def clear_categories_in_context(self, context_id):
        key = self.__categories_in_context_key(context_id)
        self.mc.delete(key)

    def __project_categories_key(self, project_id):
        key = 'prj_cats_:' + str(project_id)
        return key.encode('utf-8')

    def __all_categories_key(self):
        key = 'all_cats:'
        return key.encode('utf-8')

    def __categories_in_context_key(self, context_id):
        key = 'cats_in_context:' + str(int(context_id))
        return key.encode('utf-8')
