# -*- coding: utf-8 -*-
"""
Module contains the components for the profiles views
"""
import re
from pkg_resources import resource_filename

from trac.core import Component, implements, TracError
from trac.web import IRequestHandler
from trac.web.chrome import ITemplateProvider
from trac.util.datefmt import to_datetime

from multiproject.common.projects import Project
from multiproject.common.projects.projects import Projects
from multiproject.core.permissions import CQDEPermissionPolicy
from multiproject.core.watchlist import CQDEWatchlistStore
from multiproject.home.watchlist.watchlist_events import WatchlistEvents
from multiproject.core.configuration import conf
from multiproject.core.users import get_userstore
from multiproject.core.util import to_web_time
from multiproject.core.db import trac_db_query, safe_string


RE_HOME_USER = re.compile(r'^/user/[a-zA-Z0-9.@_ ]*$')

# TODO: Separate the code+template between own profile and other profile

class MyProjectsModule(Component):
    """ Trac component for showing welcome screen for user with most relevant
        user content in it.

        Should be used on home project only.
    """
    implements(ITemplateProvider, IRequestHandler)

    # IRequestHandler methods
    def match_request(self, req):
        """
        Match /myprojects path to this page
        """
        if req.path_info.startswith('/myprojects'):
            return True

        return bool(RE_HOME_USER.match(req.path_info))

    def process_request(self, req):
        """
        Render welcome page
        """
        # Cast into bool directly, since match object properties are not needed
        viewing_user_profile = bool(RE_HOME_USER.match(req.path_info))
        userstore = get_userstore()

        if (req.authname == 'anonymous'
            and not self.env.config.getbool('multiproject', 'allow_public_projects')):
            conf.redirect(req, req.href('/user'))

        if viewing_user_profile:
            username = req.path_info.rsplit("/")[-1]
        else:
            username = req.authname

        user = userstore.getUser(username)
        if not user:
            raise TracError("User not found.")

        if req.authname == 'anonymous' and not viewing_user_profile:
            conf.redirect(req, conf.url_home_path + '/user')

        if user.username == 'anonymous' or user.username == 'authenticated':
            raise TracError("User not found.")

        # Possible values
        sort_cols = {'DATE': 5, 'PRIORITY': 6, 'PROJECT': 7}
        desc_asc = {'DESC': True, 'ASC': False}

        sort_tasks_by = req.args.get('sort_tasks_by','DATE')
        if sort_tasks_by not in sort_cols:
            sort_tasks_by = 'DATE'
        sort_col = sort_cols[sort_tasks_by]

        sort_options = {'DESC':'DESC', 'ASC':'ASC'}
        sort_tasks_order = sort_options.get(req.args.get('sort_tasks_order'), 'ASC')


        data = {}
        data['username'] = user.getDisplayName()
        if viewing_user_profile:
            if username != req.authname:
                # TODO: i18n support
                data['usernames'] = username + "'s"
            else:
                data['usernames'] = "Your"
        else:
            data['username'] = "{0} {1}".format(user.givenName, user.lastName)
            data['usernames'] = "My"

        data['baseurl'] = conf.url_projects_path
        data['userpage'] = viewing_user_profile
        data['base_path'] = req.base_path

        # Prepare data for template
        prjs = Projects()

        default_projects, default_names = prjs.get_default_projects()
        data['default_projects'] = default_projects
        try:
            if viewing_user_profile:
                projects = prjs.get_participated_projects(user, by_ldap=False, public_only=True)
            else:
                projects = prjs.get_participated_projects(user, by_ldap=True, public_only=False)
        except TracError as e:
            projects = []

        if viewing_user_profile:
            all_projects = projects
        else:
            all_projects = default_projects + [p for p in projects if p.env_name not in default_names]

        admin_projects = []
        other_projects = []

        if viewing_user_profile:
            other_projects = all_projects
        else:
            for project in all_projects:
                if project.is_admin(user.username):
                    admin_projects.append(project)
                else:
                    other_projects.append(project)

        # admin_projects is [] in public profile or if there are not public, administrated projects
        data['projects_where_admin'] = admin_projects
        data['projects'] = other_projects

        # Get tickets and posts
        # [project, row[URL], row[SUMMARY], row[DESCRIPTION], row[PRIORITY], to_datetime(row[TIME]/1000000)]
        policy = CQDEPermissionPolicy(self.env)
        ticket_projects = []
        post_projects = []
        if viewing_user_profile:
            for project in all_projects:
                self.log.warning('project %s' % project.env_name)
                if policy.check_permission(project.trac_environment_key, 'TICKET_VIEW', 'anonymous'):
                    ticket_projects.append(project)
                if policy.check_permission(project.trac_environment_key, 'DISCUSSION_VIEW', 'anonymous'):
                    post_projects.append(project)
        else:
            ticket_projects = all_projects
            post_projects = all_projects

        tasks = prjs.get_all_user_tasks(user.username, ticket_projects)

        do_reverse = desc_asc[sort_tasks_order]
        tasks = sorted(tasks, key = lambda task: task[sort_col], reverse = do_reverse)

        # Get posts
        posts = self._get_posts(user.username, post_projects)

        data['tasks'] = tasks

        (totaltickets, totalclosed) = prjs.get_all_user_task_sums(user.username, all_projects)

        data['user'] = user
        data['known_priorities'] = ['blocker', 'critical', 'major', 'minor', 'trivial']
        data['sort_tasks_by'] = sort_tasks_by
        data['sort_tasks_order'] = sort_tasks_order
        data['posts'] = posts[:10]
        data['userpage'] = viewing_user_profile
        data['to_web_time'] = to_web_time

        # Check if user can create a project
        data['can_create_project'] = user.can_create_project()

        if viewing_user_profile:
            if username != req.authname:
                data['title'] = username + "'s profile"
                data['badgelinktitle'] = "View profile"
            else:
                data['title'] = "This is your public profile"
                data['badgelinktitle'] = "View your profile"
        else:
            data['title'] = "My projects"
            data['badgelinktitle'] = "View my public profile"

        topics_started = 0
        for post in posts:
            if post['topic_id'] == 0:
                topics_started += 1

        data['user'].details = {'Total tickets':totaltickets,
                                'Total tickets closed':totalclosed,
                                'Discussions started': topics_started}
        if not viewing_user_profile:
            data['watchlist'] = self._get_watchlist_events(user)

        return "myprojects.html", data, None

    # ITemplateProvider methods
    def get_templates_dirs(self):
        return [resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        return []

    def _get_watchlist_events(self, user):
        watchlist = CQDEWatchlistStore().get_projects_by_user(user.id)
        events = []
        event_helper = WatchlistEvents(self.env)

        # TODO: inefficient querying
        for watch in watchlist:
            project = Project.get(id=watch.project_id)
            project_events = event_helper.get_project_events(project, days = 7, minutes = 0)
            # filter eventlist by user's permissions
            project_events = event_helper.filter_events(project_events, user, project)
            if project_events:
                # show only one event per project
                events.append(project_events[0])

        events.sort(lambda x, y: cmp(y[1]['date'], x[1]['date']))
        return events

    def _get_posts(self, user, projects):
        #project_name, subject, body, createtime
        """ Get posts
        """
        posts = []
        query = None

        with trac_db_query(self.env) as cursor:
            for prj in projects:
                query = ("SELECT id, forum, 0, time, subject, body FROM `%(dbname)s`.`topic` "
                         "WHERE author = '%(user)s' "
                         "UNION ALL "
                         "SELECT m.id, m.forum, m.topic, m.time, t.subject, m.body FROM "
                         "`%(dbname)s`.`message` m, `%(dbname)s`.`topic` t "
                         "WHERE m.author = '%(user)s' AND m.topic = t.id" %
                         {'dbname': safe_string(prj.env_name),
                          'user': safe_string(user)})

                try:
                    cursor.execute(query)
                    for row in cursor:
                        posts.append({
                            'project': prj,
                            'id': row[0],
                            'forum_id': row[1],
                            'topic_id': row[2],
                            'time': to_datetime(row[3]),
                            'subject': unicode((row[4] != '') and row[4] or '<no subject>'),
                            'body': unicode(row[5]),
                            'type': (row[2] == 0) and 'NEWTOPIC' or 'POST'
                        })
                except:
                    self.log.exception(
                        "MyProjectsModule._get_posts query failed for project %s with query: '''%s'''" %
                        (prj.env_name, query))

        import operator
        posts.sort(key = operator.itemgetter('time'), reverse = True)

        return posts
