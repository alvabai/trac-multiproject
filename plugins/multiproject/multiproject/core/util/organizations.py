# -*- coding: utf-8 -*-
from multiproject.core.db import admin_transaction, safe_string, safe_int

class OrganizationUpdater(object):
    @staticmethod
    def update_to_db(conf):
        """
        Update organizations from project.ini to database
        """
        orgdict = {}
        for authname in conf.organizations.keys():
            pos, type, organization = conf.organizations[authname]
            orgdict[pos] = organization

        # Surround organizations with '
        organizations_wrapped = []
        checklist = []
        for position in sorted(orgdict.keys()):
            organization = orgdict[position]
            if organization not in checklist:
                organizations_wrapped.append("('{0}', {1})".format(safe_string(organization), safe_int(position)))
                checklist.append(organization)
        organizations_str = ','.join(organizations_wrapped)

        query = """
        INSERT IGNORE INTO organization (organization_name,sorting)
        VALUES {0}
        ON DUPLICATE KEY UPDATE sorting=VALUES(sorting)
        """.format(organizations_str)

        with admin_transaction() as cursor:
            try:
                cursor.execute(query)
            except:
                conf.log.exception("Organization update failed (conf -> db) with query %s" % query)
                return False

        return True
