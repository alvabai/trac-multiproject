# -*- coding: utf-8 -*-
"""
Module for user organizations, which are tied to authentication backends.
Component uses following configuration keys::

    [multiproject-users]
    use_organizations = true
    # org.<type>.<position> = <backend|domain>,<orgname>
    org.auth.1 = LDAP,LDAP users
    org.auth.2 = LocalDB,Local users
    org.email.3 = @gmail.com,Gmail

Where prefix ``org`` is used for defining organizations where new users are put it.
Users can be put into organizations based on authentication backend and/or email domain.
In many cases, user can match with both.
"""
import logging

from trac.admin import IAdminCommandProvider
from trac.config import BoolOption, Section
from trac.core import Component, implements
from trac.util.text import printout

from multiproject.core.configuration import MultiListOption
from multiproject.core.db import safe_string, safe_int, admin_transaction


class OrganizationManager(Component):
    """
    Main class for managing organizations as Trac component

    Config:

        org.<type>.<identifier> = <backend>, <organization>

    """
    prefix = 'org'
    section = 'multiproject-users'
    use_organizations = BoolOption(section, 'use_organizations', False, 'Put users into organizations based on auth backend')
    organizations = MultiListOption(section, prefix, 'LocalDB,Local users', 'Organizations, on entry per line with numeric prefix')

    def get_organizations_by_backend(self, backend):
        """
        Returns organization info based on backend name
        :param str backend: Backend name
        :return: List of matching organizations if match was found, otherwise empty
        """
        return [org for org in self.get_organizations() if org['backend'] == backend]

    def get_organizations(self):
        """
        Returns configured organizations in dict format.
        Example:

        Configuration::

            [multiproject-users]
            org.auth.1 = LocalDB,My local users
            org.auth.2 = LDAP,My LDAP users
            org.email.3 = @gmail.com,Gmail users

        Output::

            [
                {'position': 1, 'type': 'auth', 'backend': 'LocalDB', 'name': 'My local users'},
                {'position': 2, 'type': 'auth', 'backend': 'LDAP', 'name': 'My LDAP users'},
                {'position': 3, 'type': 'email', 'backend': '@gmail.com', 'name': 'Gmail users'},
            ]

        :return: Organizations in a list
        """
        orgs = []

        for org_option in MultiListOption.get_options(Section(self.config, self.section), self.prefix):
            try:
                prefix, otype, identifier = org_option.name.split('.', 2)
                backend, name = self.config.getlist(org_option.section, org_option.name)
                orgs.append({
                    'position': int(identifier),
                    'type': otype,
                    'backend': backend,
                    'name': name,
                })
            except ValueError:
                self.log.error('Invalid configuration key or value: [%s] %s' % (org_option.section, org_option.name))

        return orgs


class OrganizationAdminCommand(Component):
    implements(IAdminCommandProvider)

    # IAdminCommandProvider methods

    def get_admin_commands(self):
        yield ('mp user update org', '',
               'Update organization info from config to db',
               None, self._do_org_update)

    def _do_org_update(self):
        """
        Updates organizations from project.ini to database
        Organizations are in format::

            org.<type>.<identifier> = <backend>, <organization>

        Where:

        - type: Organization type: auths | email
        - identifier: Identifier for organization. Id for auths and mail domain for email
        - backend: Authentication backend
        - organization: Organization name

        """
        orgman = self.env[OrganizationManager]
        organizations = orgman.get_organizations()

        if not orgman.use_organizations:
            printout('Organizations are disabled. Nothing to do.')
            return

        if not organizations:
            printout('No organizations were found from configuration. Nothing to do.')
            return

        # Surround organizations with '
        organizations_sql = []
        for organization in sorted(organizations, key=lambda org: org['position']):
            organizations_sql.append("('{0}', {1})".format(safe_string(organization['name']), safe_int(organization['position'])))

        query = """
        INSERT IGNORE INTO organization (organization_name, sorting)
        VALUES {0}
        ON DUPLICATE KEY UPDATE sorting=VALUES(sorting)
        """.format(','.join(organizations_sql))

        with admin_transaction() as cursor:
            try:
                cursor.execute(query)
            except:
                logging.exception("Organization update failed (conf -> db) with query %s" % query)
                printout('Failed to update organization info. Check the logs')
                return

        printout('Updated organization info into db successfully')
