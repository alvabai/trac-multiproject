# -*- coding: utf-8 -*-


import math

from projectTest import *

from core.dbTest import *

class ProjectsStub(object):

    @staticmethod
    def sqlToProject(project_data, parent_data=None):
        author = None
        parent = None

        if parent_data:
            parent = ProjectsStub.sqlToProject(parent_data)

        prj = ProjectStub(
            id=project_data[0],
            project_name=project_data[1],
            env_name=project_data[2],
            description=project_data[3],
            author_id=project_data[4],
            created=project_data[5],
            updated=project_data[6],
            published=project_data[7],
            parent_id=project_data[8],
            icon_name=project_data[9],
            trac_environment_key=project_data[10],
            priority=project_data[11]
        )

        return prj

    def get_featured_projects(self, limit=None, count=None):
        """ List all featured projects
        """
        query = ("SELECT projects.*, project_selected.value AS priority FROM project_selected "
                 "INNER JOIN projects ON  project_selected.project_id = projects.project_id "
                 "ORDER BY priority ")

        if limit:
            if count:
                query += "LIMIT %d,%d" % (safe_int(limit), safe_int(count))
            else:
                query += "LIMIT %d" % safe_int(limit)

        projects = self.queryProjectObjects(query)
        return projects

    def queryProjectObjects(self, project_query):
        projects = []
        if project_query == ("SELECT projects.*, project_selected.value AS priority FROM project_selected "
                             "INNER JOIN projects ON  project_selected.project_id = projects.project_id "
                             "ORDER BY priority ") and admin_query():
            project_data = [1,
                            "Project1",
                            None,
                            None,
                            "4",
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            "12"]
            projects.append(ProjectsStub.sqlToProject(project_data))
            project_data = [2,
                            "Home",
                            None,
                            None,
                            "4",
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            "12"]
            projects.append(ProjectsStub.sqlToProject(project_data))
        elif project_query == (("SELECT projects.*, project_selected.value AS priority FROM project_selected "
                               "INNER JOIN projects ON  project_selected.project_id = projects.project_id "
                               "ORDER BY priority ")+"LIMIT 4") and admin_query():
            project_data = [3,
                            "Project3",
                            None,
                            None,
                            "4",
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            "12"]
            projects.append(ProjectsStub.sqlToProject(project_data))
            project_data = [4,
                            "Project5",
                            None,
                            None,
                            "4",
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            "12"]
            projects.append(ProjectsStub.sqlToProject(project_data))

        return projects

    def search_project(self, keywords, category_ids, sub_page=1, limit=5):
        if keywords == "project":
            return {"project_id": 1, "priority": None}
        else:
            return None