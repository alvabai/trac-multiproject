from multiproject.core.cache.permission_cache import AuthenticationCache, GroupPermissionCache
from multiproject.core.test.cqdetestcase import CQDETestCase

class PermissionCacheTestCase(CQDETestCase):
    def setUp(self):
        self.cache = GroupPermissionCache.instance()

    def tearDown(self):
        pass

    # Group id caching
    def testGroupId(self):
        # Init test
        self.cache.clear_group_id('test_group_name', 478)
        self.assertEquals(self.cache.get_group_id('test_group_name', 478), None)

        # Set test
        self.cache.set_group_id('test_group_name', 478, 123454321)
        self.assertEquals(self.cache.get_group_id('test_group_name', 478), 123454321)

        # Clear test
        self.cache.clear_group_id('test_group_name', 478)
        self.assertEquals(self.cache.get_group_id('test_group_name', 478), None)

    # Group id caching
    def testOrganizationId(self):
        # Init test
        self.cache.clear_organization_id('Test Inc. Corp.')
        self.assertEquals(self.cache.get_organization_id('Test Inc. Corp.'), None)

        # Set test
        self.cache.set_organization_id('Test Inc. Corp.', 358634)
        self.assertEquals(self.cache.get_organization_id('Test Inc. Corp.'), 358634)

        # Clear test
        self.cache.clear_organization_id('Test Inc. Corp.')
        self.assertEquals(self.cache.get_organization_id('Test Inc. Corp.'), None)

    def testPermissionId(self):
        # Init test
        self.cache.clear_permission_id('DO_THAT')
        self.assertEquals(self.cache.get_permission_id('DO_THAT'), None)

        # Set test
        self.cache.set_permission_id('DO_THAT', 139)
        self.assertEquals(self.cache.get_permission_id('DO_THAT'), 139)

        # Clear test
        self.cache.clear_permission_id('DO_THAT')
        self.assertEquals(self.cache.get_permission_id('DO_THAT'), None)

    def testTemplateId(self):
        # Init test
        self.cache.clear_template_id('GENERAL PURPOSE')
        self.assertEquals(self.cache.get_template_id('GENERAL PURPOSE'), None)

        # Set test
        self.cache.set_template_id('GENERAL PURPOSE', 12)
        self.assertEquals(self.cache.get_template_id('GENERAL PURPOSE'), 12)

        # Clear test
        self.cache.clear_template_id('GENERAL PURPOSE')
        self.assertEquals(self.cache.get_template_id('GENERAL PURPOSE'), None)

    def testAuthenticationMethods(self):
        # Init test
        self.cache.clear_authentication_methods()
        self.assertEquals(self.cache.get_authentication_methods(), None)

        # Set test
        self.cache.set_authentication_methods(['Local users', 'LDAP users'])
        self.assertEquals(self.cache.get_authentication_methods(), ['Local users', 'LDAP users'])

        # Clear test
        self.cache.clear_authentication_methods()
        self.assertEquals(self.cache.get_authentication_methods(), None)

    def testUserGroups(self):
        # Init test
        self.cache.clear_user_groups(36324)
        self.assertEquals(self.cache.get_user_groups(36324), None)

        # Set test
        self.cache.set_user_groups(36324, [('username', 'groupname'),('user2name', 'group2name')])
        self.assertEquals(self.cache.get_user_groups(36324), [('username', 'groupname'),('user2name', 'group2name')])

        # Clear test
        self.cache.clear_user_groups(36324)
        self.assertEquals(self.cache.get_user_groups(36324), None)

    def testOrganizationGroups(self):
        # Init test
        self.cache.clear_organization_groups(234567)
        self.assertEquals(self.cache.get_organization_groups(234567), None)

        # Set test
        self.cache.set_organization_groups(234567, [('orgname', 'groupname'),('org2name', 'group2name')])
        self.assertEquals(self.cache.get_organization_groups(234567), [('orgname', 'groupname'),('org2name', 'group2name')])

        # Clear test
        self.cache.clear_organization_groups(234567)
        self.assertEquals(self.cache.get_organization_groups(234567), None)


class AuthenticationCacheTestCase(CQDETestCase):
    def setUp(self):
        self.cache = AuthenticationCache.instance()

    def tearDown(self):
        pass

    def testAutheticationSetGetClear(self):
        self.cache.clearAuthentication('testijuuser', 'FAK3SHA1')

        self.assertEquals(self.cache.getAuthentication('testijuuser', 'FAK3SHA1'), None)

        self.cache.setAuthentication('testijuuser', 'FAK3SHA1', True)
        self.assertEquals(self.cache.getAuthentication('testijuuser', 'FAK3SHA1'), True)

        self.cache.clearAuthentication('testijuuser', 'FAK3SHA1')
        self.assertEquals(self.cache.getAuthentication('testijuuser', 'FAK3SHA1'), None)

        self.cache.setAuthentication('testijuuser', 'FAK3SHA1', False)
        self.assertEquals(self.cache.getAuthentication('testijuuser', 'FAK3SHA1'), False)

        self.cache.clearAuthentication('testijuuser', 'FAK3SHA1')
        self.assertEquals(self.cache.getAuthentication('testijuuser', 'FAK3SHA1'), None)
