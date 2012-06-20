from multiproject.core.test.cqdetestcase import CQDETestCase
from multiproject.core.tests.ConfigurationStub import conf, userstoreStub
from multiproject.core.permissions import CQDEPermissionStore, CQDEUserGroupStore, CQDEOrganizationStore, \
    OrganizationEntity, CQDEPermissionPolicy, CQDEAuthenticationStore


class CQDEPermissionStoreTestCase(CQDETestCase):
    def setUp(self):
        conf.use_test_db(True)
        self.load_fixtures()
        conf.memcached_enabled = False

    def tearDown(self):
        conf.use_test_db(False)

    def test_get_user_permissions(self):
        store = CQDEPermissionStore(19)
        self.assertEquals(store.get_user_permissions('cartman'), ['MODIFY', 'CREATE'])
        self.assertEquals(store.get_user_permissions('kenny'), [])

        store = CQDEPermissionStore(24)
        self.assertEquals(store.get_user_permissions('kenny'), ['VERSION_CONTROL'])

    def test_get_users_with_permissions(self):
        store = CQDEPermissionStore(19)
        self.assertEquals(store.get_users_with_permissions(['MODIFY', 'CREATE']), ['cartman'])
        self.assertEquals(store.get_users_with_permissions(['TRAC_ADMIN']), ['tracadmin'])

    def test_get_all_permissions(self):
        store = CQDEPermissionStore(21)
        self.assertEquals(store.get_all_permissions(), [('cartman', 'VIEW'), ('tracadmin', 'TRAC_ADMIN')])

    def test_grant_permission(self):
        store = CQDEPermissionStore(21)
        self.assertRaises(Exception, store.grant_permission, 'testuser', 'TRAC_ADMIN')

    def test_revoke_permission(self):
        store = CQDEPermissionStore(21)
        self.assertRaises(Exception, store.revoke_permission, 'testuser', 'TRAC_ADMIN')

class CQDEUserGroupStoreTestCase(CQDETestCase):
    def setUp(self):
        conf.use_test_db(True)
        self.load_fixtures()
        conf.memcached_enabled = False

    def tearDown(self):
        conf.use_test_db(True)
        self.load_fixtures()
        s = CQDEUserGroupStore(19)
        s.remove_group('mytest')
        s.remove_group('mytest2')
        s.remove_group('tgroup')
        s.remove_group('ogroup')
        s.remove_group('addtestgroup')
        s.remove_group('newgroup')
        userstoreStub.reset()
        conf.use_test_db(False)
        conf.memcached_enabled = True

    def test_get_all_user_groups(self):
        s = CQDEUserGroupStore(19)
        usergroups = s.get_all_user_groups()
        self.assertIn(('cartman', 'testgroup'), usergroups)

    def test_get_all_organization_groups(self):
        s = CQDEUserGroupStore(19)
        org_groups = s.get_all_organization_groups()
        self.assertIn(('LDAP users', 'testgroup'), org_groups)

    def test_get_all_group_permissions(self):
        s = CQDEUserGroupStore(19)
        perm = s.get_all_group_permissions()
        self.assertIn(('testgroup', 'CREATE'), perm)
        self.assertIn(('testgroup', 'MODIFY'), perm)

    def test_create_and_remove_group(self):
        s = CQDEUserGroupStore(19)
        ok = s.create_group('mytest')
        self.assertTrue(ok)
        ok = s.create_group('mytest2')
        self.assertTrue(ok)
        groups = s.get_groups()
        self.assertIn('mytest', groups)
        self.assertIn('mytest2', groups)

        ok = s.remove_group('mytest')
        self.assertTrue(ok)
        groups = s.get_groups()
        self.assertNotIn('mytest', groups)
        self.assertIn('mytest2', groups)

        ok = s.remove_group('mytest2')
        self.assertTrue(ok)
        groups = s.get_groups()
        self.assertNotIn('mytest2', groups)

    def test_add_and_remove_user_from_group(self):
        userstoreStub.user.id = 32
        s = CQDEUserGroupStore(19)
        ok = s.add_user_to_group('cartman', 'addtestgroup')
        self.assertTrue(ok)
        usergroups = s.get_all_user_groups()
        self.assertIn(('cartman', 'addtestgroup'), usergroups)

        ok = s.remove_user_from_group('cartman', 'addtestgroup')
        self.assertTrue(ok)
        usergroups = s.get_all_user_groups()
        self.assertNotIn(('cartman', 'addtestgroup'), usergroups)

        ok = s.add_user_to_group('cartman', 'addtestgroup')
        self.assertTrue(ok)
        s.remove_group('addtestgroup')
        usergroups = s.get_all_user_groups()
        self.assertNotIn(('cartman', 'addtestgroup'), usergroups)

    def test_add_and_remove_organization_from_group(self):
        s = CQDEUserGroupStore(19)
        ok = s.add_organization_to_group('LDAP users', 'ogroup')
        self.assertTrue(ok)
        ok = s.add_organization_to_group('Local users', 'ogroup')
        self.assertTrue(ok)
        org_groups = s.get_all_organization_groups()
        self.assertIn(('LDAP users', 'ogroup'), org_groups)
        self.assertIn(('Local users', 'ogroup'), org_groups)

        ok = s.remove_organization_from_group('LDAP users', 'ogroup')
        org_groups = s.get_all_organization_groups()
        self.assertNotIn(('LDAP users', 'ogroup'), org_groups)
        self.assertIn(('Local users', 'ogroup'), org_groups)

        s.remove_group('ogroup')
        org_groups = s.get_all_organization_groups()
        self.assertNotIn(('Local users', 'ogroup'), org_groups)

    def test_grant_and_revoke_permission_from_group(self):
        s = CQDEUserGroupStore(19)
        success = s.grant_permission_to_group('newgroup', 'TRAC_ADMIN')
        self.assertTrue(success)
        success = s.grant_permission_to_group('newgroup', 'VIEW')
        self.assertTrue(success)
        perm = s.get_all_group_permissions()
        self.assertIn(('newgroup', 'TRAC_ADMIN'), perm)
        self.assertIn(('newgroup', 'VIEW'), perm)

        success = s.revoke_permission_from_group('newgroup', 'TRAC_ADMIN')
        self.assertTrue(success)
        perm = s.get_all_group_permissions()
        self.assertNotIn(('newgroup', 'TRAC_ADMIN'), perm)
        self.assertIn(('newgroup', 'VIEW'), perm)

        s.remove_group('newgroup')
        perm = s.get_all_group_permissions()
        self.assertNotIn(('newgroup', 'VIEW'), perm)

    def test_get_group_id(self):
        s = CQDEUserGroupStore(19)
        gid = s.get_group_id('testgroup')
        self.assertEquals(gid, 131078)


