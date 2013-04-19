from multiproject.core.configuration import conf
from multiproject.core.multiproj_exceptions import SingletonExistsException
import base64

class GroupPermissionCache(object):
    __instance = None

    def __init__(self):
        if GroupPermissionCache.__instance:
            raise SingletonExistsException()
        self.mc = conf.getMemcachedInstance()

        # Cache times are seconds
        self.ID_CACHE_TIME = 15 * 60
        self.PERMISSION_CACHE_TIME = 5 * 60

    @staticmethod
    def instance():
        if GroupPermissionCache.__instance is None:
            GroupPermissionCache.__instance = GroupPermissionCache()
        return GroupPermissionCache.__instance

    # Group id caching
    def get_group_id(self, group_name, trac_environment_id):
        key = self.__group_id_key(group_name, trac_environment_id)
        return self.mc.get(key)

    def set_group_id(self, group_name, trac_environment_id, group_id):
        key = self.__group_id_key(group_name, trac_environment_id)
        self.mc.set(key, group_id, self.ID_CACHE_TIME)

    def clear_group_id(self, group_name, trac_environment_id):
        key = self.__group_id_key(group_name, trac_environment_id)
        self.mc.delete(key)

    # Authentication id caching
    def get_authentication_id(self, authentication_name):
        key = self.__authentication_id_key(authentication_name)
        return self.mc.get(key)

    def set_authentication_id(self, authentication_name, authentication_id):
        key = self.__authentication_id_key(authentication_name)
        self.mc.set(key, authentication_id, self.ID_CACHE_TIME)

    def clear_authentication_id(self, authentication_name):
        key = self.__authentication_id_key(authentication_name)
        self.mc.delete(key)

    # Organization id caching
    def get_organization_id(self, organization_name):
        key = self.__organization_id_key(organization_name)
        return self.mc.get(key)

    def set_organization_id(self, organization_name, organization_id):
        key = self.__organization_id_key(organization_name)
        self.mc.set(key, organization_id, self.ID_CACHE_TIME)

    def clear_organization_id(self, organization_name):
        key = self.__organization_id_key(organization_name)
        self.mc.delete(key)

    # Organization name caching
    def get_organization_name(self, organization_id):
        key = self.__organization_name_key(organization_id)
        return self.mc.get(key)

    def set_organization_name(self, organization_id, organization_name):
        key = self.__organization_name_key(organization_id)
        self.mc.set(key, organization_name, self.ID_CACHE_TIME)

    def clear_organization_name(self, organization_id):
        key = self.__organization_name_key(organization_id)
        self.mc.delete(key)

    # environment ldap group id caching
    def get_trac_environment_ldap_group_id(self, environment_ldap_group_name):
        key = self.__environment_ldap_group_id_key(environment_ldap_group_name)
        return self.mc.get(key)

    def set_trac_environment_ldap_group_id(self, environment_ldap_group_name, environment_ldap_group_id):
        key = self.__environment_ldap_group_id_key(environment_ldap_group_name)
        self.mc.set(key, environment_ldap_group_id, self.ID_CACHE_TIME)

    def clear_trac_environment_ldap_group_id(self, environment_ldap_group_name):
        key = self.__environment_ldap_group_id_key(environment_ldap_group_name)
        self.mc.delete(key)

    # Permission id caching
    def get_permission_id(self, permission_name):
        key = self.__permission_id_key(permission_name)
        return self.mc.get(key)

    def set_permission_id(self, permission_name, permission_id):
        key = self.__permission_id_key(permission_name)
        self.mc.set(key, permission_id, self.ID_CACHE_TIME)

    def clear_permission_id(self, permission_name):
        key = self.__permission_id_key(permission_name)
        self.mc.delete(key)

    # Group template id caching
    def get_template_id(self, template_name):
        key = self.__template_id_key(template_name)
        return self.mc.get(key)

    def set_template_id(self, template_name, template_id):
        key = self.__template_id_key(template_name)
        self.mc.set(key, template_id, self.ID_CACHE_TIME)

    def clear_template_id(self, template_name):
        key = self.__template_id_key(template_name)
        self.mc.delete(key)

    # Authentication method list caching
    def get_authentication_methods(self):
        key = self.__authentication_methods_key()
        return self.mc.get(key)

    def set_authentication_methods(self, methods):
        key = self.__authentication_methods_key()
        self.mc.set(key, methods)

    def clear_authentication_methods(self):
        key = self.__authentication_methods_key()
        self.mc.delete(key)

    # User groups caching / environment (username, groupname) tuples
    def get_user_groups(self, environment_id):
        key = self.__user_groups_key(environment_id)
        return self.mc.get(key)

    def set_user_groups(self, environment_id, user_groups):
        key = self.__user_groups_key(environment_id)
        self.mc.set(key, user_groups, self.PERMISSION_CACHE_TIME)

    def clear_user_groups(self, environment_id):
        key = self.__user_groups_key(environment_id)
        self.mc.delete(key)

    # Organization groups caching / environment (organization name, group name) tuples
    def get_organization_groups(self, environment_id):
        key = self.__organization_groups_key(environment_id)
        return self.mc.get(key)

    def set_organization_groups(self, environment_id, org_groups):
        key = self.__organization_groups_key(environment_id)
        self.mc.set(key, org_groups, self.PERMISSION_CACHE_TIME)

    def clear_organization_groups(self, environment_id):
        key = self.__organization_groups_key(environment_id)
        self.mc.delete(key)

    # environment LDAP group caching
    def get_trac_environment_ldap_groups(self, environment_id):
        key = self.__environment_ldap_groups_key(environment_id)
        return self.mc.get(key)

    def set_trac_environment_ldap_groups(self, environment_id, ldapgroups):
        key = self.__environment_ldap_groups_key(environment_id)
        self.mc.set(key, ldapgroups, self.PERMISSION_CACHE_TIME)

    def clear_trac_environment_ldap_groups(self, environment_id):
        key = self.__environment_ldap_groups_key(environment_id)
        self.mc.delete(key)

    # user LDAP group caching
    def get_user_ldap_groups(self, username):
        key = self.__user_ldap_groups_key(username)
        return self.mc.get(key)

    def set_user_ldap_groups(self, username, ldapgroups):
        key = self.__user_ldap_groups_key(username)
        self.mc.set(key, ldapgroups, self.PERMISSION_CACHE_TIME)

    def clear_user_ldap_groups(self, username):
        key = self.__user_ldap_groups_key(username)
        self.mc.delete(key)

    # LDAP group user caching
    def get_ldap_group_users(self, groupname):
        key = self.__ldap_group_users_key(groupname)
        return self.mc.get(key)

    def set_ldap_group_users(self, groupname, users):
        key = self.__ldap_group_users_key(groupname)
        self.mc.set(key, users, self.PERMISSION_CACHE_TIME)

    def clear_ldap_group_users(self, groupname):
        key = self.__ldap_group_users_key(groupname)
        self.mc.delete(key)

    # Permissions in group / environment (groupname, permname) tuples
    def get_group_perms(self, environment_id):
        key = self.__group_perms_key(environment_id)
        return self.mc.get(key)

    def set_group_perms(self, environment_id, group_perms):
        key = self.__group_perms_key(environment_id)
        return self.mc.set(key, group_perms, self.PERMISSION_CACHE_TIME)

    def clear_group_perms(self, environment_id):
        key = self.__group_perms_key(environment_id)
        return self.mc.delete(key)

    # List of superusers
    def get_superusers(self):
        key = self.__superuser_key()
        return self.mc.get(key)

    def set_superusers(self, superusers):
        key = self.__superuser_key()
        return self.mc.set(key, superusers, self.PERMISSION_CACHE_TIME)

    def clear_superusers(self):
        key = self.__superuser_key()
        return self.mc.delete(key)

    # Keys generators for caching objects
    # Strings are base64 encoded to make sure there are no illegal chars
    def __group_id_key(self, group_name, environment_key):
        key = 'gid:' + str(environment_key) + ":" + base64.b64encode(group_name)
        return key.encode('utf-8')

    def __authentication_id_key(self, authentication_name):
        key = 'auth_id:' + base64.b64encode(authentication_name)
        return key.encode('utf-8')

    def __organization_id_key(self, organization_name):
        key = 'org_id:' + base64.b64encode(organization_name)
        return key.encode('utf-8')

    def __organization_name_key(self, organization_id):
        key = 'org_name:' + str(organization_id)
        return key.encode('utf-8')

    def __environment_ldap_group_id_key(self, environment_ldap_group_name):
        key = 'environment_ldap_group_id:' + base64.b64encode(environment_ldap_group_name)
        return key.encode('utf-8')

    def __permission_id_key(self, permission_name):
        key = 'perm_id:' + base64.b64encode(permission_name)
        return key.encode('utf-8')

    def __template_id_key(self, template_name):
        key = 'templ_id:' + base64.b64encode(template_name)
        return key.encode('utf-8')

    def __authentication_methods_key(self):
        key = 'authen_methd_list'
        return key.encode('utf-8')

    def __user_groups_key(self, environment_id):
        key = 'user_groups:' + str(environment_id)
        return key.encode('utf-8')

    def __organization_groups_key(self, environment_id):
        key = 'org_group:' + str(environment_id)
        return key.encode('utf-8')

    def __environment_ldap_groups_key(self, environment_id):
        key = 'environment_ldap_groups:' + str(environment_id)
        return key.encode('utf-8')

    def __user_ldap_groups_key(self, username):
        key = 'user_ldap_groups:' + base64.b64encode(username)
        return key.encode('utf-8')

    def __ldap_group_users_key(self, groupname):
        key = 'ldap_group_users:' + base64.b64encode(groupname)
        return key.encode('utf-8')

    def __group_perms_key(self, environment_id):
        key = 'group_perms:' + str(environment_id)

        return key.encode('utf-8')

    def __superuser_key(self):
        return 'super_users'.encode('utf-8')


class AuthenticationCache(object):
    """ Methods for caching all access control objects
        permissions, authetication and actions
    """
    __instance = None

    def __init__(self):
        if AuthenticationCache.__instance:
            raise SingletonExistsException()
        self.mc = conf.getMemcachedInstance()
        self.AUTHENTICATION_CACHE_TIME = 60

    @staticmethod
    def instance():
        if AuthenticationCache.__instance is None:
            AuthenticationCache.__instance = AuthenticationCache()
        return AuthenticationCache.__instance

    # Authentication caching
    def getAuthentication(self, username, sha1_pw):
        key = self.__auth_key(username, sha1_pw)
        return self.mc.get(key)

    def setAuthentication(self, username, sha1_pw, is_authentic):
        key = self.__auth_key(username, sha1_pw)
        self.mc.set(key, is_authentic, self.AUTHENTICATION_CACHE_TIME)

    def clearAuthentication(self, username, sha1_pw):
        key = self.__auth_key(username, sha1_pw)
        self.mc.delete(key)

    def __auth_key(self, username, sha1_pw):
        key = 'auth:' + base64.b64encode(username) + ':' + sha1_pw
        return key.encode('utf-8')
