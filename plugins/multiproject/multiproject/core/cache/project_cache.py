from multiproject.core.configuration import conf
from multiproject.core.exceptions import SingletonExistsException
from memcache import Client
import base64

class ProjectCache(object):
    """ Methods for caching all access control objects
        permissions, authetication and actions
    """
    __instance = None

    def __init__(self):
        if ProjectCache.__instance:
            raise SingletonExistsException()
        self.mc = conf.getMemcachedInstance()
        self.PROJECT_CACHE_TIME = 5 * 60
        self.LIST_CACHE_TIME = 3 * 60

    @staticmethod
    def instance():
        if ProjectCache.__instance is None:
            ProjectCache.__instance = ProjectCache()
        return ProjectCache.__instance

    # Project environment name => id cache
    def getProjectId(self, env_name):
        key = self.__project_name_id_key(env_name)
        try:
            return self.mc.get(key)
        except Client.MemcachedKeyError:
            # Invalid key, eg. with spaces - should not happen unless someone is manipulating requests
            from multiproject.core.configuration import conf
            conf.log.warning('ProjectCache.getProjectId invalid key "%s"' % env_name)
            return None

    def setProjectId(self, env_name, project_id):
        key = self.__project_name_id_key(env_name)
        self.mc.set(key, project_id, self.PROJECT_CACHE_TIME)

    def clearProjectId(self, env_name):
        key = self.__project_name_id_key(env_name)
        self.mc.delete(key)

    # Caching instances of Project class
    def getProject(self, project_id):
        key = self.__project_key(project_id)
        return self.mc.get(key)

    def setProject(self, project):
        key = self.__project_key(project.id)
        self.mc.set(key, project, self.PROJECT_CACHE_TIME)

    def clearProject(self, project_id):
        key = self.__project_key(project_id)
        self.mc.delete(key)

    def get_project_by_env_name(self, env_name):
        key = self.__project_by_env_key(env_name)
        try:
            return self.mc.get(key)
        except Client.MemcachedKeyError:
            # Invalid key, eg. with spaces - should not happen unless someone is manipulating requests
            from multiproject.core.configuration import conf
            conf.log.warning('ProjectCache.getProjectId invalid key "%s"' % env_name)
            return None

    def set_project_by_env_name(self, env_name, project):
        key = self.__project_by_env_key(env_name)
        self.mc.set(key, project, self.PROJECT_CACHE_TIME)

    def clear_project(self, project):
        key_by_env_name = self.__project_by_env_key(project.env_name)
        self.mc.delete(key_by_env_name)
        key_by_id = self.__project_key(project.id)
        self.mc.delete(key_by_id)

    # Caching project counts / category for user
    def get_project_counts_per_category(self, username):
        key = self.__get_project_counts_per_category_key(username)
        return self.mc.get(key)

    def set_project_counts_per_category(self, username, category_count_map):
        key = self.__get_project_counts_per_category_key(username)
        self.mc.set(key, category_count_map, self.PROJECT_CACHE_TIME)

    def clear_project_counts_per_category(self, username):
        key = self.__get_project_counts_per_category_key(username)
        self.mc.delete(key)

    # Keys used for storing project data
    def __project_key(self, project_id):
        key = 'project:' + str(project_id)
        return key.encode('utf-8')

    def __project_name_id_key(self, identifier):
        key = 'project_name_id:' + identifier
        return key.encode('utf-8')

    def __project_by_env_key(self, identifier):
        key = 'project_by_env:' + identifier
        return key.encode('utf-8')

    def __get_project_counts_per_category_key(self, username):
        key = "prj_counts:" + base64.b64encode(username.encode('utf-8'))
        return key.encode('utf-8')