class CQDEOrganizationStoreTestCase(CQDETestCase):
    def setUp(self):
        conf.use_test_db(True)
        self.load_fixtures()
        conf.memcached_enabled = False

    def tearDown(self):
        conf.use_test_db(False)

    def test_get_organizations(self):
        """ Should return all organizations.
        """
        s = CQDEOrganizationStore.instance()
        org = s.get_organizations()
        names = [x.name for x in org]
        self.assertIn('Local users', names)
        self.assertIn('LDAP users', names)

    def test_store_and_remove_organization(self):
        """ Should store and remove organizations.
        """
        organization = OrganizationEntity()
        organization.name = "Test organization to be removed"
        organization.sorting = 1

        org_store = CQDEOrganizationStore.instance()
        success = org_store.store_organization(organization)
        self.assertTrue(success)
        organization.id = org_store.get_organization_id(organization.name)

        self.assertNotEquals(organization.id, None)

        all_organizations = org_store.get_organizations()

        same_organization = None
        for org in all_organizations:
            if org.name == organization.name:
                same_organization = org
        self.assertEquals(same_organization.name, organization.name)
        self.assertEquals(same_organization.id, organization.id)

        # Remove organization
        org_store.remove_organization(organization.name)
        self.assertEquals(org_store.get_organization_id(organization.name), None)

    def test_get_organization_id(self):
        """ Should give a correct organization id.
        """
        s = CQDEOrganizationStore.instance()
        oid = s.get_organization_id('LDAP users')
        self.assertEquals(oid, 2)

class CQDEAuthenticationStoreTestCase(CQDETestCase):
    def setUp(self):
        conf.use_test_db(True)
        self.load_fixtures()
        conf.memcached_enabled = False

    def tearDown(self):
        conf.use_test_db(False)

    def test_get_authentications(self):
        """ Should return all authentication methods.
        """
        store = CQDEAuthenticationStore.instance()
        methods = store.get_authentications()
        method_names = [x.name for x in methods]
        should_have = ['LDAP', 'LocalDB']
        for name in should_have:
            self.assertIn(name, method_names)

class CQDEPermissionPolicyTestCase(CQDETestCase):
    def setUp(self):
        conf.use_test_db(True)
        self.load_fixtures()
        conf.memcached_enabled = False

    def tearDown(self):
        conf.use_test_db(False)

    def test_get_granting_permissions(self):
        """ Granting actions should give all actions that grants requested action.
        """
        policy = CQDEPermissionPolicy()
        actions = policy.get_granting_permissions('WIKI_VIEW')
        self.assertIn('VIEW', actions)
        self.assertIn('MODIFY', actions)
        self.assertIn('CREATE', actions)
        self.assertIn('TRAC_ADMIN', actions)

        actions = policy.get_granting_permissions('CREATE')
        self.assertNotIn('VIEW', actions)
        self.assertNotIn('WIKI_VIEW', actions)
        self.assertIn('TRAC_ADMIN', actions)

    def test_check_permission(self):
        """ Check permission should return true when having permission.
        """
        policy = CQDEPermissionPolicy()
        self.assertTrue(policy.check_permission(19, 'MODIFY', 'cartman'))
        self.assertTrue(policy.check_permission(19, 'VIEW', 'cartman'))
        self.assertFalse(policy.check_permission(19, 'TRAC_ADMIN', 'cartman'))
        self.assertTrue(policy.check_permission(24, 'VERSION_CONTROL_VIEW', 'kenny'))
        self.assertTrue(policy.check_permission(24, 'VERSION_CONTROL', 'kenny'))
        self.assertFalse(policy.check_permission(24, 'VERSION_CONTROL', 'cartman'))
        self.assertTrue(policy.check_permission(22, 'TRAC_ADMIN', 'testuser'))
        self.assertTrue(policy.check_permission(22, 'VIEW', 'testuser'))

    def test_get_special_users(self):
        """ Should give special users correctly.
        """
        policy = CQDEPermissionPolicy()
        self.assertEquals(policy.get_special_users('somousername'), ['anonymous', 'authenticated'])
        self.assertEquals(policy.get_special_users('anonymous'), ['anonymous'])
        self.assertEquals(policy.get_special_users('authenticated'), ['anonymous', 'authenticated'])
