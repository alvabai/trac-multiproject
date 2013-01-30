# -*- coding: utf-8 -*-

class ArgumentsStub(object):
    getparam = ""
    def setGetParam(self, val):
        self.getparam = val
    def get(self, val):
        if self.getparam == "searchprojects" and val == "searchprojects":
            return True
        elif self.getparam == "searchprojects" and val == "pattern":
            return "project"
        elif self.getparam == "update" and val == "update":
            return True
        elif self.getparam == "update" and val == "projects":
            project_data = [[3,
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
                             "12"],
                            [4,
                             "Project4",
                             None,
                             None,
                             "4",
                             None,
                             None,
                             None,
                             None,
                             None,
                             None,
                             "15"],
                            [5,
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
            ]
            return project_data
        elif isinstance(val, list):
            return "1"

class PermissionStub(object):
    def require(self, val):
        if val == "TRAC_ADMIN":
            return True
        else:
            return False


class ReqMock(object):
    method = ""
    args = ArgumentsStub()
    perm = PermissionStub()
    def __init__(self, val):
        self.method = val