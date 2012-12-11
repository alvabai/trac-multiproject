# -*- coding: utf-8 -*-
"""
.. py:module:: scripts.cron.generate_user_visibility

This module populates the `project_user_visibility` table of trac admin db.
This table is used currently only when searching for projects in explore view
(see note).

If in project X, anonymous user has 'PROJECT_VIEW' permission, the table
`project_user_visibility` will have ([project X id], [anon user id]) row inserted.
Else, if in project X, user A has 'PROJECT_VIEW', the table `project_user_visibility`
will have row ([project X id], [user A id]) inserted.

This means that if the user A has visibility to the project X, there is either
line ([project X id], [user A id]) or ([project X id], [anon user id]) after
this script has been run but not both, which gives optimization possibility in
the explore projects query.

No row for 'authenticated' users are generated currently, since they are not used currently.

In the beginning, the table is erased from previous data in
:py:meth:`.ProjectUserVisibilityGenerator.clear_visibilities` method.

Usually, this script is run with the following kind of crontab command::

 # explore project visibility generating
 0 6,18 * * * source /etc/trac/env.sh; \
    nice python /path/to/scripts/generate_project_user_visibility.py 2>&1 > /path/to/log_file.log

.. Note:

The usual usage means that there is a small possibility that the data
is inconsistent for some period of time before the next update,
when the anonymous user is added to or removed from some group of a project.
Thus, the project_user_visibility usage should be cautious.
However, since the projects will become public rather than private, this is ok.

Currently, when the :py:class:`multiproject.project.admin.basics.BasicsAdminPanelInterceptor`
handles request to set project public or private, updating project_user_visibility table
is handled by calling :py:meth:`multiproject.common.projects.api.Projects.add_public_project_visibility`
and :py:meth:`multiproject.common.projects.api.Projects.remove_public_project_visibility` methods.

"""
import sys
from time import time

from multiproject.common.projects import Projects
from multiproject.core.configuration import conf
from multiproject.core.permissions import CQDEPermissionPolicy, get_permission_id
from multiproject.core.db import admin_query, admin_transaction, safe_int
from multiproject.core.users import get_userstore
from multiproject.core.util.mockenv import MockEnvironment


class ProjectUserVisibilityGenerator():
    def __init__(self, verbose=False):
        """
        If verbose = None, be absolutely quiet
        """
        self.verbose = verbose
        self.policy = CQDEPermissionPolicy(MockEnvironment())
        self.papi = Projects()
        self.batch_size = conf.visibility_db_batch_size
        self.required_permission = 'PROJECT_VIEW'

    def get_anonymous_user_id(self):
        anon = get_userstore().getUser('anonymous')
        if anon:
            anon_id = safe_int(anon.id)
        else:
            anon_id = None

        return anon_id

    def get_public_project_pairs(self, anon_id):
        """
        :param anon_id: Anonymous user_id
        :return: List of tuples (project_id, trac_environment_key)
        """
        # TODO: it's not clearly defined when project is public
        perms = ['PROJECT_VIEW', 'TRAC_ADMIN']
        perm_ids = [get_permission_id(perm) for perm in perms]

        query = """SELECT DISTINCT p.project_id, p.trac_environment_key
                          FROM projects p
                    INNER JOIN `group` g ON g.trac_environment_key = p.trac_environment_key
                    INNER JOIN user_group ON user_group.group_key = g.group_id
                    INNER JOIN group_permission ON group_permission.group_key = g.group_id
                         WHERE user_group.user_key = {0}
                           AND group_permission.permission_key IN ({1})
                          """.format(anon_id, ', '.join([str(int(id)) for id in perm_ids]))

        id_pairs = []
        with admin_query() as cursor:
            try:
                cursor.execute(query)
                for row in cursor:
                    id_pair = (int(row[0]), int(row[1]))
                    id_pairs.append(id_pair)
            except Exception as e:
                if self.verbose is not None:
                    print "Exception. In method get_public_project_pairs, the following query failed."
                    print query
                    print e
                conf.log.exception("Exception. ProjectUserVisibilityGenerator.get_public_project_pairs "
                                   "failed with query '''%s'''." % query)

        return id_pairs

    def get_private_project_pairs(self, public_id_pairs = None):
        query = "SELECT project_id, trac_environment_key FROM projects "

        if public_id_pairs:
            public_project_ids = [pair[0] for pair in public_id_pairs]
            # TODO: What if there are really many public projects?
            pub_projs = ','.join(str(id) for id in public_project_ids)
            query += "WHERE projects.project_id NOT IN (%s)" % pub_projs

        id_pairs = []
        with admin_query() as cursor:
            try:
                cursor.execute(query)
                for row in cursor:
                    id_pair = (int(row[0]), int(row[1]))
                    id_pairs.append(id_pair)
            except Exception as e:
                if self.verbose is not None:
                    print "Exception. In method get_private_project_pairs, the following query failed."
                    print query
                    print e
                conf.log.exception("Exception. ProjectUserVisibilityGenerator.get_private_project_pairs failed "
                                   "with query '''%s'''." % query)

        return id_pairs

    def get_all_users(self, except_anon=True):
        """
        Returns :py:class:`User` objects for every user except 'authenticated' and, if
        anon_id is given, 'anonymous'.

        No row for 'authenticated' users are generated currently, this is why the 'authenticated'
        user is left out.

        :param bool except_anon: when True, don't include anon user
        :returns: A list of :py:class:`User` objects
        """
        if except_anon:
            query = """SELECT user_id, username FROM `user`
                        WHERE username NOT IN ('anonymous', 'authenticated') """
        else:
            query = """SELECT user_id, username FROM `user`
                        WHERE username NOT IN ('authenticated') """

        users = []
        with admin_query() as cursor:
            try:
                cursor.execute(query)
                for row in cursor:
                    user = User.from_sql_row(row)
                    users.append(user)
            except Exception as e:
                if self.verbose is not None:
                    print "Exception. In method get_all_users, the following query failed."
                    print query
                    print e
                conf.log.exception("Exception. ProjectUserVisibilityGenerator.get_all_users failed "
                                   "with query '''%s'''." % query)

        return users

    def user_can_view_project(self, trac_environment_key, username):
        return self.policy.check_permission(trac_environment_key, self.required_permission, username)

    def clear_project_visibilities(self, project_id):
        query = "DELETE FROM project_user_visibility where project_id = %s"

        with admin_transaction() as cursor:
            try:
                cursor.execute(query, project_id)
            except Exception as e:
                if self.verbose is not None:
                    print "Exception. In method clear_visibilities, the following query failed."
                    print query
                    print e
                conf.log.exception("Exception. ProjectUserVisibilityGenerator.clear_visibilities "
                                   "failed with query '''%s'''." % query)

    def batch_insert(self, visibilities):
        query = "INSERT INTO project_user_visibility (project_id, user_id) VALUES "

        for visibility in visibilities:
            query += ",".join(["(%d,%d)" % (safe_int(visibility.project_id),
                                            safe_int(visibility.user_id))])

        with admin_transaction() as cursor:
            try:
                cursor.execute(query)
            except Exception as e:
                if self.verbose is not None:
                    print "Exception. In method batch_insert, the following query failed."
                    print query
                    print e
                conf.log.exception("Exception. ProjectUserVisibilityGenerator.batch_insert '''%s'''." % query)

    def flush_buffer(self):
        if len(self.buffer) > 0:
            self.batch_insert(self.buffer)
            self.buffer = []

    def insert_visibilities(self, buffer):
        project_visibilities = []
        project_id = buffer[0].project_id
        for visibility in buffer:
            if project_id == visibility.project_id:
                project_visibilities.append(visibility)
            else:
                self.clear_project_visibilities(project_visibilities[0].project_id)
                self.buffered_insert(project_visibilities)
                project_visibilities = [visibility]
                project_id = visibility.project_id

        if project_visibilities:
            self.clear_project_visibilities(project_visibilities[0].project_id)
            self.buffered_insert(project_visibilities)

    def buffered_insert(self, buffer):
        while len(buffer) >= self.batch_size:
            self.batch_insert(buffer[:self.batch_size])
            buffer = buffer[self.batch_size:]

        if len(buffer) > 0:
            self.batch_insert(buffer)

    def pct_str(self, figure, total):
        if total == 0:
            return "NaN"

        percentage = 100.0 * float(figure) / float(total)
        return str(round(percentage, 1)) + "%"

    def generate_list(self, users, anon_id, pub_project_pairs, priv_project_pairs):
        """
        See the module documentation.

        :param pub_project_pairs: (project id, trac environment key) pairs of the projects which anon user can see
        :param priv_project_pairs: (project id, trac environment key) pairs of other than public projects
        :param users: A list of :py:class:`User` objects
        :returns: A list of table ProjectUserVisibility objects for (project_id, user_id)
        """
        # TODO: Horribly slow way to implement, optimize!
        # For each user, search ldap groups and organization where the
        # user belongs. For each project, search every group having the
        # required permission, and obtain the single user, ldap group or
        # organization members of those groups. Add a cache-awareness
        # into CQDEPermissionStore.check_permission() method (for example,
        # allow passing groups, organization_members and ldap_groups).
        if self.verbose:
            print "using cnc/pfnc rules to generate the visibility list"
        iter = 0
        target = len(users) * len(priv_project_pairs)
        percent = int(target / 100)
        if percent == 0:
            percent = 1
        big_list = []
        if pub_project_pairs:
            for proj_id, trac_environment_key in pub_project_pairs:
                big_list.append(ProjectUserVisibility(proj_id, anon_id))

        trues = len(pub_project_pairs or [])
        falses = 0
        last = time()
        for proj_id, trac_environment_key in priv_project_pairs:
            for user in users:
                iter += 1
                if self.user_can_view_project(trac_environment_key, user.username):
                    trues += 1
                    big_list.append(ProjectUserVisibility(proj_id, user.user_id))
                else:
                    falses += 1
                if self.verbose and iter % percent == 0:
                    print "progress:", ((100 * iter) / target + 1) , "%, delta time for", percent, "iterations: ", (time() - last), " seconds"
                    last = time()

        return big_list, trues, falses


class User():
    def __init__(self):
        self.user_id = None
        self.username = None

    @staticmethod
    def from_sql_row(row):
        user = User()
        user.user_id = int(row[0])
        user.username = row[1]
        return user

    def __repr__(self):
        return "<User:" + str(self.user_id) + ":" + str(self.username) + ">"


class ProjectUserVisibility():
    def __init__(self, project_id, user_id):
        self.project_id = project_id
        self.user_id = user_id

    def __repr__(self):
        return "<ProjectUserVisibility:" + str(self.project_id) + ":" + str(self.user_id) + ">"


def main():
    verbose = False
    quiet = False
    if len(sys.argv) > 1:
        if '-h' in sys.argv or '--help' in sys.argv:
            print "usage: python generate_project_user_visibility.py [-v] [-q]"
            print "       -q     quiet mode, don't print anything"
            print "       -v     print verbose output"
            return
        if '-v' in sys.argv or '--verbose' in sys.argv:
            verbose = True
        if '-q' in sys.argv or '--quiet' in sys.argv:
            quiet = True
            verbose = None

    start = time()
    generator = ProjectUserVisibilityGenerator(verbose)

    anon_id = generator.get_anonymous_user_id()
    pub_project_pairs = None
    if anon_id:
        pub_project_pairs = generator.get_public_project_pairs(anon_id)
    elif not quiet:
        print "Warning: anonymous user id not found!"
    # users don't contain 'authenticated'
    # TODO: implement special handling for 'authenticated' user
    # - split all projects for three disjoint lists:
    #   viewable by anonymous, viewable by authenticated (but not anonymous) and other projects
    # - Implement
    users = generator.get_all_users(except_anon = True)
    priv_project_pairs = generator.get_private_project_pairs(pub_project_pairs)

    user_count = len(users)
    pub_count = (len(pub_project_pairs or []))
    priv_count = len(priv_project_pairs)
    total_count = pub_count + priv_count
    total = user_count * total_count
    target = user_count * priv_count

    visibilities, trues, falses = generator.generate_list(users, anon_id, pub_project_pairs, priv_project_pairs)

    last = time()
    if verbose:
        print "DB inserting started"
    generator.insert_visibilities(visibilities)
    if verbose:
        print "DB inserting completed, took ", (time() - last), "seconds"
        print "---- statistics ----"
        print "users                     :", user_count
        print "public projects           :", pub_count, "( %s )" % generator.pct_str(pub_count, total_count)
        print "private projects          :", priv_count, "( %s )" % generator.pct_str(priv_count, total_count)
        print "---- iterations ----"
        print "iterations needed         :", target, "( %s )" % generator.pct_str(target, (target + user_count * pub_count))
        print "iterations left out       :", user_count * pub_count, "( %s )" % generator.pct_str(user_count * pub_count, (target + user_count * pub_count))
        print "---- visibilities ----"
        print "public visibilities       :", pub_count, "( %s )" % generator.pct_str(pub_count, (trues + falses + pub_count))
        print "private visibilities      :", trues, "( %s )" % generator.pct_str(trues, (trues + falses + pub_count))
        print "private hides             :", falses, "( %s )" % generator.pct_str(falses, (trues + falses + pub_count))
    if not quiet:
        print "generating visibilities took total", (time() - start), "seconds"

if __name__ == '__main__':
    main()
